'''
Standalone script, tests functionality of various vmAgent modules.
'''
from concurrent import futures
import sys
import os


basePath = os.path.abspath(__file__ + "/../../")
libsPath = os.path.abspath(basePath + "/libs")
grpcIncludes = os.path.abspath(basePath + "/grpc_includes")
wbxtfPath = os.path.abspath(__file__ + r"/../wbxtf")
sys.path.insert(0, basePath)
sys.path.insert(1, libsPath)
sys.path.insert(2, grpcIncludes)
sys.path.insert(3, wbxtfPath)


import grpc
import datetime
import time
import copy
import threading

from wbxtf import WBXTF
import resManager_pb2, resManager_pb2_grpc

class DummyResMgr(resManager_pb2_grpc.resManagerServicer):
    def __init__(self):
        self._resMap = dict()


    def checkHeartBeat(self, request, context):
        print "HeartBeat check [alive]"
        response = resManager_pb2.heartBeat(
            isAlive=True
        )
        return response

    def reserveWindows(self):

        print "Reserving Window"
        resNum = 1
        occupier = "dummyuser@cisco.com"
        now = datetime.datetime.fromtimestamp(time.time())
        resOccupyExpireTimeStamp = (now + datetime.timedelta(seconds=600)).strftime("%y%m%d%H%M%S")
        ip = "10.1.10.10"
        self._resMap[ip] = dict()
        self._resMap[ip]["resOccupier"] = occupier
        self._resMap[ip]["jobUUID"] = "001"
        self._resMap[ip]["resStatus"] = resManager_pb2.resStatusInfo.PENDING
        self._resMap[ip]["resOccupyExpireTimeStamp"] = resOccupyExpireTimeStamp
        return True

    def releaseWindows(self):
        print "Releasing Window"
        ip = "10.1.10.10"
        self._resMap[ip]["resStatus"] = resManager_pb2.resStatusInfo.RELEASING
        return True

    def updateResPool(self, request, context):

        resType = request.resType
        resIP = request.resIP
        resStatus = request.resStatus
        resOccupier = request.occupier
        resOccupyExpireTimeStamp = request.occupyExpireTimeStamp
        jobUUID = request.jobUUID
        timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime("%y%m%d%H%M%S")

        response = copy.deepcopy(request)
        response.timestamp = timeStamp
        if self._resMap.has_key(resIP):
            curStatus = self._resMap[resIP]["resStatus"]
            if curStatus == resManager_pb2.resStatusInfo.PENDING and resStatus == resManager_pb2.resStatusInfo.AVAILABLE:
                self._resMap[resIP]["timeStamp"] = timeStamp
                response.resStatus = resManager_pb2.resStatusInfo.OCCUPIED  # Pending to Occupied
                response.occupier = self._resMap[resIP]["resOccupier"]
                response.occupyExpireTimeStamp = self._resMap[resIP]["resOccupyExpireTimeStamp"]
                response.jobUUID = self._resMap[resIP]["jobUUID"]
                return response

            if curStatus == resManager_pb2.resStatusInfo.RELEASING and resStatus == resManager_pb2.resStatusInfo.OCCUPIED:
                self._resMap[resIP]["timeStamp"] = timeStamp
                response.resStatus = resManager_pb2.resStatusInfo.AVAILABLE  # Releasing to Available
                response.occupier = u""
                response.occupyExpireTimeStamp = u""
                response.jobUUID = u""
                return response

        resData = {}
        resData["resType"] = resType
        resData["resIP"] = resIP
        resData["resStatus"] = resStatus
        resData["resOccupier"] = resOccupier
        resData["resOccupyExpireTimeStamp"] = resOccupyExpireTimeStamp
        resData["timeStamp"] = timeStamp
        resData["jobUUID"] = jobUUID
        self._resMap[resIP] = resData
        return response


def testVmBooker(dummyResMgr):
    # Create a dummy resouce manager
    print "waiting for 10 seconds before starting reserve-release test"
    time.sleep(10)
    for i in range(5):
        dummyResMgr.reserveWindows()
        time.sleep(5)
        dummyResMgr.releaseWindows()
        time.sleep(5)

def testManagedCall(dummyResMgr):
    time.sleep(30)
    wbxtf_obj = WBXTF.WBXTFObject("wbxtf://local/tool.wbxtfResourceMgr")
    target_machine = "10.1.10.10"
    callback_url = "10.1.10.10:11830"
    cmd_to_run = "calc"
    num_of_cmds = 1
    print "running", cmd_to_run, "on", target_machine
    ret = wbxtf_obj.runManagedProcess(target_machine, callback_url, cmd_to_run, num_of_cmds)
    print "Result:", ret
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print "ending testManagedCall"

def startDummyResAdminServer():
    print "Starting Dummy Resource Admin Server..."
    dummyResMgr = DummyResMgr()

    def _subfun():
        dummyAdminServer = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        resManager_pb2_grpc.add_resManagerServicer_to_server(dummyResMgr, dummyAdminServer)
        dummyAdminServer.add_insecure_port("[::]:11830")
        dummyAdminServer.start()
        while True:
            time.sleep(3600)

    t = threading.Thread(target=_subfun)
    t.daemon = True
    t.start()
    time.sleep(5)
    print "Dummy Resource Admin Server started."

    return dummyResMgr

if __name__ == "__main__":

    dummyResMgr = startDummyResAdminServer()

    #print "testing VM Booker..."
    #testVmBooker(dummyResMgr)

    print "testing managed process call..."
    testManagedCall(dummyResMgr)