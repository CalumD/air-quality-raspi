import argparse

from influxdb import InfluxDBClient

test1 = argparse.ArgumentParser()

test2 = InfluxDBClient(host='influxDB.docker.local')

if __name__ == '__main__':
    print(test2.get_list_database())
    test2.close()
    pass
