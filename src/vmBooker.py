import sys
import os

libsPath = os.path.abspath(__file__ + "/../libs")
sys.path.insert(0,libsPath)

from concurrent import futures
import grpc
import resManager_pb2
import resManager_pb2_grpc
import generalTA_pb2
import generalTA_pb2_grpc
import generalTAService
import vmMonitor_pb2, vmMonitor_pb2_grpc
import vmMonitor
import cmdParser_pb2
import cmdParser_pb2_grpc
from WBXTFLogex import *
import time
import datetime
import threading
import socket
from sys import platform as _platform

from resAgentConfig import *


class VMBooker(threading.Thread):
    def __init__(self, oResAgent):
        threading.Thread.__init__(self)

        self._oResAgent = oResAgent
        self._machineIp = socket.gethostbyname(socket.gethostname())
        # if this machine has 192.xx ip will use it as toolurl
        IPinfo = socket.gethostbyname_ex(socket.gethostname())
        for ip in IPinfo[2]:
            if ip.find("192") != -1:
                self._machineIp = ip
                break

        self._channel = grpc.insecure_channel(self._oResAgent.resAdminServerAddr)
        self._channel.subscribe(self.onChannelIndication,True)
        self._stub = resManager_pb2_grpc.resManagerStub(self._channel)
        self._statusInfo = None
        self.initResStatusInfo()
        self._lastStatus = None

    def initResStatusInfo(self):
        self._statusInfo = resManager_pb2.resStatusInfo()
        self._statusInfo.resType = self.getOSName()
        self._statusInfo.resIP = self._machineIp
        self._statusInfo.resStatus = resManager_pb2.resStatusInfo.AVAILABLE

    def getOSName(self):
        if _platform == "linux" or _platform == "linux2":
            return "linux"
        elif _platform == "darwin":
            return "mac"
        elif _platform == "win32" or _platform == "win64":
            return "win"
        else:
            return "unknown"

    def onChannelIndication(self,channelStauts):
        WBXTFLogInfo("GRPC Status : %s" % channelStauts)

    def run(self):
        while self._oResAgent.keepAliveVMBooker:
            try:
                adminResponse = self._stub.updateResPool(self._statusInfo)
                self._statusInfo = adminResponse
                if self._lastStatus != adminResponse.resStatus:
                    WBXTFLogInfo("Res state changed from:%s to %s" % (self._lastStatus,adminResponse.resStatus))
                    self._oResAgent.updateVMStatus(adminResponse)
                    self._lastStatus = adminResponse.resStatus

            except grpc.RpcError, err:
                WBXTFLogError("GRPC Error : %s" % err)
            except Exception, e:
                WBXTFLogError("Unknow Error : %s" % e)
            time.sleep(1)


if __name__ == "__main__":
    WBXTFLogSetLogLevel(WBXTF_INFO)
    timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime("%y%m%d%H%M%S")
    logFilePath = os.path.join(os.path.split(os.path.realpath(__file__))[0], "log/ResAgent_log_%s.txt" % timeStamp)
    WBXTFLogSetLogFilePath(logFilePath)

    if len(sys.argv) > 1 :
        WBXTFLogInfo("Set ResAdmin server addr : %s" % sys.argv[1])

        class dummyResAgent:
            '''
            Dummy class to suuport standalone execution of vmBooker
            '''
            def __init__(self):
                self._vmStatus = resManager_pb2.resStatusInfo.AVAILABLE
                self.resAdminServerAddr = sys.argv[1]

        oDummyResAgent = dummyResAgent()
        vmBooker = VMBooker(oDummyResAgent)
        vmBooker.setDaemon(True)
        vmBooker.start()

        try:
            while True:
                time.sleep(ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            vmBooker.join()
    else:
        WBXTFLogError("Not enough params")


    pass