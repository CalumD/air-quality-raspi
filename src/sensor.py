#!/usr/bin/env python3
import json
import sys
import time
from datetime import datetime

import bme680
import psutil

import utils

_FIRST_TIME_RUN_TIME_MINS = 20
_CONFIG_FILE_NAME = 'sensor_config.json'
_DEFAULT_SENSOR_CONFIG = {
    "pressure_oversample": bme680.OS_4X,
    "temperature_oversample": bme680.OS_8X,
    "temperature_offset": 0.000,
    "cpu": {
        "rounding_factor": 0.7,
        "smoothing_strength": 10
    },
    "filter_size": bme680.FILTER_SIZE_7,
    "humidity": {
        "oversample": bme680.OS_2X,
        "baseline": 40.000,
        "quality_weighting": 0.250
    },
    "gas": {
        "heater_temperature": 320,
        "heater_duration": 150,
        "heater_profile": 0,
        "ambient_background": 0
    }
}


class Sensor:
    def __init__(self):
        # Configure
        if utils.validate_file_exists(_CONFIG_FILE_NAME):
            config = utils.get_json_from_file(_CONFIG_FILE_NAME)
        else:
            utils.validate_can_write_file(_CONFIG_FILE_NAME, should_del_after=True)
            self._configure_sensor(_DEFAULT_SENSOR_CONFIG)
            config = self.first_time_setup(_DEFAULT_SENSOR_CONFIG)
        self._configure_sensor(config)

        # Populate properties based on config
        self._data = utils.DataCapture()
        self.humidity_baseline = config['humidity']['baseline']
        self.humidity_gas_quality_ratio = config['humidity']['quality_weighting']
        self.gas_baseline = config['gas']['ambient_background']
        self.__cpu = config['cpu']
        self.__cpu['smoothing'] = []

    def first_time_setup(self, config):
        # Define burn-in variables
        total_burn_in_time = 60 * _FIRST_TIME_RUN_TIME_MINS  # == 1MinuteInSeconds * DefaultBurnInTime
        percent_complete_increment = total_burn_in_time / 10
        next_milestone_marker = 0
        percent_complete = 0
        burn_in_data = []

        # Let the user know what is about to happen
        print(f'Collecting sensor first-time-run \'burn-in\' data for {_FIRST_TIME_RUN_TIME_MINS} minutes.')
        print(f'Approximate completion time: '
              f'{datetime.fromtimestamp(time.time() + total_burn_in_time).strftime("%d/%m/%Y %H:%M")}:00')

        # Capture Data for pre-determined minutes
        start_time = time.time()
        current_time = time.time()
        while current_time - start_time < total_burn_in_time:
            # Decide if it's time for an update on progress.
            if current_time - start_time >= next_milestone_marker:
                print(f'Collecting Data... {percent_complete}% complete')
                next_milestone_marker += percent_complete_increment
                percent_complete = int((next_milestone_marker / total_burn_in_time) * 100)

            # Capture more sensor data.
            if self.sensor.get_sensor_data() and self.sensor.data.heat_stable:
                ambient_gas_reading = self.sensor.data.gas_resistance
                burn_in_data.append(ambient_gas_reading)
                utils.v_print('Gas: {0} Ohms'.format(ambient_gas_reading))
                # Rest for a second to save pounding the sensor / CPU unnecessarily.
                time.sleep(1)

            # Update the current time so while loop can progress.
            current_time = time.time()

        # Gather an average of the last 50 data points for smoothing and save as background readings.
        config['gas']['ambient_background'] = sum(burn_in_data[-50:]) / 50.0

        # Write data to config file.
        with open(_CONFIG_FILE_NAME, 'w') as json_file:
            json.dump(config, indent=4, fp=json_file)

        # return new data.
        return utils.get_json_from_file(_CONFIG_FILE_NAME)

    def _configure_sensor(self, config):
        # Set necessities
        self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        # Set Temp & Misc
        self.sensor.set_pressure_oversample(config['pressure_oversample'])
        self.sensor.set_temperature_oversample(config['temperature_oversample'])
        self.sensor.set_temp_offset(config['temperature_offset'])
        self.sensor.set_filter(config['filter_size'])
        # Humidity
        self.sensor.set_humidity_oversample(config['humidity']['oversample'])
        # Gas
        self.sensor.set_gas_heater_temperature(config['gas']['heater_temperature'])
        self.sensor.set_gas_heater_duration(config['gas']['heater_duration'])
        self.sensor.select_gas_heater_profile(config['gas']['heater_profile'])

    def read(self):
        # Update the time taken for the next readings.
        self._data.tick()

        # Wait until sensor is ready to be read from.
        while (not self.sensor.get_sensor_data()) or (not self.sensor.data.heat_stable):
            print(f'Sensor data not ready yet, waiting...', file=sys.stderr)
            time.sleep(1)

        # Capture 'simple' data.
        self._data.humidity = self.sensor.data.humidity
        self._data.pressure = self.sensor.data.pressure
        self._data.gas = self.sensor.data.gas_resistance

        # Capture current temperature - removing the CPU ambient temp
        self._data.temperature = self._calculate_temperature()

        # Capture Air Quality Score.
        self._data.iaq_index = self._calculate_iaq_index()

        # Return results to caller.
        return self._data

    def _calculate_iaq_index(self):
        humidity_offset = self._data.humidity - self.humidity_baseline
        gas_offset = self._data.gas - self.gas_baseline
        if humidity_offset > 0:
            hum_score = (100 - self.humidity_baseline - humidity_offset)
            hum_score /= (100 - self.humidity_baseline)
            hum_score *= (self.humidity_gas_quality_ratio * 100)
        else:
            hum_score = (self.humidity_baseline + humidity_offset)
            hum_score /= self.humidity_baseline
            hum_score *= (self.humidity_gas_quality_ratio * 100)

        if gas_offset > 0:
            gas_score = (self._data.gas / self.gas_baseline)
            gas_score *= (100 - (self.humidity_gas_quality_ratio * 100))
        else:
            gas_score = 100 - (self.humidity_gas_quality_ratio * 100)

        return hum_score + gas_score

    def _calculate_temperature(self):
        # Get the current cpu temperature and record it
        current_cpu_temp = psutil.sensors_temperatures()['cpu-thermal'][0][1]
        self.__cpu['smoothing'].append(current_cpu_temp)
        smoothing = self.__cpu['smoothing']

        # Roll the list on to the most recent values.
        if len(smoothing) > self.__cpu['smoothing_strength']:
            self.__cpu['smoothing'] = smoothing[1:]

        # Average the list of CPU temps
        recent_avg = sum(smoothing) / float(len(smoothing))
        snapshot = self.sensor.data.temperature

        # Offset the recorded value based on nearby CPU temps.
        return snapshot - ((recent_avg - snapshot) / self.__cpu['rounding_factor'])
