__author__ = 'huajin2'

import sys
import os


pylibPath = os.path.abspath(__file__ + "/../../")
wbxtfPath = os.path.abspath(pylibPath + "/wbxtf")
thirdPartyPath = os.path.abspath(pylibPath + "/ThirdParty")
sys.path.insert(0,pylibPath)
sys.path.insert(1,wbxtfPath)
sys.path.insert(2,thirdPartyPath)


from wbxtf.WBXTFLogex import *
from wbxtf.WBXTFPYToolHelp import *
from wbxtf.WBXTFActionPool import *

RM_TOOL_ASK = "ASK"
RM_TOOL_WBXUIA = "WBXUIA"
RM_TOOL_THINCLIENT = "ThinClientTool"
RM_TOOL_THINCLIENT_EUREKA = "ThinClientTooleureka"
RM_TOOL_PERTEST = "Pertest"
RM_TOOL_UA = "UA"
#import psutil
import socket
import urllib2
import socket
import json
import types
import shutil
import subprocess
from status_monitor import StatusMonitor, DEFAULT_SSH_PORT
from toolMgr import *
from tool_version_manager import ToolVersionManager

class wbxtfPingAgent(threading.Thread):
    def __init__(self,masterIP,masterURL,checkingIntervalSec = 5):
        threading.Thread.__init__(self)
        self._masterIP = masterIP
        self._masterURL = masterURL
        self._checkingIntervalSec = checkingIntervalSec
        IPinfo = socket.gethostbyname_ex(socket.gethostname())
        self._localIP = IPinfo[2][0]
        for ip in IPinfo[2]:
            if ip.find("10.1") != -1 or ip.find("192.168") != -1:
                self._localIP = ip
                break

    def pingWBXTF(self,machine):
        oWBXTF = WBXTF.WBXTFGetWBXTFObj(machine)
        ret = oWBXTF.util.Ping()
        if ret["rc"] == 0 and ret["result"] == "PONG":
            return True
        else:
            return False

    def pingMasterWBXTF(self):
        return self.pingWBXTF(self._masterIP)

    def pingLocalWBXTF(self):
        return self.pingWBXTF("local")


    def updateInfoToMaster(self,infoDict):
        requestURL = self._masterURL
        bodyData = {}
        bodyData["ip"] = self._localIP
        bodyData.update(infoDict)
        bodyDataString = json.dumps(bodyData)
        requestURL += r"/" + self._localIP
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(
            url = requestURL,
            data = bodyDataString,
            headers={"Content-Type":"application/json",}
        )
        request.get_method = lambda : "PUT"
        try:
            strResponse = opener.open(request).read()
            dictResponse = eval(strResponse)
            WBXTFLogDebug("master server response = %s" % dictResponse)
            if dictResponse.has_key("status_code"):
                if dictResponse["status_code"] == 200:
                    return True
            else:
                WBXTFLogError("Master server response can not be parsed, return = %s" % strResponse)
                return False
        except urllib2.HTTPError,httpErr:
            if httpErr.code == 404:
                request.get_method = lambda : "POST"
                try:
                    strResponse = opener.open(request).read()
                    dictResponse = eval(strResponse)
                    WBXTFLogDebug("master server response = %s" % dictResponse)
                    if dictResponse.has_key("status_code") and dictResponse["status_code"] == 201:
                        return True
                    else:
                        WBXTFLogError("Post data to Master failed, return = %s" % strResponse)
                        return False
                except Exception, e:
                    WBXTFLogError("add machine info to %s failed, errorinfo = %s" % (requestURL,e))
                    return False
            else:
                 WBXTFLogError("add machine info to %s failed, errorinfo = %s" % (requestURL,httpErr))
                 return False
        except Exception, e:
            WBXTFLogError("add machine info to %s failed, errorinfo = %s" % (requestURL,e))
            return False
        pass


    def run(self):
        while True:
            if self.pingLocalWBXTF() == False:
                self.updateInfoToMaster({"status":"WBXTF Offline"})
                WBXTFLogWarning("Local WBXTF is not running")
            else:
                # if self.pingMasterWBXTF() == False:
                #     self.updateInfoToMaster({"status":"WBXTF Offline"})
                #     WBXTFLogWarning("Master server WBXTF is not running")
                # else:
                #     self.updateInfoToMaster({"status":"WBXTF Online"})
                #     WBXTFLogDebug("Ping Master server(%s) WBXTF success " % self._masterIP)
                WBXTFLogDebug("Ping local WBXTF success ")
                self.updateInfoToMaster({"status": "WBXTF Online"})
            time.sleep(self._checkingIntervalSec)
        pass


class wbxtfResMgr(object):
    def __init__(self,configPath = ""):
        self._mgrCtrInterface = wbxtfResMgrCtrInterface(self)
        self._mgrCtr = wbxtfPyToolModule(self._mgrCtrInterface)
        self._mgrCtr.setupToolName("wbxtfResourceMgr")
        self._mgrCtr.daemon = True
        self._lock = threading.Lock()
        self._configLock = threading.Lock()
        if configPath =="": configPath = os.path.abspath(__file__ + "\..\wbxtfResMgrConfig.py")
        self.__loadParamFile(configPath)
        self._toolMgr = toolMgr()
        self._toolMgr.daemon = True
        self._monitor = StatusMonitor()
        self._toolVerMgr = ToolVersionManager(self.getParam("PFTBaseURL"))

        pass

    @property
    def Monitor(self):
        return self._monitor

    @property
    def ToolMgr(self):
        return self._toolMgr

    @property
    def ToolVerMgr(self):
        return self._toolVerMgr

    def __loadParamFile(self, file):
        with self._configLock:
            var = {}
            WBXTFLogInfo("loading config file = %s" % file)
            if os.path.isfile(file):
                execfile(file, var)
                for k,v in var.items():
                    if type(k) == types.StringType:
                        setattr(self, k, v)
            else:
                WBXTFLogError("config file is not found. file path = %s" % file)

    def getParam(self,paramName,defaultValue = None):
        try:
            with self._configLock:
                return getattr(self,paramName)
        except Exception, e:
            if defaultValue == None:
                WBXTFLogError("Required input param(%s) is not found" % paramName)
                raise
            else:
                return defaultValue

    def start(self):
        self._mgrCtr.start()
        self._toolMgr.start()
        try:
            while True:
                time.sleep(30)
        except KeyboardInterrupt:
            WBXTFLogInfo("Resource Manager interrupted, will exit")
            self.stop()
            sys.exit(0)

    def stop(self):
        #WBXTFLogInfo("unregistering tools")
        #self._mgrCtr.unregisterTool()
        time.sleep(1)

class wbxtfResMgrCtrInterface(wbxtfPyToolModuleInterfaceBase):
    def __init__(self,ptrMgr):
        """
        :type ptrMgr: wbxtfResMgr
        """
        super(wbxtfResMgrCtrInterface,self).__init__()
        self._resMgr = ptrMgr
        self._lock = threading.RLock()

    def reportManagedToolsInfo(self):
        return  self._resMgr.ToolMgr.reportManagedTools()

    def reportUnmanagedToolsInfo(self):
        return  self._resMgr.ToolMgr.reportUnmanagedTools()

    def killUnmanagedTools(self,toolTypes = None):
        return self._resMgr.ToolMgr.killUnmangedTools(toolTypes)

    def cleanToolsByType(self,toolType,toolURLs):
        WBXTFLogInfo("Kill Tool:%s for object:%s" % (toolType,toolURLs))
        self._resMgr.ToolMgr.cleanToolsByType(toolType,toolURLs)
        return 0

    def runwbxUIAs(self,version,ownerName,ownerURL,toolNum,timeout = 60):
        toolDir = self._resMgr.ToolVerMgr.get_local_path(TOOL_WBXUIA, str(version))
        if toolDir == None:
            errString = "wbxUIA version:%s could not be found in local." % version
            WBXTFLogWarning(errString)
            return errString
        toolPath = toolDir + r"\wbxUIA.exe"
        return self._resMgr.ToolMgr.runManagedTools(ownerName,ownerURL,toolPath,TOOL_WBXUIA,toolNum,None,timeout)

    def runThinClientTools(self,version,ownerName,ownerURL,toolNum,timeout = 60):
        toolDir = self._resMgr.ToolVerMgr.get_local_path(TOOL_THINCLIENT, str(version))
        if toolDir == None:
            errString = "thinclient tool version:%s could not be found in local." % version
            WBXTFLogWarning(errString)
            return errString

        #for thin client we need run a local web server "Host.py" first
        # self._resMgr.ToolMgr.runManagedProcess(ownerName,ownerURL,"python",1,toolDir + r"\Build\host.py")
        # time.sleep(1)
        toolPath =  toolDir + r"\TCToolWrapper.py"
        return self._resMgr.ToolMgr.runManagedTools(ownerName,ownerURL,toolPath,TOOL_THINCLIENT,toolNum,None,timeout)

    def runManagedTools(self,ownerName,ownerURL,toolPath,toolType,toolNum,toolParam = None,timeout = 60):
        return self._resMgr.ToolMgr.runManagedTools(ownerName,ownerURL,toolPath,toolType,toolNum,toolParam,timeout)

    def runUnmanagedTools(self,toolPath,toolType,toolNum,toolParam = None,timeout = 60):
        return self._resMgr.ToolMgr.runUnmanagedTools(toolPath,toolType,toolNum,toolParam,timeout)

    def runManagedProcess(self,ownerName,ownerURL,procPath,procNum,procParam = None):
        return self._resMgr.ToolMgr.runManagedProcess(ownerName,ownerURL,procPath,procNum,procParam)

    def runUnmanagedProcess(self,procPath,procNum,procParam = None):
        return self._resMgr.ToolMgr.runUnmanagedProcess(procPath,procNum,procParam)

    def addCmd4wbxtfObjExit(self,wbxtfURL,cmd):
        return self._resMgr.ToolMgr.addCmd4wbxtfObjExit(wbxtfURL,cmd)

    def getRunningToolCount(self,toolType):
        return self._resMgr.ToolMgr.getRunningToolCount(toolType)

    def getMonitorInfo(self):
        return self._resMgr.Monitor.get_info()

    def getMonitorInfoFilePath(self):
        return self._resMgr.Monitor.get_info_file()

    def connectMonitorToHost(self, host, username=None, password=None, port=DEFAULT_SSH_PORT):
        return self._resMgr.Monitor.connect_to(target_host=host, username=username, password=password, port=port)

    def setMonitorInterval(self, interval):
        return self._resMgr.Monitor.set_interval(interval)

    def setMoniterMetrics(self,metricsList = None):
        return self._resMgr.Monitor.set_monitor_metrics(metricsList)

    def getMonitorInfoNow(self, metric):
        """Get the info from host immediately, data will not be written into the
        data dictionary.
        """
        return self._resMgr.Monitor.get_now(metric)

    def getMonitorInfoEx(self,nLastCount = 0):
        return self._resMgr.Monitor.get_info(nLastCount)

    def getMonitorMetricMax(self, metric):
        return self._resMgr.Monitor.get_max(metric)

    def getMonitorMetricMin(self, metric):
        return self._resMgr.Monitor.get_min(metric)

    def getMonitorMetricMedian(self, metric):
        return self._resMgr.Monitor.get_median(metric)

    def getMonitorMetricAverage(self, metric):
        return self._resMgr.Monitor.get_average(metric)

    def startMonitor(self):
        return self._resMgr.Monitor.start_monitor()

    def stopMonitor(self):
        return self._resMgr.Monitor.stop_monitor()

    def pauseMonitor(self):
        return self._resMgr.Monitor.pause_monitor()

    def resumeMonitor(self):
        return self._resMgr.Monitor.resume_monitor()

    def addRemoteTool(self, name, version, target_folder=None):
        return self._resMgr.ToolVerMgr.add_remote_tool(name, str(version), target_folder)

    def addLocalTool(self, name, version, local_path):
        return self._resMgr.ToolVerMgr.add_local_tool(name, str(version), local_path)

    def removeTool(self, tool_name, version):
        return self._resMgr.ToolVerMgr.remove_tool(tool_name, str(version))

    def loadToolsList(self):
        self._resMgr.ToolVerMgr.load()

    def saveToolsList(self):
        self._resMgr.ToolVerMgr.save()

    def getAllTools(self):
        return self._resMgr.ToolVerMgr.all_tools()

    def reportToolsList(self):
        return self._resMgr.ToolVerMgr.report()

    def getRemoteToolInfo(self, tool_name, version):
        return self._resMgr.ToolVerMgr.get_tool_info_from_remote(tool_name, str(version))

    def getRemoteToolPath(self, tool_name, version):
        return self._resMgr.ToolVerMgr.get_remote_path(tool_name, str(version))

    def getLocalToolPath(self, tool_name, version):
        return self._resMgr.ToolVerMgr.get_local_path(tool_name, str(version))

    def prepareTools(self, tool_list, callback=None):
        return self._resMgr.ToolVerMgr.prepare_tools(tool_list, callback)


if __name__ == '__main__':
    WBXTFLogSetLogLevel(WBXTF_DEBUG)
    logPath = os.path.abspath(__file__ + "/../log.txt")
    WBXTFLogSetLogFilePath(logPath,1024*1024*5,3)

    oMgr = wbxtfResMgr()
    oMgr.start()

    pass