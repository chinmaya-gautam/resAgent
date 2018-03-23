"""A parser to extract monitoring information from OSWbb results.

Will also send the information to PF Machine Portal for a visual
monitoring interface.
"""

import socket
import sys
import logging
import json
import re
from datetime import datetime
try:
    import httplib
except ImportError:
    # Renamed to http.client in Python 3
    from http import client as httplib

try:
    import argparse as arg_lib
    parser = arg_lib.ArgumentParser(description='Parse OSWbb result file and post to PF Machine Portal.')
    parser.add_argument('file_path', type=str, help='The path of file to be parsed.')
    args = parser.parse_args()
    try:
        args = {'file_path': args.file_path}
    except AttributeError:
        args = {'file_path': ''}
except ImportError:
    # argparse is only available in and after Python 2.7
    import optparse as arg_lib
    parser = arg_lib.OptionParser(description='Parse OSWbb result file and post to PF Machine Portal.')
    # parser.add_option('file_path', type=str, help='The path of file to be parsed.')
    options, args = parser.parse_args()
    if args:
        args = {'file_path': args.pop(0)}
    else:
        args = {'file_path': ''}


__author__ = 'Ares Ou (weou@cisco.com)'


API_URL = '/api/v1/db_server_status'
API_HOST_ADDRESS = '192.168.22.11'
API_HOST_PORT = '7777'

HOSTNAME = socket.gethostname()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

REGEX_TIME = re.compile(r'zzz[ *]*[a-zA-Z]+? ([a-zA-Z\d: ]+)')
REGEX_LOAD_AVERAGE = re.compile(r'load average:[ ]*([\d.]*)[, ]+([\d.]*)[, ]+([\d.]*)')
REGEX_CPU_IDLE = re.compile(r'[CPUcpu].*,[ ]*([\d.]*)[% ]*id,')

FIELD_TIMESTAMP = 'timestamp'
FIELD_LAST_ONE_MINUTE_LOAD = 'last_one_minute_load'
FIELD_LAST_FIVE_MINUTES_LOAD = 'last_five_minutes_load'
FIELD_LAST_FIFTEEN_MINUTES_LOAD = 'last_fifteen_minutes_load'
FIELD_CPU_USAGE = 'cpu_usage'


def parse_timestamp(line, data):
    match = REGEX_TIME.search(line)
    if match:
        # Find a header line containing the time info
        # the format is like `Oct 11 16:00:04 GMT 2016`
        data.append({'hostname': HOSTNAME})
        data[-1][FIELD_TIMESTAMP] = datetime.strptime(match.group(1), '%b %d %X %Z %Y').isoformat()

        return True

    return False


def parse_load_average(line, data):
    match = REGEX_LOAD_AVERAGE.search(line)
    # The load average line is like:
    # `top - 16:00:05 up 56 days, 20:55,  1 user,  load average: 2.00, 1.59, 1.50`
    # The last three numbers represent load average in last 1, 5 and 15 minutes
    if match:
        data[-1][FIELD_LAST_ONE_MINUTE_LOAD] = match.group(1)
        data[-1][FIELD_LAST_FIVE_MINUTES_LOAD] = match.group(2)
        data[-1][FIELD_LAST_FIFTEEN_MINUTES_LOAD] = match.group(3)

        return True

    return False


def parse_cpu_usage(line, data):
    match = REGEX_CPU_IDLE.search(line)
    if match:
        data[-1][FIELD_CPU_USAGE] = 100.0 - float(match.group(1))

        return True

    return False


def post_data(data):
    # Connection will not be established immediately, so try-except block
    # is put below.
    client = httplib.HTTPConnection(API_HOST_ADDRESS, API_HOST_PORT, timeout=3)
    try:
        client.request('POST', API_URL, json.dumps(data), {'Content-type': 'application/json'})
    except socket.timeout:
        logger.error('Timeout when connecting to PF Machine Portal, program will exit!')
        return False

    resp = client.getresponse()

    if resp.status != 200:
        logger.error('Couldn\'t post data to PF Machine Portal!')
        return False
    else:
        return True


def parse_and_post(path):
    logger.info('Start to parse the file %s...' % path)

    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except IOError as e:
        logger.exception(e)
        logger.error('Cound not open data file, program will exit now!')
        sys.exit(1)

    logger.info('File successfully loaded.')

    section_started = False
    data = []

    if __name__ == '__main__':
        for line in lines:
            # process every line and extract time, CPU and other information.
            if not section_started and line.startswith('zzz'):
                section_started = parse_timestamp(line, data)
            elif section_started:
                # Already inside a data section, parsing other lines
                if parse_load_average(line, data): continue
                if parse_cpu_usage(line, data):
                    section_started = False

    if data:
        logger.info('Data parsed, ready to post.')
        if post_data(data):
            logger.info('Data uploaded, program will exit now.')
        else:
            logger.error('Data couldn\'t be uploaded!')
    else:
        logger.info('No data parsed, program will exit now.')


if __name__ == '__main__':
    file_path = args['file_path']
    if not file_path:
        logger.error('You must provide the data file path!')
        sys.exit(1)

    parse_and_post(file_path)

