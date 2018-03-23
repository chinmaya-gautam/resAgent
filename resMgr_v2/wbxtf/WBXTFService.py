import WBXTF
import time
import os
from types import *
WBXTF_PROT_STAF = "staf"
WBXTF_PROT_WBXTF = "wbxtf"
from wbxtf.WBXTFLogex import *

####################################################################################################
#Get WBXTF Object

def WBXTFGetProt():
    #return WBXTF_PROT_STAF
    return WBXTF_PROT_WBXTF

def WBXTFGetReportIPObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/reportip"%(WBXTFGetProt(),machine))
    return obj

def WBXTFGetWBXTFObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/wbxtf"%(WBXTFGetProt(),machine))
    return obj

def WBXTFGetEnvObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/env"%(WBXTFGetProt(),machine))
    return obj

def WBXTFGetMachineObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/"%(WBXTFGetProt(),machine))
    return obj

def WBXTFGetToolObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/tool"%(WBXTFGetProt(),machine))
    return obj

def WBXTFGetPyObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/py"%(WBXTFGetProt(),machine))
    return obj

def WBXTFGetJavaObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/java"%(WBXTFGetProt(),machine))
    return obj

def WBXTFGetProcessObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/process"%(WBXTFGetProt(),machine))
    return obj

def WBXTFGetToolByHandle(machine,handle):
    prot = WBXTFGetProt()
    if(prot ==WBXTF_PROT_STAF):
        obj = WBXTF.WBXTFObject("%s://%s:%d/"%(prot,machine,handle))
        return obj
    else:
        obj = WBXTF.WBXTFObject("%s://%s/tool.$%d"%(prot,machine,handle))
        return obj
    
def WBXTFGetToolBySubID(machine,subID):
    obj = WBXTF.WBXTFObject("%s://%s/tool.[%d]"%(WBXTFGetProt(),machine,subID))
    return obj

def WBXTFGetSysInfoObj(machine):
    obj = WBXTF.WBXTFObject("%s://%s/sysinfo"%(WBXTFGetProt(),machine))
    return obj
                            
    
def WBXTFGetToolByObjID(machine,objID):
    obj = WBXTF.WBXTFObject("%s://%s/tool.{%d}"%(WBXTFGetProt(),machine,objID))
    return obj

####################################################################################################


def WBXTFGetLocalTime(format="%Y-%m-%d %H:%M:%S"):
    nowTime = time.gmtime()
    strNowTime = time.strftime(format, nowTime)
    return strNowTime  


class SaveCaseLogToFile:
    def __init__(self):
        self.m_logPath = ""
        self.m_file = None
        self.m_fileHead = None

    def setLogPath(self,path):
        self.m_logPath = path
    
    def getLogPath(self):
        return self.m_logPath
    
    def onWriteLogFun(self,log):
        newLog = WBXTF.WBXTFGetLogObject().formatLog(log)
        newLog += "\n"
        self.writeLog(newLog)

    def registerWriteLogToFile(self):
        WBXTF.WBXTFLogAddFun(self.onWriteLogFun)

    def unRegisterWriteLogToFile(self):
        WBXTF.WBXTFLogRemoveFun(self.onWriteLogFun)
        self.closeFile()

    def writeLog(self,log):
        self.openFile()
        if(self.m_file !=None):
            self.m_file.write(log)
            self.m_file.flush()
        else:
            print "[SaveCaseLogToFile]m_file is null in writelog function"

    def closeFile(self):
        if self.m_file != None:
            self.m_file.close()
            self.m_file = None
            
    def openFile(self):
        try:
            if self.m_file == None:
                self.m_file = open(self.m_logPath, "w")
                if self.m_fileHead != None:
                    self.m_file.write(self.m_fileHead)
        except Exception,e:
            print "[SaveCaseLogToFile]openFile function exception:%s"%e

g_saveCaseLogToFile = SaveCaseLogToFile() 

def SetSaveCaseLogToFile(filePath):
    g_saveCaseLogToFile.setLogPath(filePath)
    g_saveCaseLogToFile.registerWriteLogToFile()

def StopSaveCaseLogToFile():
    g_saveCaseLogToFile.unRegisterWriteLogToFile()
    g_saveCaseLogToFile.closeFile()



###############################################################################################################
#FS Service


def WBXTFCopyFile(machine,filePath,targetMachine,targetDir,sExtend="FULLPATH"):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        request = "COPY FILE %s TODIRECTORY %s TOMACHINE %s"%(filePath,targetDir,targetMachine)
        res = WBXTF.g_wbxtfSTAF.submit(machine, "fs" , request)
        if(res["rc"]==0):
            return True
        else:
            print "WBXTFCopyFile failed,res=%s"%res
        return False
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.CopyFileToDir(filePath,targetMachine,targetDir,sExtend)
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0):
            return True
        else:
            print "WBXTFCopyFile failed,res=%s"%res
        return False

def WBXTFCopyFileToFile(machine,filePath,targetMachine,targetFile,sExtend="FULLPATH"):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        request = "COPY FILE %s TODIRECTORY %s TOMACHINE %s"%(filePath,targetFile,targetMachine)
        res = WBXTF.g_wbxtfSTAF.submit(machine, "fs" , request)
        if(res["rc"]==0):
            return True
        else:
            print "WBXTFCopyFileToFile failed,res=%s"%res
        return False
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.CopyFileToFile(filePath,targetMachine,targetFile,sExtend)
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0):
            return True
        else:
            print "WBXTFCopyFile failed,res=%s"%res
        return False

    
def WBXTFCopyDir(machine,dirPath,targetMachine,targetDir,sExtend="RECURSE"):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        #request = "COPY DIRECTORY %s TODIRECTORY %s TOMACHINE %s RECURSE KEEPEMPTYDIRECTORIES"%(dirPath,targetDir,targetMachine)
        request = "COPY DIRECTORY %s TODIRECTORY %s TOMACHINE %s %s"%(dirPath,targetDir,targetMachine,sExtend)
        res = WBXTF.g_wbxtfSTAF.submit(machine, "fs" , request)
        if(res["rc"]==0):
            return True
        else:
            WBXTF.WBXTFOutput("Copy Directory Failed:%s"%res)
        return False
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.CopyDir(dirPath,targetMachine,targetDir,sExtend)
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0):
            return True
        return False

def WBXTFDeleteDir(machine,dirPath,sExtend="RECURSE"):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        service = "fs"
        #request = "DELETE ENTRY %s CONFIRM RECURSE"%dirPath
        request = "DELETE ENTRY %s %s"%(dirPath,sExtend)
        res = WBXTF.g_wbxtfSTAF.submit(machine, service, request)
        if(res["rc"]==0):
            return True
        return False
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.DeleteDir(dirPath,sExtend)
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0):
            return True
        else:
            print "WBXTFDeleteDir failed:%s"%res
        return False

def WBXTFDeleteFile(machine,filePath,sExtend=""):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        service = "fs"
        #request = "DELETE ENTRY %s CONFIRM"%(filePath,sExtend)
        request = "DELETE ENTRY %s"%(filePath,sExtend)
        res = WBXTF.g_wbxtfSTAF.submit(machine, service, request)
        if(res["rc"]==0 and res["result"]==0):
            return True
        return False
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.DeleteFile(filePath,sExtend)
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0):
            return True
        return False

def WBXTFCreateDirectory(machine,directory,sExtend="FULLPATH"):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        service = "fs"
        request = "CREATE DIRECTORY %s %s"%(directory,sExtend)
        res = WBXTF.g_wbxtfSTAF.submit(machine, service, request)
        if(res["rc"]==0 and int(res["result"])==0):
            return True
        return False
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.CreateDir(directory,sExtend)
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0):
            return True
        return False

def WBXTFListDirectory(machine,directory,sExtend=""):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        service = "fs"
        request = "LIST DIRECTORY %s %s"%(directory,sExtend)
        res = WBXTF.g_wbxtfSTAF.submit(machine, service, request)
        if(res["rc"]==0 and res["result"]!=None):
            return res["result"]
        return []
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.ListDir(directory,sExtend)
        if(res["rc"]==0 and res["result"]!=None):
            return res["result"]
        return []


def WBXTFIsFileExist(machine,filePath):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        service = "fs"
        request = "QUERY ENTRY %s"%filePath
        res = WBXTF.g_wbxtfSTAF.submit(machine, service, request)
        if(res["rc"]==0 and res["result"]!=None):
            return True
        return False
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.IsFileExist(filePath)
        if(res["rc"]==0 and res["result"]!=None):
            return res["result"]

def WBXTFIsDirExist(machine,dirPath):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        service = "fs"
        request = "QUERY ENTRY %s"%dirPath
        res = WBXTF.g_wbxtfSTAF.submit(machine, service, request)
        if(res["rc"]==0 and res["result"]!=None):
            return True
        return False
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/fs"%machine)
        res = obj.IsDirExist(dirPath)
        if(res["rc"]==0 and res["result"]!=None):
            return res["result"]
###################################################################################################################

###################################################################################################################
#Process Service
def WBXTFExecCmdWithDir(machine,cmd,param = "",workDir=""):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        obj = WBXTF.WBXTFObject("staf://%s/process"%machine)
        extend = "SHELL"
        if(workDir!=""):
            extend = "SHELL WORKDIR %s"%workDir
        res = obj.Run(cmd,param,extend)
        return res
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/process"%machine)
        res = obj.Run(cmd,param,{"SHELL":"","WORKDIR":workDir})
        return res

def WBXTFExecCmd(machine,cmd,param = ""):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        obj = WBXTF.WBXTFObject("staf://%s/process"%machine)
        res = obj.Run(cmd,param,"SHELL")
        return res
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/process"%machine)
        res = obj.Run(cmd,param,{"SHELL":""})
        return res

def WBXTFExecCmdWait(machine,cmd,param = "",nTimeOut=60):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        obj = WBXTF.WBXTFObject("staf://%s/process"%machine)
        res = obj.Run(cmd,param,"SHELL WAIT %d"%(nTimeOut*1000))
        return res
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/process"%machine)
        res = obj.Run(cmd,param,{"SHELL":"","WAIT":nTimeOut*1000})
        return res

def WBXTFExecCmdReturn(machine,cmd,param = "",nTimeOut=60):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        obj = WBXTF.WBXTFObject("staf://%s/process"%machine)
        res = obj.Run(cmd,param,"SHELL WAIT %d RETURNSTDOUT"%(nTimeOut*1000))
        return res
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/process"%machine)
        res = obj.Run(cmd,param,{"SHELL":"","WAIT":nTimeOut*1000,"RETURNSTDOUT":""})
        return res


def UCSRun(machine,cmd,param=""):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return 0
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/process"%machine)
        res = obj.Run(cmd,param,{"SHELL":""})
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0):
            return res["result"]["Result"]["rc"]
        return 0
    
def UCSRunWait(machine,cmd,param="",nTimeOut=60):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return 0
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/process"%machine)
        res = obj.Run(cmd,param,{"SHELL":"","WAIT":nTimeOut*1000})
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0):
            return res["result"]["Result"]["rc"]
        return 0
    
def UCSRunReturn(machine,cmd,param="",nTimeOut=60):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/process"%machine)
        res = obj.Run(cmd,param,{"WAIT":nTimeOut*1000,"RETURNSTDOUT":""})
        if(res["rc"]==0 and res["result"]!=None and res["result"]["RC"]==0 and res["result"]["Result"].has_key("fileList") and res["result"]["Result"]["fileList"]!=None):
            return res["result"]["Result"]["fileList"][0]["data"]
        return None


###################################################################################################################
    
###################################################################################################################
#UCSEvent Service
def UCSWaitEvent(machine,key,nTimeout=-1):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/ucsevent"%machine)
        res = obj.Wait(key,nTimeout)
        print res
        if(res["rc"]==0 and res["result"]!=None and res["result"]==0):
            return True
        return False    
    

    
def UCSSetEvent(machine,key):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/ucsevent"%machine)
        res = obj.Set(key)
        if(res["rc"]==0 and res["result"]!=None and res["result"]==0):
            return True
        return False
        
def UCSClearEvent(machine,key):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/ucsevent"%machine)
        res = obj.Clear(key)
        if(res["rc"]==0 and res["result"]!=None and res["result"]==0):
            return True
        return False
###################################################################################################################
        
###################################################################################################################
#UCS Variable Service
def UCSSetString(machine,key,value):
    prot = WBXTFGetProt()
    sVal = "%s"%value
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/variable"%machine)
        res = obj.Set(key,sVal)
        print res
        if(res["rc"]==0 and res["result"]!=None and int(res["result"])==0):
            return True
        return False
        
def UCSGetString(machine,key):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/variable"%machine)
        res = obj.Get(key)
        if(res["rc"]==0):
            return "%s"%(res["result"])
        return None



    
def UCSSetVariable(machine,key,value):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/variable"%machine)
        res = obj.Set(key,value)
        #print res
        if(res["rc"]==0 and res["result"]!=None and int(res["result"])==0):
            return True
        return False
        
def UCSGetVariable(machine,key):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/variable"%machine)
        res = obj.Get(key)
        if(res["rc"]==0):
            return res["result"]
        return None
        
def UCSClearVariable(machine,key):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/variable"%machine)
        res = obj.Clear(key)
        if(res["rc"]==0 and res["result"]!=None and int(res["result"])==0):
            return True
        return False
    
def UCSListVariable(machine):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/variable"%machine)
        res = obj.List()
        if(res["rc"]==0):
            return res["result"]
        return None

    
def UCSClearAllVariable(machine):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/variable"%machine)
        res = obj.ClearAll()
        if(res["rc"]==0 and res["result"]!=None and int(res["result"])==0):
            return True
        return False
###################################################################################################################
    
###################################################################################################################
#Trace Service
def WBXTFSetTrace(machine,bEnable=True):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/trace"%machine)
        res = obj.SetEnable(bEnable)
        if(res["rc"]==0 and res["result"]!=None and int(res["result"])==0):
            return True
        return False

def WBXTFIsEnableTrace(machine):
    prot = WBXTFGetProt()
    if(prot=="staf"):
        return None
    else:
        obj = WBXTF.WBXTFObject("wbxtf://%s/trace"%machine)
        res = obj.GetEnable()
        if(res["rc"]==0 and res["result"]!=None):
            return res["result"]
        return False
###################################################################################################################





    
def WBXTFSYNCTime(machines):
    resultMachines = {}
    success = 0        
    for machine in machines:
        now = time.time()
        t = time.gmtime(now)
        sTime = time.strftime("%Y-%m-%d %H:%M:%S", t)
        ms = int((now - int(now)) * 1000)                          
        obj = WBXTF.WBXTFGetMachineObj(machine)
        res = obj.Execute("wbxtf.util.UpdateUTCTime(%s, %s)" % (sTime, ms))            
        if res['rc'] == 0 and res['result'] == 0:
            success += 1
        resultMachines[machine] = res 
    totalResult = {}
    if len(machines) == success:
        totalResult['rc'] = 0
    elif success == 0:
        totalResult['rc'] = WBXTF.E_ERROR
    else:
        totalResult['rc'] = WBXTF.S_FALSE        
    totalResult['result'] = resultMachines
    totalResult['success'] = success        
    return totalResult

def WBXTFKillProcessByName(machines,processName,nSleepTime=0,bWindows=True):
    typeVar = type(machines)
    processMachines = []
    if typeVar == StringType:
        processMachines.append(machines)
    elif (typeVar == ListType):
        processMachines = machines
    if(bWindows):
        cmd = "taskkill /F /IM %s"%processName
        for machine in processMachines:
            WBXTFExecCmd(machine,cmd)
            if(nSleepTime!=0):
                time.sleep(nSleepTime)
    else:
        cmd = "killall -9 %s"%processName
        for machine in processMachines:
            WBXTFExecCmd(machine,cmd)
            if(nSleepTime!=0):
                time.sleep(nSleepTime)

def WBXTFKillProcessTreeByName(machines,processName,nSleepTime=0,bWindows=True):
    bWindows =True ## currently only support windows
    typeVar = type(machines)
    processMachines = []
    if typeVar == StringType:
        processMachines.append(machines)
    elif (typeVar == ListType):
        processMachines = machines
    if(bWindows):
        cmd = "taskkill /F /T /IM %s"%processName
        for machine in processMachines:
            WBXTFExecCmd(machine,cmd)
            if(nSleepTime!=0):
                time.sleep(nSleepTime)
    else:
        cmd = "killall -9 %s"%processName
        for machine in processMachines:
            WBXTFExecCmd(machine,cmd)
            if(nSleepTime!=0):
                time.sleep(nSleepTime)

def WBXTFKillProcessByPID(machines,PID,nSleepTime=0,bWindows=True):
    typeVar = type(machines)
    processMachines = []
    if typeVar == StringType:
        processMachines.append(machines)
    elif (typeVar == ListType):
        processMachines = machines
    if(bWindows):
        cmd = "taskkill /F /PID %s"%PID
        for machine in processMachines:
            WBXTFExecCmd(machine,cmd)
            if(nSleepTime!=0):
                time.sleep(nSleepTime)
    else:
        cmd = "killall -9 %s"%PID
        for machine in processMachines:
            WBXTFExecCmd(machine,cmd)
            if(nSleepTime!=0):
                time.sleep(nSleepTime)

def WBXTFKillProcessTreeByPID(machines,PID,nSleepTime=0,bWindows=True):
    bWindows =True ## currently only support windows
    typeVar = type(machines)
    processMachines = []
    if typeVar == StringType:
        processMachines.append(machines)
    elif (typeVar == ListType):
        processMachines = machines
    if(bWindows):
        cmd = "taskkill /F /T /PID %s"%PID
        for machine in processMachines:
            WBXTFExecCmd(machine,cmd)
            if(nSleepTime!=0):
                time.sleep(nSleepTime)
    else:
        cmd = "killall -9 %s"%PID
        for machine in processMachines:
            WBXTFExecCmd(machine,cmd)
            if(nSleepTime!=0):
                time.sleep(nSleepTime)

def WBXTFRunOneProByPath(machines,processName,nSleepTime=0,bWindows=True):
    typeVar = type(machines)
    processMachines = []
    if typeVar == StringType:
        processMachines.append(machines)
    elif (typeVar == ListType):
        processMachines = machines
    for machine in processMachines:
        #WBXTFExecCmd(machine,"powershell Start-Process powershell -Verb runAs " +processName)
        lastSlash = processName.rfind("\\")
        currentPath = processName[0:lastSlash]
        WBXTFExecCmdWithDir(machine, processName,"",currentPath)
        #print "Run %s on the machine: %s!"%(processName,machine)
        if(nSleepTime!=0):
            time.sleep(nSleepTime)

def WBXTFDataStat(dataList,mostList=[]):
    stat = {}
    stat["SampleCount"] = 0
    stat["avg"] = 0
    stat["max"] = 0
    stat["min"] = 0
    stat["middle"] = 0
    stat["most_90"] = 0
    count = len(dataList)
    stat["SampleCount"] = count
    if(count <1):
        return stat
    index = 0
    total = 0
    while(index <count):
        total += dataList[index]
        index +=1
    avgData = float(total)/count
    dataListTemp = dataList
    dataListTemp.sort()
    count = len(dataListTemp)
    minData = dataList[0]
    index = count -1
    if(index<0):
        index = 0
    maxData = dataList[index]
    index = count/2 -1
    if(index<0):
        index = 0
    middleData = dataList[index]
    index = count*9/10 -1
    if(index<0):
        index = 0  
    most_90Data = dataList[index]
    stat["avg"] = avgData
    stat["max"] = maxData
    stat["min"] = minData
    stat["middle"] = middleData
    stat["most_90"] = most_90Data
    for most in mostList:
        most = int(most)
        if(most!=90 and most != 50 and most <100):
            index = count*most/100-1
            if(index<0):
                index =0
            mostData = dataList[(count*most)/100-1]
            
            stat["most_%d"%most]= mostData
    return stat        
        
def WBXTFGetLocalIP():
    ip = ""
    try:
        sh = os.popen("ipconfig")
        ress = sh.readlines()
        sh.close()
        for res in ress:
            if(res.find("IP Address")>-1):
                ips = res.split(":")
                ip = ips[1]
                ip = ip.replace("\r","")
                ip = ip.replace("\n","")
                ip = ip.replace(" ","")
                break
    except Exception,e:
        WBXTF.WBXTFWarning("getLocal IP exception:%s"%e)
    return ip          


def RegisterToolInfoToResMgr(ToolMachine,ToolName,ToolPID,ProcessName,CaseName,CaseMachine,OSType):
    try:
        if CaseName == "":
            return True
        machine = ToolMachine
        toolNode = WBXTF.WBXTFGetToolObj(machine)
        res = toolNode.WBXTFGetSubObjs()
        if res.has_key("rc") and res["rc"] == 0 :
            if res["result"]!= None:
                for item in res["result"]:
                    if item["name"] ==  "wbxtfResourceMgr":
                        resMgrObj = WBXTF.WBXTFGetToolBySubID(machine,item["subid"])
                        WBXTFLogInfo("Register %s to machine:%s with caseName:%s caseMachine:%s " %
                                     (ProcessName,machine,CaseName,CaseName))
                        resMgrObj.registerToolInfo(ToolName,ToolPID,ProcessName,CaseName,CaseMachine,OSType)
                        return True
                WBXTFLogWarning("wbxtfResourceMgr is not running on Machine:%s" % machine)
        return False
    except Exception, e:
        WBXTFLogError("Register Tool Info to ResAgent failed, exception info:%s" %e)
        return False