#!/usr/bin/env python3
import sys
import time

import bme680


class DataCapture:
    timestamp = time.time()

    def __init__(self, temperature=0.0, humidity=0.0, pressure=0.0, gas=0.0, iaq_index=0.0):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.gas = gas
        self.iaq_index = iaq_index

    def tick(self):
        self.timestamp = time.time()


class Sensor:
    def __init__(self):
        self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)
        self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

        # TODO: Config-file-ify the following 3 values.
        self.sensor.set_gas_heater_temperature(320)
        self.sensor.set_gas_heater_duration(150)
        self.sensor.select_gas_heater_profile(0)

        if not self.sensor_been_run_before():
            self.first_time_setup()

        self._config_data = self.get_config_data()
        self._data = DataCapture()

    def sensor_been_run_before(self):
        # TODO: Determine whether a config data file exists on disk already.
        return True

    def get_config_data(self):
        # TODO: implement reading the config data from the file and setting values in this class instance.
        return {}

    def first_time_setup(self):
        # TODO: Implement creating the config file on disk, then running for pre-determined amount of time to collect
        #  average gas resistance value.
        pass

    def read(self):
        # TODO: Improve this method to capture rolling averages effecting data output.
        #  Including CPU temps and gas changes/

        # Update the time taken for the next readings.
        self._data.tick()

        # Gather all readings.
        if self.sensor.get_sensor_data():
            self._data.temperature = self.sensor.data.temperature
            self._data.humidity = self.sensor.data.humidity
            self._data.pressure = self.sensor.data.pressure

            if self.sensor.data.heat_stable:
                self._data.gas = self.sensor.data.gas_resistance
            else:
                print('Gas reading was premature!', file=sys.stderr)
                self._data.gas = -1
        else:
            print('Sensor not ready for more readings yet!', file=sys.stderr)

        return DataCapture()
