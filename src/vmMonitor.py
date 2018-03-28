try:
    import psutil
except ImportError:
    print "FATAL ERROR: psutil module not installed\nsuggestion: pip isntall psutil"

try:
    import progressbar
except ImportError:
    print "progressbar module is not installed, though not required it is suggested to be installed\nsuggestion: pip install progressbar2"

import threading
import time
import datetime
import vmMonitor_pb2, vmMonitor_pb2_grpc
import os

from resAgentConfig import *
from sparkRestAPIInterface import *
from DB import DB


class vmMonitor(vmMonitor_pb2_grpc.vmMonitorServicer):

    def __init__(self, oResAgent):
        self._oResAgent = oResAgent
        self.pollDuration = POLL_DURATION
        self.cacheSize = CACHE_SIZE
        self.userReqeust = None

        self.vmStat = VMHealtCheck()
        self.sparkStat = sparkHealthCheck()

        self.activeMonitoring = False
        self.db = DB()

    def is_spark_running(self):

        spark_process_name = "sparkwindows.exe"
        for p in psutil.process_iter():
            if p.name().lower() == spark_process_name:
                return True
        return False

    def is_webex_running(self):
        webex_process_name = "atmgr.exe"
        for p in psutil.process_iter():
            if p.name().lower() == webex_process_name:
                return True
        return False

    def getVMStatus(self, request, context):
        response = vmMonitor_pb2.vmStatus(
            cpuPercent=self.vmStat.cpu_percent,
            cpuPercentPerCpu=",".join([str(x) for x in self.vmStat.cpu_percent_per_cpu]),
            vmemPercent=self.vmStat.vmem_percent,
            smemPercent=self.vmStat.smem_percent,
        )
        return response

    def getSparkStatus(self, request, context):
        response = vmMonitor_pb2.sparkStatus(
            isAlive=self.sparkStat.is_alive,
            isLoggedIn=self.sparkStat.is_logged_in,
            loggedInUser=self.sparkStat.logged_in_user,
            pairedDeviceId=self.sparkStat.paired_device_id,
            callState=self.sparkStat.call_state,
            isInLobby=self.sparkStat.is_in_lobby,
            sparkVersion=self.sparkStat.spark_version,
            mediaStats=json.dumps(self.sparkStat.media_stats),
            packetStats=json.dumps(self.sparkStat.packet_stats),
        )
        return response

    #####
    # None GRPC Interface methods
    #####

    def startStatusMonitor(self):

        if not self.activeMonitoring:
            print "Starting status monitor"
            self.activeMonitoring = True
            self.monitor()

    def stopStatusMonitor(self):
        if self.activeMonitoring:
            print "Stopping status monitor"
            self.activeMonitoring = False

    def monitor(self):
        '''
        This will keep monitoring the system for any potential call
        and in case of a call, it will dump data to database
        :return: None
        '''

        userRequest = self._oResAgent.getUserRequest()

        if not userRequest:
            # This is test case, when running vmMonitor stand-alone
            #class dummy:
            #    resType = 'win'
            #    resIP = '10.1.11.0'
            #    resStatus = 'OCCUPIED'
            #    occupier = 'dummy@example.com'
            #    occupyExpireTimeStamp = str(datetime.datetime.now())
            #    timestamp = str(datetime.datetime.now())
            #    jobUUID = '007'
            self.activeMonitoring = False
            return

        while self.activeMonitoring:
            records = []
            for i in range(self.cacheSize):
                self.vmStat.getVMResUsage()
                self.sparkStat.getSparkUsage()
                ts = datetime.datetime.now()

                client_type = "NA"

                if self.is_webex_running():
                    client_type = "WEBEX"
                elif self.is_spark_running():
                    client_type = "SPARK"

                records.append(
                    (
                        str(ts),	                                                   # 'timestamp'
                        str(userRequest.jobUUID),	                                   # 'uuid'
                        str(userRequest.resIP),	                                       # 'ip'
                        client_type,                                                   # 'client_type'
                        str(self.vmStat.cpu_percent),	                               # 'cpu_percent'
                        ", ".join([str(x) for x in self.vmStat.cpu_percent_per_cpu]),  # 'cpu_percent_per_cpu'
                        str(self.vmStat.vmem_percent),	                               # 'vmem_percent'
                        str(self.vmStat.smem_percent),	                               # 'smem_percent'
                        str(self.sparkStat.is_alive),	                               # 'is_alive'
                        str(self.sparkStat.is_logged_in),	                           # 'is_logged_in'
                        str(self.sparkStat.logged_in_user),	                           # 'logged_in_user'
                        str(self.sparkStat.paired_device_id),	                       # 'paired_device_id'
                        str(self.sparkStat.call_state),	                               # 'call_state'
                        str(self.sparkStat.is_in_lobby),	                           # 'is_in_lobby'
                        json.dumps(self.sparkStat.media_stats, ensure_ascii=True),	   # 'media_stats'
                        json.dumps(self.sparkStat.packet_stats, ensure_ascii=True),	   # 'packet_stats'
                        ''                                                             # additional information
                )
                )
                time.sleep(self.pollDuration)
            #self.db.dump(records)
            self.db.storeStatus(records)

class VMHealtCheck:

    def __init__(self):

        self.cpu_percent = 0.0             # Overall cpu usage
        self.cpu_percent_per_cpu = []      # Cpu usage per core
        self.vmem_percent = 0.0            # Virtual Memory usage
        self.smem_percent = 0.0            # Swap Memory usage

        self.getVMResUsage()

    def getVMResUsage(self):
        self.cpu_percent = psutil.cpu_percent(interval=1)  # Overall cpu usage
        self.cpu_percent_per_cpu = psutil.cpu_percent(interval=1, percpu=True)  # Cpu usage per core
        self.vmem_percent = psutil.virtual_memory().percent  # Virtual Memory usage
        self.smem_percent = psutil.swap_memory().percent  # Swap Memory usage


class sparkHealthCheck:

    def __init__(self):
        self.ip = 'localhost'

        self.is_alive = False

        self.is_logged_in = False
        self.logged_in_user = False
        self.paired_device_id = "NA"

        self.call_state = "NA"
        self.is_in_lobby = False

        self.spark_version = "NA"
        self.media_stats = {}
        self.packet_stats = {}

        self.sparkRestAPI = sparkRestAPI()
        self.getSparkUsage()

    def reset(self):
        self.is_alive = False
        self.is_logged_in = False
        self.logged_in_user = False
        self.paired_device_id = "NA"
        self.call_state = "NA"
        self.is_in_lobby = False
        self.spark_version = "NA"
        self.media_stats = {}
        self.packet_stats = {}


    def getSparkUsage(self):
        ip = self.ip

        self.is_alive = self.sparkRestAPI.isAlive(ip)
        if self.is_alive:
            self.is_logged_in = self.sparkRestAPI.isLoggedIn(ip)
            self.logged_in_user = self.sparkRestAPI.loggedInUser(ip)
            self.paired_device_id = self.sparkRestAPI.pairedDeviceID(ip)
            self.call_state = self.sparkRestAPI.callState(ip)
            if self.call_state != "DISCONNECTED":
                self.is_in_lobby = self.sparkRestAPI.isInLobby(ip)
                self.media_stats = self.sparkRestAPI.mediaStats(ip)
                self.packet_stats = self.sparkRestAPI.packetStats(ip)
            else:
                self.is_in_lobby = False
                self.media_stats = {}
                self.packet_stats = {}
        else:
            self.reset()

def pbar(duration):
    time.sleep(1)
    try:
        bar = progressbar.ProgressBar()
        for i in bar(range(duration)):
            time.sleep(1)
    except:
        time.sleep(duration)
    time.sleep(1)
    print

def showStats():
    vmStat = VMHealtCheck()

    print "Collecting device stats..."
    pbar(5)
    #time.sleep(5)
    print "CPU usage (overall): %s%%" % str(vmStat.cpu_percent)
    print "CPU usage (per core): %s" % str(vmStat.cpu_percent_per_cpu)
    print
    print "Virtual Memory usage: %s%%" % str(vmStat.vmem_percent)
    print "Swap Memory Usage: %s%%" % str(vmStat.smem_percent)
    print

    print "Collecting spark stats..."
    sparkStat = sparkHealthCheck()
    pbar(5)
    #time.sleep(30)
    print "Is alive? %s" % str(sparkStat.is_alive)
    print "Is logged in? %s" % str(sparkStat.is_logged_in)
    print "Logged in user: %s" % sparkStat.logged_in_user
    print "Paired device ID: %s" % str(sparkStat.paired_device_id)
    print
    print "call state: %s" % str(sparkStat.call_state)
    print "waiting in lobby? %s" % str(sparkStat.is_in_lobby)
    print
    print "Media Stats:"
    for k in sparkStat.media_stats:
        print "\t%s -> %s" % (k, sparkStat.media_stats[k])

    print "Packet Stats:"
    for k in sparkStat.packet_stats:
        print "\t%s -> %s" % (k, sparkStat.packet_stats[k])

    time.sleep(2)

if __name__ == "__main__":
    # showStats()
    vhm = vmMonitor(5, 6)
    #vhm.isMeetingActive = True
    #threading.Thread(target = vhm.startStatusMonitor).start()
    #time.sleep(30)
    #vhm.stopStatusMonitor()
    #time.sleep(2)

    db = DB()
    #db.storeStatus([("2018-03-22 11:12:13", "012", "0.0.0.0", "dummy", "10.4", "[10.4, 0.0]", "4.5", "9.8", "True", "True", "cgautam", "NA", "Connected", "True", "{}", "{}", "res1")])