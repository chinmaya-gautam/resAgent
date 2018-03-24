import sys
import os

libsPath = os.path.abspath(__file__ + "/../libs")
sys.path.insert(0,libsPath)

from concurrent import futures
import grpc
import time
import datetime
import threading
import socket
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

from WBXTFLogex import *
from resAgentConfig import *

from resConfig import *

class ResAgent:

    _vmStatus = resManager_pb2.resStatusInfo.AVAILABLE
    _occupierInfo = None

    def __init__(self, resAdminServerAddr=DEFAULT_RES_ADMIN_SERVER_ADDR):

        self.resAdminServerAddr = resAdminServerAddr

        self._vmBooker = VMBooker(self)
        self._vmBooker.setDaemon(True)

        self.vmMonitor = vmMonitor.vmMonitor(self)

        # Note this is not a thread, start is just a function
        self.start()

    def getUserRequest(self):
        return self._occupierInfo

    def updateVMStatus(self, adminResponse):
        self._vmStatus = adminResponse.resStatus
        if self._vmStatus == resManager_pb2.resStatusInfo.AVAILABLE:
            self._occupierInfo = None
        else:
            self._occupierInfo = adminResponse

    def start(self):
        self._vmBooker.start()

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
        WBXTFLogInfo("Shutting down resource agent ...")
        # maybe kill resource manager too
        os._exit(0)


if __name__ == "__main__":
    WBXTFLogSetLogLevel(WBXTF_DEBUG)
    timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime("%y%m%d%H%M%S")
    logFilePath = os.path.join(os.path.split(os.path.realpath(__file__))[0], "log/ResAgent_log_%s.txt" % timeStamp)
    WBXTFLogSetLogFilePath(logFilePath)

    WBXTFLogInfo("Set ResAdmin server address : %s" % sys.argv[1])
    vmBooker = VMBooker(sys.argv[1])
    vmBooker.setDaemon(True)
    vmBooker.start()

    agentServer = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    generalTA_pb2_grpc.add_generalTAServicer_to_server(generalTAService.generalTAServer(agentServer), agentServer)
    # Uncomment to use vmMonitor as a grpc service
    # vmMonitor_pb2_grpc.add_vmMonitorServicer_to_server(vmMonitor.vmMonitor(pollDuration=5, cacheSize=6), agentServer)
    agentServer.add_insecure_port("[::]:11831")
    agentServer.start()

    try:
        while True:
            time.sleep(ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        vmBooker.join()

    pass