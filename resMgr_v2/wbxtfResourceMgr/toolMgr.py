__author__ = 'huajin2'

import os
import sys

pylibPath = os.path.abspath(__file__ + "/../../")
grpcPath = os.path.abspath(pylibPath + "/grpc")
sys.path.insert(0, grpcPath)

import WBXTF
import WBXTFTool
import time
import grpc
from wbxtf import WBXTFService
import socket
import threading
from wbxtf.WBXTFLogex import *
import resManager_pb2, resManager_pb2_grpc

TOOL_ASK = "tool_ask"
TOOL_PERTEST = "tool_pertest"
TOOL_WBXUIA = "tool_wbxUIA"
TOOL_THINCLIENT = "tool_thinclient"

TOOL_SUPPORT_LIST = [TOOL_ASK, TOOL_PERTEST, TOOL_WBXUIA, TOOL_THINCLIENT]
TOOL_TYPE_CATEGORY = {TOOL_ASK: WBXTFTool.WBXTFToolType_C,
                      TOOL_PERTEST: WBXTFTool.WBXTFToolType_C,
                      TOOL_WBXUIA: WBXTFTool.WBXTFToolType_C,
                      TOOL_THINCLIENT: WBXTFTool.WBXTFToolType_Python}


class toolMgr(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="toolMgr")
        self._managedToolsInfo = {}
        self._managedProcessInfo = {}
        self._unmanagedToolsInfo = {}
        self._lock = threading.Lock()
        self._machineIp = "local"
        IPinfo = socket.gethostbyname_ex(socket.gethostname())
        self._machineIp = IPinfo[2][0]
        for ip in IPinfo[2]:
            if ip.find("10.1") != -1 or ip.find("192.168") != -1:
                self._machineIp = ip
                break

        self._cmd4wbxtfObjExit = {}

    ####  toolCategory
    # WBXTFToolType_C = "c"
    # WBXTFToolType_Java = "java"
    # WBXTFToolType_Python = "python"
    def _runTools(self, toolPath, toolCategory, toolNum, toolParam=None, timeout=60):
        wbxtfTM = WBXTFTool.WBXTFToolMgr()
        wbxtfTM.setToolType(toolCategory)
        wbxtfTM.setToolPath(toolPath)
        wbxtfTM.setMachines([self._machineIp])
        if toolParam != None:
            wbxtfTM.setToolParams(toolParam)
        retVal = wbxtfTM.runToolsOnMachinesByTotal([self._machineIp], totalNum=toolNum, timeout=timeout)
        return retVal

    def _runProcess(self, procPath, procNum, procParam=None):
        return WBXTF.WBXTFRun(self._machineIp, procPath, procParam, procNum)

    def _checkGRPCHeartbeat(self, addr):
        try:
            channel = grpc.insecure_channel(addr)
            stub = resManager_pb2_grpc.resAgnetStub(channel)
            response = stub.checkHeartBeat()
            return response.isAlive
        except Exception as e:
            WBXTFLogError("Exception checking GRPC heartbeat at %s: %s" % (addr, str(e)))
            return False

    def _isOwnerURLVaild(self, URL):

        def _checkURLType(url):
            try:
                prefix = url[:5]
                if prefix == 'wbxtf':
                    return "WBXTF"
                else:
                    return "GRPC"
            except Exception as e:
                WBXTFLogError("Exception %s. url type for %s could not be determined." % (e, URL))
                # return default wbxtf type
                return "WBXTF"

        if _checkURLType == "GRPC":
            return self._checkGRPCHeartbeat(URL)

        else:
            try:
                objOwner = WBXTF.WBXTFObject(URL, 1)
                oRes = objOwner.WBXTFGetTags()
                if oRes["rc"] == 0:
                    return True
                return False
            except Exception, e:
                WBXTFLogError("Exception %s.  OwnerURL(%s) is not Vailed." % (e, URL))
                return False

    def cleanToolsByType(self, toolType, toolURLs):
        WBXTFLogInfo("cleaning toolType=%s " % toolType)
        if toolType == TOOL_WBXUIA:
            # kill ie process tree
            WBXTFService.WBXTFKillProcessTreeByName(["local"], "iexplore.exe")  # kill brower and meetingclient
            WBXTFService.WBXTFKillProcessTreeByName(["local"], "wbxUIA.exe")
            WBXTFService.WBXTFKillProcessTreeByName(["local"], "atmgr.exe")
            # for toolURL in toolURLs:
            #     #oTool = WBXTF.WBXTFObject(toolURL)
            #     # res = oTool.getGlobalBrowerPID()
            #     # if res.has_key("rc") and res["rc"]==0:
            #     #     WBXTFService.WBXTFKillProcessTreeByPID(["local"],res["result"])# kill brower and meetingclient
            #     # else:
            #     #     WBXTFLogError("get wbxUIA's IE pid failed.")
            #     res = oTool.getPID()
            #     if res.has_key("rc") and res["rc"]==0:
            #         WBXTFService.WBXTFKillProcessTreeByPID(["local"],res["result"])
            #     else:
            #         WBXTFLogError("get wbxUIA pid failed.")

        if toolType == TOOL_ASK or toolType == TOOL_PERTEST:
            handles = []
            for toolURL in toolURLs:
                wbxtfHandle = toolURL.split("$")[1]
                handles.append(wbxtfHandle)
            WBXTF.WBXTFStop("local", handles)

        if toolType == TOOL_THINCLIENT:
            for toolURL in toolURLs:
                oTool = WBXTF.WBXTFObject(toolURL)
                res = oTool.getPID()
                if res.has_key("rc") and res["rc"] == 0:
                    WBXTFService.WBXTFKillProcessTreeByPID(["local"], res["result"])
                else:
                    WBXTFLogError("get thin client tool pid failed.")

    def _getToolCategoryByToolType(self, toolType):
        if toolType in TOOL_SUPPORT_LIST:
            return TOOL_TYPE_CATEGORY[toolType]
        else:
            WBXTFLogError("toolType:%s is not supported! " % toolType)
            return None

    def runUnmanagedTools(self, toolPath, toolType, toolNum, toolParam=None, timeout=60):
        WBXTFLogInfo("runUnmanagedTools  toolPath=%s , toolType=%s , toolNum=%s , toolParam=%s" %
                     (toolPath, toolType, toolNum, toolParam))

        toolCategory = self._getToolCategoryByToolType(toolType)
        if toolCategory == None: return None

        oToolObjs = self._runTools(toolPath, toolCategory, toolNum, toolParam, timeout)
        retToolURLs = None
        if len(oToolObjs) > 0:
            retToolURLs = []
            for oTool in oToolObjs:
                retToolURLs.append(oTool.url)
            with self._lock:
                if self._unmanagedToolsInfo.has_key(toolType):
                    self._unmanagedToolsInfo[toolType] += retToolURLs
                else:
                    self._unmanagedToolsInfo[toolType] = retToolURLs
            WBXTFLogInfo("run Unmanaged tool:%s count:%s success. Total count on this machine:%s" %
                         (toolType, toolNum, len(self._unmanagedToolsInfo[toolType])))
        else:
            WBXTFLogError("run unmanaged tool failed.")
        return retToolURLs

    def runManagedTools(self, ownerName, ownerURL, toolPath, toolType, toolNum, toolParam=None, timeout=60):
        WBXTFLogInfo(
            "runManagedTools ownerName=%s , ownerUR=%s , toolPath=%s , toolType=%s , toolNum=%s , toolParam=%s" %
            (ownerName, ownerURL, toolPath, toolType, toolNum, toolParam))

        toolCategory = self._getToolCategoryByToolType(toolType)
        if toolCategory == None: return None

        if self._isOwnerURLVaild(ownerURL):
            toolObjs = self._runTools(toolPath, toolCategory, toolNum, toolParam, timeout)
            retToolURLs = None
            if len(toolObjs) > 0:
                retToolURLs = []
                for oTool in toolObjs:
                    ##using ip
                    retToolURLs.append(oTool.url)

                    ##using hostname
                    # toolURL = oTool.url
                    # hostName = socket.gethostname()
                    # retToolURL = "wbxtf://" + hostName + toolURL[toolURL.find("/tool."):]
                    # retToolURLs.append(retToolURL)
                with self._lock:
                    if self._managedToolsInfo.has_key(ownerName):
                        if self._managedToolsInfo[ownerName]["toolsDict"].has_key(toolType):
                            self._managedToolsInfo[ownerName]["toolsDict"][toolType] += retToolURLs
                        else:
                            self._managedToolsInfo[ownerName]["toolsDict"][toolType] = retToolURLs
                    else:
                        newManagedInfo = {}
                        newManagedInfo["ownerName"] = ownerName
                        newManagedInfo["ownerURL"] = ownerURL
                        newManagedInfo["toolsDict"] = {toolType: retToolURLs}
                        self._managedToolsInfo[ownerName] = newManagedInfo

                WBXTFLogInfo("run managed tool:%s count:%s success for owner:%s . Total count on this machine:%s" %
                             (toolType, toolNum, ownerName,
                              len(self._managedToolsInfo[ownerName]["toolsDict"][toolType])))
            else:
                WBXTFLogError("run managed tool failed.")
            return retToolURLs
        else:
            WBXTFLogError("ownerURL:%s is invalid" % ownerURL)
            return None

    def runUnmanagedProcess(self, procPath, procNum, procParam=None):
        WBXTFLogInfo("runUnmanagedProcess procPath=%s ,procNum=%s ,procParam=%s" % (procPath, procNum, procParam))
        retVal = False
        ret = self._runProcess(procPath, procNum, procParam)
        if len(ret) == procNum:
            retVal = True
            WBXTFLogInfo("run unmanaged process:%s count:%s success" % (procPath, procNum))
        return retVal

    def runManagedProcess(self, ownerName, ownerURL, procPath, procNum, procParam=None):
        WBXTFLogInfo("runManagedProcess ownerName=%s,ownerURL=%s,procPath=%s ,procNum=%s ,procParam=%s" %
                     (ownerName, ownerURL, procPath, procNum, procParam))
        if self._isOwnerURLVaild(ownerURL):
            retHandles = self._runProcess(procPath, procNum, procParam)
            with self._lock:
                if self._managedProcessInfo.has_key(ownerName):
                    self._managedProcessInfo[ownerName]["wbxtfHandles"] += retHandles
                else:
                    newManagedProcInfo = {}
                    newManagedProcInfo["ownerName"] = ownerName
                    newManagedProcInfo["ownerURL"] = ownerURL
                    newManagedProcInfo["wbxtfHandles"] = retHandles
                    self._managedProcessInfo[ownerName] = newManagedProcInfo
            WBXTFLogInfo("run managed process:%s count:%s for owner:%s success." % (procPath, procNum, ownerName))
            return True
        else:
            WBXTFLogError("ownerURL:%s is invalid" % ownerURL)
            return False

    def addCmd4wbxtfObjExit(self, wbxtfURL, cmd):
        WBXTFLogInfo("addCmd4wbxtfObjExit wbxtfURL=%s,cmd=%s" % (wbxtfURL, cmd))
        if self._isOwnerURLVaild(wbxtfURL):
            with self._lock:
                if self._cmd4wbxtfObjExit.has_key(wbxtfURL):
                    self._cmd4wbxtfObjExit[wbxtfURL].append(cmd)
                else:
                    self._cmd4wbxtfObjExit[wbxtfURL] = [cmd]
            return True
        else:
            WBXTFLogError("wbxtfURL:%s is invalid" % wbxtfURL)
            return False

    def reportManagedTools(self):
        return self._managedToolsInfo

    def reportUnmanagedTools(self):
        return self._unmanagedToolsInfo

    def reportManagedProcess(self):
        return self._managedProcessInfo

    def killUnmangedTools(self, toolTypes=None):
        if toolTypes == None:  # kill all unmanaged Tools
            toolTypes = TOOL_SUPPORT_LIST
        for toolType in self._unmanagedToolsInfo.keys():
            if toolType in toolTypes:
                self.cleanToolsByType(toolType, self._unmanagedToolsInfo[toolType])
                with self._lock:
                    del self._unmanagedToolsInfo[toolType]

    def run(self):
        while 1:
            try:
                for ownerName in self._managedToolsInfo.keys():
                    url = self._managedToolsInfo[ownerName]["ownerURL"]
                    if self._isOwnerURLVaild(url) == False:
                        WBXTFLogInfo(
                            "tools owner:%s (url=%s) is not valid any more, its managed tools will be killed" % (
                            ownerName, url))
                        for toolType in self._managedToolsInfo[ownerName]["toolsDict"].keys():
                            self.cleanToolsByType(toolType, self._managedToolsInfo[ownerName]["toolsDict"][toolType])
                        with self._lock:
                            del self._managedToolsInfo[ownerName]
                    else:
                        for toolType, toolURLList in self._managedToolsInfo[ownerName]["toolsDict"].items():
                            newURLList = []
                            for toolURL in toolURLList:
                                if self.isToolAlive(toolURL):
                                    newURLList.append(toolURL)
                            with self._lock:
                                self._managedToolsInfo[ownerName]["toolsDict"][toolType] = newURLList

                for ownerName in self._managedProcessInfo.keys():
                    url = self._managedProcessInfo[ownerName]["ownerURL"]
                    if self._isOwnerURLVaild(url) == False:
                        WBXTFLogInfo(
                            "process owner:%s (url=%s) is not valid any more, its managed process will be killed" % (
                            ownerName, url))
                        WBXTF.WBXTFStop("local", self._managedProcessInfo[ownerName]["wbxtfHandles"])
                        self.killProcessByHandles(
                            self._managedProcessInfo[ownerName]["wbxtfHandles"])  # for window 2008
                        with self._lock:
                            del self._managedProcessInfo[ownerName]

                for wbxtfObjURL in self._cmd4wbxtfObjExit.keys():
                    if self._isOwnerURLVaild(wbxtfObjURL) == False:
                        for cmd in self._cmd4wbxtfObjExit[wbxtfObjURL]:
                            WBXTF.WBXTFExecCmd("local", cmd)
                        with self._lock:
                            del self._cmd4wbxtfObjExit[wbxtfObjURL]

                time.sleep(1)
            except Exception, e:
                WBXTFLogError("Exception caught in toolMgr checking thread. error:%s" % e)

    # def isToolAlive(self,toolURL):
    #     oTool = WBXTF.WBXTFObject(toolURL)
    #     oRes = oTool.WBXTFGetTags()
    #     if oRes["rc"] == 0 :
    #         return True
    #     return False

    def killProcessByHandles(self, handleList):
        if len(handleList) > 0:
            objProcess = WBXTF.WBXTFObject("wbxtf://local/process")
            ret = objProcess.List()
            if ret["rc"] == 0:
                for item in ret["result"]:
                    if item["endStamp"] == "None" and item["dwHandle"] in handleList:
                        cmd = "taskkill /F /T /PID %s" % item["dwPID"]
                        WBXTFService.WBXTFExecCmd("local", cmd)

    def isToolAlive(self, toolURL):
        toolHandle = toolURL[toolURL.find('$') + 1:]
        wbxtfHandleObj = WBXTF.WBXTFObject("wbxtf://local/handle")
        res = wbxtfHandleObj.Query(toolHandle)
        if res["rc"] == 0 and res["result"] != None:
            return True
        return False

    def getRunningToolCount(self, toolType):
        retCount = 0
        for ownerName, ownerData in self._managedToolsInfo.items():
            if ownerData["toolsDict"].has_key(toolType):
                retCount += len(ownerData["toolsDict"][toolType])
        return retCount


if __name__ == "__main__":
    # oToolMgr = toolMgr()
    # oToolMgr.start()
    # oToolMgr.runUnmanagedTools(r"C:\PF_Tools\wbxUIA\wbxUIA.exe",WBXTFTool.WBXTFToolType_C,2)
    # oToolMgr.runManagedTools("TestOwner",r"wbxtf://local/tool.$62",r"C:\PF_Tools\wbxUIA\wbxUIA.exe",TOOL_WBXUIA,1)
    # oToolMgr.runManagedTools("TestOwner",r"wbxtf://local/tool.$57",r"C:\Git\webex-systemtest-performance-pylib\ThinClient\TCToolWrapper.py",TOOL_THINCLIENT,1)
    # while 1:
    #     time.sleep(10)
    # WBXTFLogInfo("#   WBXTF Resource Manager Version:%s   #" % version)
    # WBXTFLogInfo("############################################")

    pass
