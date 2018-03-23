import paramiko
import logging
import time
import threading
import json
import os
from paramiko.ssh_exception import NoValidConnectionsError
from wbxtf.WBXTFLogex import WBXTFLogInfo, WBXTFLogError, WBXTFLogWarning
from wbxtfResourceMgr.status_monitor_samplers import *


__author__ = 'Ares Ou (weou@cisco.com)'


DEFAULT_INTERVAL = 1000     # ms
# used to adjust the latency during executing a command to remote host
DEFAULT_SSH_PORT = 22


class StatusMonitor(object):
    """A monitor to get real-time utilization information
    from the given remote host. IP address and login credentials
    are required. For now this class only works as a delegation
    from Windows machines to monitor Linux machines.
    """
    def __init__(self, *args, **kwargs):
        # monitor only serve for one request per time.
        self._started = False
        self._monitoring = False
        self._current_thread = None
        self._target_host = None
        self._username = None
        self._password = None
        self._port = None
        self._connected = False
        self._interval = DEFAULT_INTERVAL
        self._ssh_client = None
        self._metric_list = []
        self._info = {}
        # set the level to warning, otherwise paramiko will output
        # a lot of debug logs.
        logging.getLogger("paramiko").setLevel(logging.WARNING)

    def _execute_sampler(self, metric):
        # call the function and return its output
        cls = METRIC_TO_SAMPLING[metric]
        data = cls.sample(self._ssh_client)
        cls.put_data(data, self._info)
        return data

    def _monitor(self):
        WBXTFLogInfo('Monitoring...')

        while self._monitoring:
            # even if monitoring has been stopped or paused, we will continue
            # to sample until a full iteration through the metric list is completed.

            for index in range(len(self._metric_list)):
                self._execute_sampler(self._metric_list[index])

            # convert milliseconds to seconds
            time.sleep(self._interval / 1000.0)

    def connect_to(self, target_host, port=DEFAULT_SSH_PORT, username=None, password=None):
        """Connect to the target host with username and password.
        Will start monitoring after user calls start_monitor()
        """
        if self._started:
            WBXTFLogWarning('Please stop current monitor before you connect to a new host!')
            return False
        WBXTFLogInfo('Preparing to connect to host %s' % target_host)
        self._target_host = target_host
        self._username = username
        self._password = password
        self._port = port
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.load_system_host_keys()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self._ssh_client.connect(self._target_host, self._port, self._username, self._password)
        except NoValidConnectionsError as e:
            WBXTFLogError('Connection failed. Errors: \n %s' % e)

            return False

        self._connected = True
        WBXTFLogInfo('Connection established successfully to hoset %s.' % target_host)

        return True

    def set_monitor_metrics(self, metric_list=None):
        """By default, if user do not provide metric list, we will
        try to monitor overall CPU and memory usage.
        """
        if not metric_list:
            self._metric_list = [METRIC_OVERALL_CPU_USAGE, METRIC_OVERALL_MEMORY_USAGE]
        else:
            self._metric_list = [item for item in metric_list if item in METRIC_TO_SAMPLING]

    def execute_command(self, command_string):
        """Execute a command and return the output in an order of
        stdin, stdout and stderr.
        """
        if self._ssh_client:
            return self._ssh_client.exec_command(command_string)
        else:
            WBXTFLogWarning('You must connect to a host before you send any commands.')
            return False

    def set_interval(self, interval=DEFAULT_INTERVAL):
        self._interval = interval

    def start_monitor(self):
        if self._monitoring:
            return True

        if not self._metric_list:
            raise Exception('Please set metrics before starting the monitor!')

        self.reset_data()
        self._started = True
        self._monitoring = True
        t = threading.Thread(target=self._monitor)
        self._current_thread = t
        self._current_thread.start()
        return True

    def pause_monitor(self):
        self._monitoring = False

    def resume_monitor(self):
        if not self._started:
            WBXTFLogError('Could not resume monitor because it is not started yet.')

            return False

        self._monitoring = True
        self._monitor()

        return True

    def stop_monitor(self):
        self._monitoring = False
        self._started = False
        while self._current_thread.is_alive():
            # wait until current thread complete before closing the client.
            # Otherwise the transport under current SSH client will be closed
            # and trigger exception.
            time.sleep(0.1)
        self._ssh_client.close()
        return True

    def reset_data(self):
        self._info = {}

    def get_info(self,nLastCount = 0):
        """Return the last n record current information stored in memory."""
        if nLastCount == 0:
            return self._info
        else:
            retVal = {}
            for key in self._info.keys():
                retCount = min(len(self._info[key][METRIC_FIELD_DATA]),nLastCount)
                totalDataPoints = self._info[key][METRIC_FIELD_DATA].keys()
                lastNPoint = totalDataPoints[len(totalDataPoints)-retCount:]
                retVal[key] = OrderedDict()
                for point in lastNPoint:
                    retVal[key][point] = self._info[key][METRIC_FIELD_DATA][point]
            return retVal

    def get_info_file(self):
        """Return the current information stored in file."""
        if self._info:
            file_name = 'status_monitor_%s_%s.json' % (self._target_host, datetime.now().strftime("%y%m%d%H%M%S"))
            WBXTFLogInfo('Writing monitor information to file %s' % file_name)
            try:
                with open(file_name, 'wb') as f:
                    f.writelines(json.dumps(self._info))
            except IOError as e:
                WBXTFLogError('Error writing file...')
                WBXTFLogError(e)
                return False
            else:
                WBXTFLogInfo('Successfully exported monitor information to file.')
                return os.path.abspath(file_name)

    def get_now(self, metric):
        # do not put the one time execution data into dictionary
        return self._execute_sampler(metric)

    def get_average(self, metric):
        """Return average of the specific metric"""
        return self._info[metric][METRIC_FIELD_AVERAGE]

    def get_median(self, metric):
        """Simple implementation of finding a median from a list of numbers."""
        # TODO: use statistics.median in Python 3
        array = sorted(list(self._info[metric][METRIC_FIELD_DATA].values()))
        half, odd = divmod(len(array), 2)
        if odd:
            return array[half]
        return (array[half - 1] + array[half]) / 2.0

    def get_max(self, metric):
        try:
            return max(self._info[metric][METRIC_FIELD_DATA].iteritems(),
                       key=lambda x: x[1])
        except KeyError:
            return None

    def get_min(self, metric):
        try:
            return min(self._info[metric][METRIC_FIELD_DATA].iteritems(),
                       key=lambda x: x[1])
        except KeyError:
            return None


if __name__ == '__main__':
    monitor = StatusMonitor()
    monitor.connect_to('10.195.135.80', username='root', password='pass')
    # monitor.connect_to('10.194.242.233', username='user', password='pass')
    # monitor.set_monitor_metrics(metric_list=[METRIC_MMP_CPU_USAGE])
    monitor.set_monitor_metrics()
    monitor.set_interval(600)
    print monitor.get_now(METRIC_MMP_CPU_USAGE)
    print monitor.get_now(METRIC_OVERALL_MEMORY_USAGE)
    monitor.start_monitor()
    time.sleep(30)
    monitor.stop_monitor()
    print monitor.get_info()
    print monitor.get_max(METRIC_OVERALL_CPU_USAGE)
    print monitor.get_min(METRIC_OVERALL_CPU_USAGE)
    print monitor.get_median(METRIC_OVERALL_CPU_USAGE)
    print monitor.get_average(METRIC_OVERALL_CPU_USAGE)
    print monitor.get_info()[METRIC_OVERALL_CPU_USAGE][METRIC_FIELD_DATA]
    print monitor.get_max(METRIC_OVERALL_MEMORY_USAGE)
    print monitor.get_min(METRIC_OVERALL_MEMORY_USAGE)
    print monitor.get_median(METRIC_OVERALL_MEMORY_USAGE)
    print monitor.get_average(METRIC_OVERALL_MEMORY_USAGE)
    print monitor.get_info()[METRIC_OVERALL_MEMORY_USAGE][METRIC_FIELD_DATA]
    print monitor.get_info_file()
