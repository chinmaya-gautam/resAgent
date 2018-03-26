import generalTA_pb2
import generalTA_pb2_grpc
import sys
import time
import psutil
import os
import threading
from WBXTFLogex import *

class generalTAServer(generalTA_pb2_grpc.generalTAServicer):
    def __init__(self,serverPtr):
        generalTA_pb2_grpc.generalTAServicer.__init__(self)
        self._server = serverPtr

    def exitThreadFunc(self,exitWaitSec = 0):
        time.sleep(exitWaitSec)
        self._server.stop(0)
        WBXTFLogInfo("grpc server stopped. server process will be killed.")
        ps = psutil.Process(os.getpid())
        ps.terminate()

    def exitMe(self, request, context):
        exitDelaySec = 0
        if hasattr(request,"exitDelaySec"):
            exitDelaySec = request.exitDelaySec
        exitAction = threading.Thread(target=self.exitThreadFunc, args=(exitDelaySec,))
        exitAction.start()
        return generalTA_pb2.exitResponse(retCode= 1)

