import sys
import os

basePath = os.path.abspath(__file__ + "/../../")
libsPath = os.path.abspath(basePath + "/libs")
grpcIncludes = os.path.abspath(basePath + "/grpc_includes")
sys.path.insert(0, basePath)
sys.path.insert(1,libsPath)
sys.path.insert(2, grpcIncludes)

from concurrent import futures
import grpc
import time
import datetime
import threading
import socket
import subprocess
import atexit

from sys import platform as _platform

import generalTA_pb2_grpc
import generalTAService

import resManager_pb2
import resManager_pb2_grpc
import generalTA_pb2
import vmMonitor_pb2, vmMonitor_pb2_grpc
import vmMonitor
import cmdParser_pb2
import cmdParser_pb2_grpc

from vmBooker import VMBooker
from resMgr_v2 import wbxtfResourceMgr
from WBXTFLogex import *
from resAgentConfig import *


class ResAgent:

    _vmStatus = resManager_pb2.resStatusInfo.AVAILABLE
    _occupierInfo = None

    def __init__(self, resAdminServerAddr=DEFAULT_RES_ADMIN_SERVER_ADDR):

        atexit.register(self.cleanup)

        self.resAdminServerAddr = resAdminServerAddr

        self.keepAliveVMBooker = True
        self._vmBooker = VMBooker(self)
        self._vmBooker.setDaemon(True)

        self.vmMonitor = vmMonitor.vmMonitor(self)

        self.resMgrProcess = None
        self.autoUpdaterProcess = None

        # Note this is not a thread, start is just a function
        self.start()

    def startResMgr(self):
        resMgrPath = os.path.abspath(basePath + "/resMgr_v2/wbxtfResourceMgr/wbxtfResMgr.py")
        resMgrProcess = subprocess.Popen(resMgrPath, shell=True)
        return resMgrProcess

    def stopResMgr(self):
        if isinstance(self.resMgrProcess, subprocess.Popen):
            self.resMgrProcess.terminate()
            return True
        return False

    def startAutoUpdater(self):
        autoUpdaterPath = os.path.join(basePath, "src", "resAgentAutoUpdater.py")
        autoUpdaterProcess = subprocess.Popen(autoUpdaterPath, shell=True)
        return autoUpdaterProcess

    def stopAutoUpdater(self):
        if isinstance(self.autoUpdaterProcess, subprocess.Popen):
            self.autoUpdaterProcess.terminate()
            return True
        return False

    def getUserRequest(self):
        return self._occupierInfo

    def updateVMStatus(self, adminResponse):
        self._vmStatus = adminResponse.resStatus
        if self._vmStatus == resManager_pb2.resStatusInfo.AVAILABLE:
            self._occupierInfo = None
        else:
            self._occupierInfo = adminResponse

    def start(self):
        # Start wbxtfResMgr.py
        WBXTFLogInfo("Starting Resource Manager...")
        self.resMgrProcess = self.startResMgr()

        WBXTFLogInfo("Starting VM Booker...")
        self._vmBooker.start()

        WBXTFLogInfo("Starting Auto Updater...")
        self.autoUpdaterProcess = self.startAutoUpdater()


        try:
            while True:
                if self._vmStatus != resManager_pb2.resStatusInfo.AVAILABLE:
                    self.vmMonitor.startStatusMonitor()
                else:
                    # For any other status
                    self.vmMonitor.stopStatusMonitor()

                time.sleep(5)
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            WBXTFLogError("Exception caught: %s" % str(e))

    def cleanup(self):
        try:
            WBXTFLogInfo("Shutting down resource agent ...")

            WBXTFLogInfo("Shutting down resource manager ...")
            self.stopResMgr()
            WBXTFLogInfo("Shutting down auto updater...")
            self.stopAutoUpdater()
            WBXTFLogInfo("Shutting down vm monitor ...")
            self.vmMonitor.stopStatusMonitor()
            WBXTFLogInfo("Shutting down vm booker ...")
            self.keepAliveVMBooker = False
            self._vmBooker.join(10)
        except Exception as e:
            WBXTFLogError("Exception trying to cleanup: %s, resource agent will continue to exit..." % (str(e)))
        WBXTFLogInfo("Completed all cleanup tasks, resource agent will exit in 3 seconds. Bye...")
        time.sleep(3)
        os._exit(0)

if __name__ == "__main__":
    WBXTFLogSetLogLevel(WBXTF_DEBUG)
    timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime("%y%m%d%H%M%S")
    logFilePath = os.path.join(os.path.split(os.path.realpath(__file__))[0], "../log/ResAgent_log_%s.txt" % timeStamp)
    WBXTFLogSetLogFilePath(logFilePath)


    agentServer = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    generalTA_pb2_grpc.add_generalTAServicer_to_server(generalTAService.generalTAServer(agentServer), agentServer)
    # Uncomment to use vmMonitor as a grpc service
    # vmMonitor_pb2_grpc.add_vmMonitorServicer_to_server(vmMonitor.vmMonitor(pollDuration=5, cacheSize=6), agentServer)
    agentServer.add_insecure_port("[::]:11831")
    agentServer.start()

    ra = ResAgent()
    ra.start()
    pass