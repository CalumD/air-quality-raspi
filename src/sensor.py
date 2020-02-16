#!/usr/bin/env python


class Sensor:

    def __init__(self):
        # TODO implement the sensor initialisation.
        pass

    def read(self):
        # TODO implement reading the data from the sensor
        return "Here is some data."

# try:
#     from smbus2 import SMBus
# except ImportError:
#     from smbus import SMBus

# try:
#     sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
# except IOError:
#     sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
#
# sensor.set_humidity_oversample(bme680.OS_2X)
# sensor.set_pressure_oversample(bme680.OS_4X)
# sensor.set_temperature_oversample(bme680.OS_8X)
# sensor.set_filter(bme680.FILTER_SIZE_3)
#
# while True:
#     if sensor.get_sensor_data():
#         print("Temperature: {:05.2f} *C".format(sensor.data.temperature))
#         time.sleep(1.0)
#
