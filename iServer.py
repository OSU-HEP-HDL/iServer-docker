import socket
import sys
import time
import datetime
import re
from influxdb import InfluxDBClient
import requests

client = None
dbname = 'dcsDB'
iServerHost = '10.206.68.18'
# iServer ip address

def connectiServer(hostname, port, content):
    ''' connect to iServer and access temperature/RH'''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.sendall(content.encode('utf-8'))
    s.shutdown(socket.SHUT_WR)
    data = s.recv(1024)
    s.close()
    return data
    

def readiServer(hostname):
    ''' read temperature/RH value from iServer  '''

    temp = connectiServer(hostname, 1000, "*SRTF\r")
    while temp.decode('utf-8') is '':
        print("Couldn't get temperature. Re-trying.")
        temp = connectiServer(hostname, 1000, "*SRTF\r")
    temp = float(re.findall(r'[-+]?\d*\.\d+', temp.decode('utf-8'))[0])

    rh = connectiServer(hostname, 1000, "*SRH2\r")
    while rh.decode('utf-8') is '':
        print("Couldn't get humidity. Re-trying.")
        rh = connectiServer(hostname, 1000, "*SRH2\r")
    rh = float(re.findall(r'[-+]?\d*\.\d+', rh.decode('utf-8'))[0])

    return temp, rh

def uploaddata(temperature, humidity):
    """influxdb info format"""
    data_list = [{
        'measurement': 'teststand',
        'tags': {'cpu': 'aspen'},
        'fields':{
            'time': datetime.datetime.now().strftime("%H:%M:%S"),
            'iServer_temperature': temperature,
            'iServer_rh': humidity
            }
        }]

    return data_list


def db_exists():
    '''returns True if the database exists'''
    dbs = client.get_list_database()
    for db in dbs:
        if db['name'] == dbname:
            return True
    return False

def wait_for_server(host, port, nretries=5):
    '''wait for the server to come online for waiting_time, nretries times.'''
    url = 'http://{}:{}'.format(host, port)
    waiting_time = 1
    for i in range(nretries):
        try:
            requests.get(url)
            return 
        except requests.exceptions.ConnectionError:
            print('waiting for', url)
            time.sleep(waiting_time)
            waiting_time *= 2
            pass
    print('cannot connect to', url)
    sys.exit(1)

def connect_db(host, port, reset):
    '''connect to the database, and create it if it does notexist'''
    global client
    print('connecting to database: {}:{}'.format(host,port))
    client = InfluxDBClient(host, port, retries=5, timeout=1)
    wait_for_server(host, port)
    if not db_exists():
        client.create_database(dbname)
    client.switch_database(dbname)

if __name__ == '__main__':
    import sys
    from optparse import OptionParser

    parser = OptionParser('%prog [OPTIONS] <host> <port>')
    parser.add_option(
            '-r', '--reset', dest='reset',
            help='reset database',
            default=False,
            action='store_true'
            )
    parser.add_option(
            '-n', '--nmeasurements', dest='nmeasurements',
            type='int',
            help='reset database',
            default=0
            )

    options, args = parser.parse_args()
    if len(args)!=2:
        parser.print_usage()
        print('please specify two arguments')
        sys.exit(1)

    host, port = args
    connect_db(host, port, options.reset)

    while True:
        temp, rh = readiServer(iServerHost)
        print('temperature: {} F, humidity = {} % RH '.format(temp, rh))
        client.write_points(uploaddata(temp, rh))
        time.sleep(3)

