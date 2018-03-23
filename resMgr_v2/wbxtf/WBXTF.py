#!/usr/bin/python
##################################################################
##
## Library for WBXTF by STAF
##
#################################################################
'''
    This is a foundation module for WBXTF        
    
    @version: 1.0.0
    @copyright: WebEx
'''
import time
import sys
import types
import os
from threading import Thread
import threading
from WBXTFLog import *
from WBXTFCase import *
from WBXTFUtil import *
from WBXTFActionPool import *
from WBXTFError import *
from WBXTFService import *
from WBXTFSysInfo import *

try:
    import cPickle as pickle
except ImportError:
    import pickle


WBXTF_PROT_STAF = "staf"
WBXTF_PROT_WBXTF = "wbxtf"
def WBXTFGetProt():
    return WBXTF_PROT_WBXTF

if(WBXTFGetProt()==WBXTF_PROT_STAF):
    import PySTAF
else:
    from WBXTFCORBA import * #from WBXTFCORBA import * #Disable WBXTFCORBA for the current version
from WBXTFCallBack import *


##################################################################
##
## Config
##
#################################################################
global __gConfigSystem
__gConfigSystem = {}
def WBXTFSysConfig(name, value):
    """
    Set the system config    
    
    @type name: string
    @type name: the key of the setting
    @type value: any object
    @param value: any object
    @rtype:  any object
    @return: the old setting  
    @author: Shaun  
    """    
    global __gConfigSystem
    old = None
    if __gConfigSystem.has_key(name):
        old = __gConfigSystem[name]
    __gConfigSystem[name] = value
    return old 
    
def WBXTFGetSysConfig(name, default = None):
    """
    get the system config    
    
    @type name: string
    @param name: the key of the setting
    @type name: any
    @param name: the default value    
    @rtype: any
    @return: the value or the default value
    @author: Shaun  
    """      
    global __gConfigSystem
    if __gConfigSystem.has_key(name):
        return __gConfigSystem[name]
    else:
        return default
 
WBXTF_SYS_CONFIG_STRINGRESULT = "sys.config.stringResult"   
WBXTF_SYS_CONFIG_DEBUG        = "sys.config.debug"
WBXTF_SYS_CONFIG_WBXTFEX_VERSION       = "sys.config.wbxtfex.version"
WBXTF_SYS_CONFIG_REQUEST_POOL_MAX      = "sys.config.request.pool.max"
WBXTF_SYS_CONFIG_REQUEST_COMPOUND_OBJECTS_MAX    = "sys.config.request.compound.obj.max"
WBXTF_SYS_CONFIG_TOOLOBJECT_TIMEOUT = "sys.config.toolobject.timeout"

WBXTF_SYS_CONFIG_REQUEST_POOL_DEFAULT = 30 
WBXTF_SYS_CONFIG_REQUEST_COMPOUND_OBJECTS_DEFAULT = 100
WBXTF_SYS_CONFIG_TOOLOBJECT_TIMEOUT_DEFAULT = 60000

##################################################################
##
## Define
##
#################################################################
WBXTF_PROT_TYPE_NONE = 0
WBXTF_PROT_TYPE_STAF = 1
WBXTF_PROT_TYPE_WBXTF = 2

##################################################################
##
## VersionMgr
##
#################################################################
class WBXTFVersionMgr:
    __m_versionEvent = {}
    __m_versionDefaultBusiness = {}
    __m_lock = threading.Lock()    
    def getEventVersion(self, machine):
        self.__m_lock.acquire()
        if self.__m_versionEvent.has_key(machine):
            version = self.__m_versionEvent[machine]
            self.__m_lock.release()
            return version     
        version = WBXTFGetSysConfig(WBXTF_SYS_CONFIG_WBXTFEX_VERSION)        
        if version == None:        
            result = g_wbxtfSTAF.submit(machine, "WBXTFEX", "version()")
            if result["rc"] == 0 and result["result"] >= "1":
                version = result["result"]
            else:
                version = "0"            
        self.__m_versionEvent[machine] = version
        self.__m_lock.release()
        return version 
    
    def getDefaultBusinessVersion(self, machine):
        self.__m_lock.acquire()
        if self.__m_versionDefaultBusiness.has_key(machine):
            version = self.__m_versionDefaultBusiness[machine]
            self.__m_lock.release()
            return version
        
        version = WBXTFGetSysConfig(WBXTF_SYS_CONFIG_WBXTFEX_VERSION)        
        if version == None:        
            result = g_wbxtfSTAF.submit(machine, "WBXTFEX", "wbxtf.GetVersion")
            if result["rc"] == 0 and result["result"] >= "1":
                version = result["result"]
            else:
                version = "0"            
        self.__m_versionDefaultBusiness[machine] = version
        self.__m_lock.release()
        return version 
    
global g_versionMgr
g_versionMgr = WBXTFVersionMgr()
def WBXTFGetEventVersion(machine):
    return g_versionMgr.getEventVersion(machine)

def WBXTFGetDefaultBusinessVersion(machine):
    return g_versionMgr.getDefaultBusinessVersion(machine)

##################################################################
##
## WBXTFSTAF
##
#################################################################
def WBXTFMarshall(var):
    """
    marshal Python variable by STAF Text Format    
    
    @type var: any
    @param var: any object
    @rtype:  string
    @return: a string by using STAF Text Format  
    @author: Shaun  
    """
    return PySTAF.marshall(var)


def WBXTFFormatObject(obj):
    """
    format Python variable and return a formated text  
      
    @type obj: any
    @param obj: The source variable
    @rtype:  string
    @return: A format text  
    @author: Shaun  
    """
    return PySTAF.formatObject(obj)


class WBXTFSTAF:
    """
    Description: WBXTFSTAF wraps STAF 
    
    @author: Shaun
    @date: 2008/07/15
    """    
    m_perf = None
    def __init__(self, name="Test"):
        #self.m_perf = STAFPerformancePatch(self)
        self.name = name
        self.bHandle = 0
        self.m_lock = threading.Lock()             
             
    def __createHandle(self, bForce = False):
        self.m_lock.acquire()
        if self.bHandle == 0 or bForce:
            try:
                self.handle = PySTAF.STAFHandle(self.name)
                self.bHandle = 1
            except PySTAF.STAFException, e:
                sys.stderr.write("Error registering with STAF, RC: %d\n" % e.rc)
                self.bHandle = 0
        self.m_lock.release() 

    def submit(self, machine, service, request):
        """
        Submit a STAF request and return the request    
        
        @type machine: string
        @param machine: the target machine
        @type service: string
        @param service: STAF service name
        @type request: string
        @param request: STAF request  
        @rtype:  map
        @return: the return is a map, it includes "rc" and "result"
                And the "result" item includes the actual result
                "rc" item = 0 means success
        @author: Shaun  
        """        
        if self.m_perf != None:
            self.m_perf.optimizeMachine(machine)
        return self.do_submit(machine, service, request)
                                    
    def do_submit(self, machine, service, request):
        self.__createHandle()
        try:
            result = self.handle.submit(machine, service, request)
            if result.rc == 5: # The handle does not exist and try again
                self.__createHandle(True)
                result = self.handle.submit(machine, service, request)
            res = {}
            res["rc"] = result.rc;
            res["result"] = PySTAF.unmarshall(result.result).getRootObject() 
        except Exception, e:
            self.bHandle = 0
            res = {}
            res["rc"] = 1;
            res["result"] = None;
        return res

if(WBXTFGetProt()==WBXTF_PROT_STAF):
    global g_wbxtfSTAF
    g_wbxtfSTAF = WBXTFSTAF()
else:
    global g_WBXTFCORBA
    g_WBXTFCORBA = WBXTFCORBA()

def InitGlobalSTAF():
    g_wbxtfSTAF.createHanlde()

def WBXTFVAR(var):
    """
    Description: same to WBXTFVar 
    @see: WBXTFVar
    """
    return WBXTFVar(var)


def WBXTFVar(var):
    """
    Convert a variable to a WBXTF format
    If you want to pass a complex variable to WBXTF Tool, 
    please format your python variable by using the function
        >>> var = {'name':'Tom', 'age': 19}
        obj = WBXTF.WBXTFObject("staf://local/tool.Test.Info")
        obj.Execute("Register(%s)" % WBXTF.WBXTFVar(var)
        
    @type var: any
    @param var: the source object  
    @author: Shaun
    @date: 2008/07/15   
    """   
    sText = ""
    if type(var) == types.StringType:        
        sText = var.replace("`", "``")
        sText = sText.replace('"', '`"')
        sText = '"%s"' % (sText)
#        sText = '"%s"' % (var)
    elif type(var) == type(True) and type(var) != types.IntType:
        if var:     
            sText = '__TYPE:BOOL__1'
        else:
            sText = '__TYPE:BOOL__0'        
    elif type(var) == types.ListType or type(var) == types.TupleType:
        sText = "("
        nCount = 0
        for item in var:
            if nCount > 0:
                sText = sText + ", "            
            sText = sText + WBXTFVAR(item)
            nCount = nCount + 1            
        sText = sText + ")"
    elif type(var) == types.DictType:
        sText = '{'
        nCount = 0
        for k,v in var.items():
            if nCount > 0:
                sText = sText + ", " 
            sText = sText + WBXTFVAR(k)
            sText = sText + ":"
            sText = sText + WBXTFVAR(v)   
            nCount = nCount + 1 
        sText = sText + '}'
    elif type(var) == types.UnicodeType:
        sData = ""
        for chr in var:
            item = ord(chr)
            tmp = '%04X' % item
            tmp = WBXTFFormatUnicodeByte(tmp)
            sData = sData + tmp
        sText = "__TYPE:UNICODE__"+sData
        #sText = sText + WBXTFVar2DefaultResultFormat(var)
    else:
        sText = '%s' % (var)        
    return sText
    
##################################################################
##
## WBXTFObject
##
#################################################################
class WBXTFObject:
    __m_eventVersion = None
    """
    WBXTFObject is bound to a remote WBXTF object
        >>> import WBXTF
        myObj = WBXTF.WBXTFObject("staf://local/tool")
        print myObj.Execute("WBXTFGetSubObjs()")
        
    @author: Shaun
    @date: 2008/07/15
    """    
    def setEventVersion(self, version):
        self.__m_eventVersion = version
        
    def __partition(self, sText, sSep):
        """
        This is for python2.2  
        """   
        res = []
        nPos = sText.find(sSep)
        if nPos >= 0:
            res.append(sText[0:nPos])
            res.append(sSep)
            res.append(sText[nPos + len(sSep):])
        else:
            res.append(sText)
            res.append('')
            res.append('')
        return res        
        
    def __init__(self, url, bselfobject = 0):
        self.m_param = {}
        global g_wbxtfSTAF
        self.__m_name = url
        self.__m_eventVersion = None
        self.url = url
        self.__m_type = 0
        # Parse the url
        nPort = 0
        sProt ="staf"
        sMachine = "local"
        sObject = ""
        sURL = url
        # Parse Protocol
        sParts = self.__partition(sURL, "://")
        if len(sParts[1]):
            sProt = sParts[0]
            sURL = sParts[2]
        else:
            sURL = sParts[0]            
        # Parse Machine
        sParts = self.__partition(sURL, "/")
        sMachine = sParts[0]        
        sURL = sParts[2]
        sObject = sURL        
        # Parse Port
        #Add to support IPv6 Address
        if len(sMachine.split(":"))>2:#IPv6 Address
            if sMachine[0] == "[":
                #now can't specify port,we will solve it later             
                #nPort = int(sMachine[sMachine.index("]:")+2:])
                sMachine = sMachine[sMachine.index("[")+1:sMachine.index("]")]
        #Add end
        else:
            sParts = self.__partition(sMachine, ":")
            sMachine = sParts[0]
            if len(sParts[2]) > 0:
                nPort = int(sParts[2])
        
        self.sMachine = sMachine
        self.sObject = sObject
        self.sProt = sProt
        self.nPort = nPort
        self.bselfobject = bselfobject
        if self.sProt == "staf":
            self.__m_type = WBXTF_PROT_TYPE_STAF
        else:
            self.__m_type = WBXTF_PROT_TYPE_WBXTF
        if(self.bselfobject):
            if self.sProt == "staf":
                self.wbxtfObj = WBXTFSTAF()
            else:
                self.wbxtfObj = WBXTFCORBA()
        else:
            if self.sProt == "staf":
                self.wbxtfObj = g_wbxtfSTAF
            else:
                self.wbxtfObj = g_WBXTFCORBA                
        self.setKeyValue("machine",sMachine)
        self.setKeyValue("objUrl",url)
        self.m_name = ""

    def dumpToString(self):
        self.wbxtfObj.destroy()
        self.wbxtfObj.dll = None
        return pickle.dumps(self)


    def getAllParam(self):
        return self.m_param
    
    def setAllParam(self,param):
        self.m_param = param

    def addParam(self,param):
        for key in param.keys():
            self.m_param[key] = param[key]
                
    
    def setKeyValue(self,key,value):
        self.m_param[key] = value
        
    def getKeyValue(self,key):
        if(self.m_param.has_key(key)):
            return self.m_param[key]
        return None

    def setName(self,name):
        """
        set the name of this tool object
        @type name: string
        @param name:the name of the object
        @rtype:  None
        @return: None
        """         
        self.m_name = name
        
    def getName(self):
        return self.m_name
    
    def Execute(self, request):
        """
        Execute a command to the remote object 
            >>> Example:
            import WBXTF
            myObj = WBXTF.WBXTFObject("staf://local/tool")
            print myObj.Execute("WBXTFGetSubObjs()")
            print myObj.Execute("demo.WBXTFGetSubObjs()")
            print myObj.Execute("demo.math.Add(1, 2)")            
        
        @type request: string
        @param request: the command  
        @rtype:  map
        @return: the return is a map, it includes "rc" and "result"
                And the "result" item includes the actual result
                "rc" item = 0 means success
        """    
        if self.__m_type == WBXTF_PROT_TYPE_STAF:    
            if self.__getEventVersion() == "0": 
                return self.__ExecuteOldEvent(request) 
            else:
                return self.__ExecuteNewEvent(request)
        else:
            return self.__ExecuteByCORBA(request)
        
    def __ExecuteByCORBA(self, request): 
        sCommand = self.sObject
        if len(sCommand) > 0:
            sCommand += "."
        sCommand += request
        return self.wbxtfObj.execute(self.sMachine, sCommand)                
    
    def __ExecuteOldEvent(self, request):
        """
        Execute a command to the remote object 
            >>> Example:
            import WBXTF
            myObj = WBXTF.WBXTFObject("staf://local/tool")
            print myObj.Execute("WBXTFGetSubObjs()")
            print myObj.Execute("demo.WBXTFGetSubObjs()")
            print myObj.Execute("demo.math.Add(1, 2)")            
        
        @type request: string
        @param request: the command  
        @rtype:  map
        @return: the return is a map, it includes "rc" and "result"
                And the "result" item includes the actual result
                "rc" item = 0 means success
        """          
        if self.nPort == 0:
            sRequest = self.__GenerateRequest(request)
            result = self.wbxtfObj.submit(self.sMachine, "WBXTFEX", sRequest)
        else:
            sTmpRequest = self.__GenerateRequest(request)
            timeout = WBXTFGetSysConfig(WBXTF_SYS_CONFIG_TOOLOBJECT_TIMEOUT, WBXTF_SYS_CONFIG_TOOLOBJECT_TIMEOUT_DEFAULT)
            if timeout == 0:
                timeout = ''
            sRequest = "SEND HANDLE %s WAIT %s COMMAND \"%s\"" % (self.nPort, timeout, sTmpRequest)
            result = self.wbxtfObj.submit(self.sMachine, "WBXTFEvent", sRequest)
            if result["rc"] == 0:
                try:
                    res1 = result["result"]["results"][0]["sresult"]
                    res2 = result["result"]["results"][0]["hresult"]
                    result = {}
                    result["rc"] = int(res2)
                    result["result"] = res1
                except Exception:
                    result["rc"] = -2147483647
        return result   
    
    def __ExecuteNewEvent(self, request):
        """
        Execute a command to the remote object 
            >>> Example:
            import WBXTF
            myObj = WBXTF.WBXTFObject("staf://local/tool")
            print myObj.Execute("WBXTFGetSubObjs()")
            print myObj.Execute("demo.WBXTFGetSubObjs()")
            print myObj.Execute("demo.math.Add(1, 2)")            
        
        @type request: string
        @param request: the command  
        @rtype:  map
        @return: the return is a map, it includes "rc" and "result"
                And the "result" item includes the actual result
                "rc" item = 0 means success
        """ 
        sRequest = self.__GenerateRequest(request)
        sRequest = WBXTFEncodeDefault(sRequest)      
        if self.nPort == 0:            
            sNewRequest = "sendex("
            sNewRequest = sNewRequest + sRequest
            sNewRequest = sNewRequest +', {"encode":"default", "resultformat":"default"})' 
            result = self.wbxtfObj.submit(self.sMachine, "WBXTFEX", sNewRequest)
        else:            
            timeout = WBXTFGetSysConfig(WBXTF_SYS_CONFIG_TOOLOBJECT_TIMEOUT, WBXTF_SYS_CONFIG_TOOLOBJECT_TIMEOUT_DEFAULT)
            if timeout == 0:
                timeout = ''
            sNewRequest = "SEND HANDLE %s WAIT %s VAR encode=default VAR resultformat=default COMMAND \"%s\"" % (self.nPort, timeout, sRequest)
#            print sNewRequest
            result = self.wbxtfObj.submit(self.sMachine, "WBXTFEvent", sNewRequest)
            #print result
            if result["rc"] == 0:
                try:
                    res1 = result["result"]["results"][0]["sresult"]
                    res2 = result["result"]["results"][0]["hresult"]
                    result = {}
                    result["rc"] = int(res2)
                    result["result"] = res1
                except Exception, e:                 
                    result["result"] = "fail to parse the result: %s" % (result)
                    result["rc"] = -2147483647
                    return result
        if result.has_key('result'):
            res = WBXTFDecodeDefault(result['result'])
            if WBXTFGetSysConfig(WBXTF_SYS_CONFIG_STRINGRESULT) == True:
                result['result'] = WBXTFConvert2OldVar(WBXTFDefaultResultFormat2Var(res))
            else:
                result['result'] = WBXTFDefaultResultFormat2Var(res)
            
 #       print result
 #       print "========================"
        return result   

    def __GenerateRequest(self,request):
        sRequest = self.sObject
        if len(sRequest):
            sRequest += "."
        sRequest += request
        return sRequest

    def GetURI(self):
        """
        return the URI of the object 
        @rtype:  string
        @return: The format of URI is "<protocol>:<machine>/<obj>.<obj>" 
        """         
        return self.url

    def Attach(self, obj):
        """
        Attach to a new object 
        @rtype:  none
        """             
        self.__init__(obj.GetURI())
        
    def __getEventVersion(self):
        if self.__m_eventVersion != None:
            return self.__m_eventVersion
        self.__m_eventVersion = WBXTFGetEventVersion(self.sMachine)
        return self.__m_eventVersion        
         
    def __getattr__(self, name):
        if len(name) > 1 and name[0:2] == "__":
            raise AttributeError        
        newname = self.__m_name
        if newname[-1:] != "/":
            nPos = newname.find("//")
            if nPos < 0:
                #newname = "staf://local/"
                newname = "%s://local/" %(WBXTF.WBXTFGetProt())
            else:
                nPos = newname.find("/", nPos + 2)
                if nPos < 0:
                    newname = newname + "/"
                else:
                    newname = newname + "."
        newname = newname + name
        other = WBXTFObject(newname, self.bselfobject)
        other.setEventVersion(self.__m_eventVersion)
        return other        
       
    def __call__(self, *args):
        nPos1 = self.__m_name.rfind(".")
        nPos2 = self.__m_name.rfind("/")
        nPos = nPos1
        if nPos2 > nPos:
            nPos = nPos2
        if nPos < 0:
            return None
        strObj = self.__m_name[0:nPos]
        strMethod = self.__m_name[nPos + 1:]
        obj = WBXTFObject(strObj, self.bselfobject)
        obj.setEventVersion(self.__m_eventVersion)             
        request = strMethod
        request += WBXTF.WBXTFVar(args) 
        return obj.Execute(request)   
    
    
#    def __str__(self):   
#        return self.url
 
#    def __repr__(self):
#        return self.url 
    
    def __eq__(self, other):
        if isinstance(other, WBXTFObject):        
            return self.url == other.url
        else:
            return False
        
    def __ne__(self, other):
        if isinstance(other, WBXTFObject):        
            return self.url != other.url
        else:
            return True   

class WBXTFRequestThreadPool: 
    def __init__(self, max_thread_num = 0, timeout = None):
        if max_thread_num <= 0:
            max_thread_num = WBXTFGetSysConfig(WBXTF_SYS_CONFIG_REQUEST_POOL_MAX,
                                               WBXTF_SYS_CONFIG_REQUEST_POOL_DEFAULT)
        self.m_actionPool = WBXTFActionPool(max_thread_num)
        self.m_lock = threading.RLock()
        self.m_requests = {}
        self.timeout = timeout
        
    def cancel(self, timeout = None):      
        res = self.m_actionPool.cancel(timeout)
        self.m_lock.acquire()
        self.m_requests = {}
        self.m_lock.release()
                    
    def pushRequest(self, obj, command):
        id = self.m_actionPool.putAction(None, obj.Execute, command) 
        if id == 0:
            return id
        self.m_lock.acquire()
        request = {}
        request["id"] = id
        request["obj"] = obj
        request["command"] = command
        self.m_requests[id] = request
        self.m_lock.release()
        return id 
        
    def getResult(self, id):
        self.m_lock.acquire()
        result = None
        if self.m_requests.has_key(id):
           resActionPool = self.m_actionPool.getResult(id)
           if result['rc'] == 0:
               result = {}
               result['command'] = self.m_requests[id]['command']
               result['obj'] = self.m_requests[id]['obj']
               result['result'] = resActionPool['result']
               self.m_requests.pop(id)
        self.m_lock.release()
        return result
    
    def waitResult(self, id, timeout = None):
        self.m_lock.acquire()
        result = None
        if self.m_requests.has_key(id):
           resActionPool = self.m_actionPool.waitResult(id, timeout)
           if resActionPool['rc'] == 0:
               result = {}
               result['command'] = self.m_requests[id]['command']
               result['obj'] = self.m_requests[id]['obj']               
               result['result'] = resActionPool['result']
               self.m_requests.pop(id)
        self.m_lock.release()
        return result   
    
    def setMaxThreadCount(self, num):
        self.m_actionPool.setMaxThreadCount(num) 
             
##################################################################
##
## WBXTFObjectGroup
##
#################################################################
modeOGAuto = 1
modeOGThread = 2
modeOGStep = 3
modeOGCompound = 4
modeOGBatch = 5
modeOGDefault = modeOGAuto

class WBXTFExecutor:
    def __init__(self, mode = modeOGDefault):
        self.m_mode = mode
        self.__m_nTimeout = None
        self.__m_nMaxThread = WBXTF_SYS_CONFIG_REQUEST_POOL_DEFAULT
        self.__m_nMaxCompoundObjects = WBXTF_SYS_CONFIG_REQUEST_COMPOUND_OBJECTS_DEFAULT
        self.__m_nNumberPerBatch = 0
        self.__m_nInterval =  0
        
    def setTimeout(self, timeout):
        self.__m_nTimeout = timeout
        
    def setMode(self, mode):
        self.m_mode = mode
        
    def setMaxRequestThreads(self, num):
        self.__m_nMaxThread = num
        
    def setMaxCompoundObjects(self, num):
        self.__m_nMaxCompoundObjects = num
        
    def setBatch(self, numperbatch, interval):
        self.__m_nNumberPerBatch = numperbatch
        self.__m_nInterval =  interval
        
    def execute(self, commands):        
        if self.m_mode == modeOGStep:
            return self.__executeByStep(commands)
        elif self.m_mode == modeOGThread:
            return self.__executeByThreads(commands)
        elif self.m_mode == modeOGAuto and len(commands) <= 1:
            return self.__executeByStep(commands)
        elif self.m_mode == modeOGAuto:
            return self.__executeByCompound(commands)
        elif self.m_mode == modeOGCompound:
            return self.__executeByCompound(commands)
        elif self.m_mode == modeOGBatch:
            return self.__executeByBatch(commands)
        else:
            return self.__executeByStep(commands)
        
    def __executeByStep(self, commands):    
        ress = []
        for command in commands:
              res = {}   
              obj = command["object"]
              res["object"] = obj           
              res["result"] = obj.Execute(command['command'])
              ress.append(res)
        return ress 
    
    def __executeByBatch(self, commands):
        ress = []
        batchs = []        
        if self.__m_nNumberPerBatch > 0:
            groupByMachines = {}
            for command in commands:
                machine = command['object'].sMachine
                if not groupByMachines.has_key(machine):
                    groupByMachines[machine] = []
                groupByMachines[machine].append(command)
            num = 0
            index = 0
            batch = []
            while len(groupByMachines) > 0:
                for machine,item in groupByMachines.items():
                    if len(item) == 0:
                        del groupByMachines[machine]
                        break
                    batch.append(item[0])
                    del item[0]
                    index += 1
                    if index >= self.__m_nNumberPerBatch:                        
                        batchs.append(batch)
                        index = 0
                        batch = []            
            if len(batch) > 0:
                batchs.append(batch) 
        else:
            batchs.append(commands)
       
        index = 0
        for batch in batchs:
            executor = WBXTFExecutor()
            res = executor.execute(batch)
            for item in res:
                ress.append(item)
            index += 1
            if index != len(batchs):
                time.sleep(self.__m_nInterval)  
        return ress        
            
    def __executeByThreads(self, commands):
        requestPool = WBXTFRequestThreadPool()
        if self.__m_nMaxThread != None:
            requestPool.setMaxThreadCount(self.__m_nMaxThread)
        ress = []
        requests = []
        for cmd in commands:
            request = {}
            request["id"] = requestPool.pushRequest(cmd["object"], cmd["command"])
            request["obj"] = cmd["object"]
            requests.append(request)
            
        for request in requests:
            result = requestPool.waitResult(request["id"], self.__m_nTimeout)
            if result == None:              
              res = {}
              res["object"] = request["obj"]
              res["result"] = {'rc':E_TIMEOUT, 'result':'Timeout for execute'}
              ress.append(res)                
            else:
              res = {}
              res["object"] = result["obj"]
              res["result"] = result["result"]
              ress.append(res)    
        requestPool.cancel(0)    
        return ress

    def __executeByCompound(self, commands):
        requests = []
        results = []
        machineRequests = {}
        sProt = WBXTFGetProt()
        for cmd in commands:
            # Parse the object
            obj = cmd["object"]
            command = cmd["command"]
            if(sProt==WBXTF_PROT_STAF):
                if WBXTFGetDefaultBusinessVersion(obj.sMachine) < "1.1":
                    request = {}
                    request['obj'] = obj
                    request['type'] = 0
                    request['command'] = command
                    requests.append(request)
                    continue
            else:
                request = {}
                request['obj'] = obj
                request['type'] = 0 
                request['command'] = command 
            if not machineRequests.has_key(obj.sMachine):
                machineRequests[obj.sMachine] = []
            request = {}
            request['obj'] = obj
            request['type'] = 0 
            request['command'] = command           
            machineRequests[obj.sMachine].append(request)
            
        for machine, reqs in machineRequests.items():            
            obj = WBXTF.WBXTFObject("%s://%s/wbxtf.command" % (sProt,machine))
            commands = []
            objs = []
            for request in reqs:
                sURL = request['obj'].url
                sObj = request['obj'].sObject
                sLastChr = ''
                if len(sURL) > 0:
                    sLastChr = sURL[len(sURL) - 1: len(sURL)]
                if len(sObj) > 0:              
                    cmd = '%s.%s' % (sURL, request['command'])
                elif sLastChr == '/':
                    cmd = '%s%s' % (sURL, request['command'])
                else:
                    cmd = '%s/%s' % (sURL, request['command'])   
                objs.append(request['obj'])
                nPos = cmd.find("(")
                if nPos < 0:
                    nPos = len(cmd)
                nNewPos = cmd.rfind("/", 0, nPos)                
                if nNewPos >= 0:
                    tail = cmd[nNewPos:]
                    head = cmd[0:nNewPos]
                    head = head.replace(machine, 'local')
                    cmd = head + tail 
                commands.append(cmd)
                
            nMaxObjectNum = self.__m_nMaxCompoundObjects            
            if  nMaxObjectNum == 0:        
                nMaxObjectNum = WBXTFGetSysConfig(WBXTF_SYS_CONFIG_REQUEST_COMPOUND_OBJECTS_MAX,
                                              WBXTF_SYS_CONFIG_REQUEST_COMPOUND_OBJECTS_DEFAULT)
            
            commandsGroup = []
            objsGroup = []
            nGroupID = 0
            nPosID = 0
            if nMaxObjectNum == 0 or nMaxObjectNum >= len(commands):
                commandsGroup.append(commands)
                objsGroup.append(objs)
            else:
                for index in range(len(commands)): 
                    if nPosID == nMaxObjectNum:
                        nPosID = 0
                        nGroupID = nGroupID + 1
                    if nPosID == 0:
                        commandsGroup.append([])
                        objsGroup.append([])
                    nPosID = nPosID + 1
                    commandsGroup[nGroupID].append(commands[index])
                    objsGroup[nGroupID].append(objs[index])            
            for index in range(len(commandsGroup)):                 
                request = {}
                request['obj'] = obj
                request['type'] = 1                               
                request['objs'] = objsGroup[index]
                request['command'] = 'SendMany(%s)' % WBXTFVar(commandsGroup[index]) 
                     
                requests.append(request)
        requestPool = WBXTFRequestThreadPool()
        if self.__m_nMaxThread != None:
            requestPool.setMaxThreadCount(self.__m_nMaxThread)
            
        for request in requests: 
              request["id"] = requestPool.pushRequest(request["obj"],
                                                     request["command"])      
        for request in requests: 
            res = requestPool.waitResult(request["id"], self.__m_nTimeout)    
            if res == None:
                continue                   
            if request["type"] == 1:
                rcTotal = res["result"]["rc"]
                resultItem = None
                index = 0                   
                for obj in request["objs"]:
                    result = {}
                    result["object"] = obj
                    rc = rcTotal
                    if rc == 0:
                        rc = E_ERROR
                        resultItem = None                
                        if type(res["result"]["result"]) == types.ListType and index < len(res["result"]["result"]):
                            if type(res["result"]["result"][index]) == types.DictType:
                                if res["result"]["result"][index].has_key("hresult"):    
                                    rc = int(res["result"]["result"][index]["hresult"])
                                if res["result"]["result"][index].has_key("result"):
                                    resultItem = res["result"]["result"][index]["result"]                            
                    tmp = {}
                    tmp['rc'] = rc
                    tmp['result'] = resultItem
                    result["result"] = tmp                         
                    results.append(result)  
                    index = index + 1   
            else:
                result = {}
                result["object"] = request["obj"]
                result["result"] = res["result"]
                results.append(result)
        requestPool.cancel(0)        
        return results

def WBXTFRE(key,reType="wbxtf"):
    str = "@WBXTFREHead:%s:%s@WBXTFREEnd"%(reType,key)
    return str


class WBXTFObjectGroup(WBXTFExecutor): 
    def __init__(self, name = "", mode = modeOGDefault):
        self.m_objs = []
        WBXTFExecutor.__init__(self, mode)
        self.m_name = name 
        
    def setName(self, name):
        self.m_name = name        
    
    def getName(self):
        return self.m_name
        
    def add(self, obj, bAllowRepeat = False):
        if not bAllowRepeat:
            self.remove(obj)        
        self.m_objs.append(obj)
           
    def addList(self, objList, bAllowRepeat = False):
        for obj in objList:
            self.add(obj, bAllowRepeat)     
    
    def remove(self, obj):
        if obj in self.m_objs:
            self.m_objs.remove(obj)
    
    def clear(self):
        self.m_objs = []
        
    def isExist(self, obj):
        return obj in self.m_objs
    
    def getCount(self):
        return len(self.m_objs)
    
    def getObject(self, index):
        return self.m_objs[index]
    
    def execute(self, command):
        commands = []
        for obj in self.m_objs:
            item = {}
            item['object'] = obj
            item['command'] = command
            commands.append(item)
        ress = WBXTFExecutor.execute(self, commands)        
        return ress

    def __getWBXTFRECommand(self,obj,command):
        index = command.find("@WBXTFREHead:")
        if(index<0):
            return command
        else:
            strBegin = command[0:index]
            strTemp = command[index+len("@WBXTFREHead:"):]
            indexType = strTemp.find(":")
            REType = strTemp[0:indexType]
            strTemp = strTemp[indexType+len(":"):]
            indexEnd = strTemp.find("@WBXTFREEnd")
            if(indexEnd<0):
                return command
            key = strTemp[0:indexEnd]
            strEnd = strTemp[indexEnd+len("@WBXTFREEnd"):]
            if(REType=="wbxtf"):
                strCommand = strBegin+WBXTFVar(obj.getKeyValue(key))+self.__getWBXTFRECommand(obj,strEnd)
            else:
                strCommand = strBegin+self.onREEncode(obj.getKeyValue(key))+self.__getWBXTFRECommand(obj,strEnd)
            return strCommand

    def onREEncode(self,param):
        return WBXTFVar(param)
    
    def executeRE(self, command):
        commands = []
        for obj in self.m_objs:
            item = {}
            item['object'] = obj
            item['command'] = self.__getWBXTFRECommand(obj,command)
            commands.append(item)
        ress = WBXTFExecutor.execute(self, commands)        
        return ress
    
    def copyFrom(self, other):
        if type(self) != type(other):
            return False 
        self.m_objs = list(other.m_objs)


    def __add__(self, other):
        new = WBXTFObjectGroup(self.__m_nMaxThreads)
        new.copyFrom(self)
        for item in other.m_objs:
            if new.isExist(item):
                continue
            new.add(item)
        return new


    
    def __sub__(self, other):
        new = WBXTFObjectGroup()
        new.copyFrom(self)
        for item in other.m_objs:
            new.remove(item)
        return new
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        if len(self.m_objs) != len(other.m_objs):
            return False
        for item in self.m_objs:
            if not other.isExsit(item):
                return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __len__(self):
        return self.getCount()

##################################################################
##
## WBXTF Object Ex
##
#################################################################


        
##################################################################
##
## WBXTF Run
##
#################################################################
## Return ID
def WBXTFRun(sMachine, sPath, sParam, nNum, sExtend=""):
    """
    Run commands on a local/remote machine
        >>> Example - Start Notepad
        tools = WBXTFRun("local", "notepad", "", 1)
        if len(tools) == 1:
            print "Success"
        else:
            print "Failed"        
    
    @type sMachine: stringProt
    @param sMachine: the target machine
    @type sPath: string
    @param sPath: command path or command
    @type sParam: string
    @param nNum: integer
    @param nNum: the amount of the instances
    @rtype: list
    @return: If failed, run a empty list - []
             If success, run a list of handle ID.
    @see: WBXTFStop
    """
    sProt = WBXTFGetProt()
    objProcess = WBXTFObject("%s://%s/process" % (sProt,sMachine))
    res = objProcess.Execute("RunMany(%d,%s,%s,%s)" % (nNum, sPath, sParam,sExtend))
    result = []
    try:
        if res["rc"] == 0 and (not res["result"].has_key("RC")):
            result = res["result"]["Result"]
        else:
            WBXTFOutputError("Fail to run: %s" % (res))
    except Exception:
            WBXTFOutputError("Fail to run: %s" % (res))
            result = []             
    return result

##################################################################
##
## WBXTF Run and Wait
##
#################################################################
## Return ID
def WBXTFRunWait(sMachine, sPath, sParam = "", nTimeout = 60):
    """
    Run commands on a local/remote machine and wait it until end or timeout
        >>> Example - Start Notepad
        res = WBXTFRunWait("local", "notepad", "", 30)
        if res['rc'] == 0:
            print "Success"
        else:
            print "Failed"        
    
    @type sMachine: string
    @param sMachine: the target machine
    @type sPath: string
    @param sPath: command path or command
    @type sParam: string
    @param sParam: the arguments
    @param nTimeout: integer
    @param nTimeout: the timeout
    @rtype: a map, result
    @return: If failed, return the cause 
             If success, return the stdout
             If result['rc'] == 37, timeout
    @see: 
    """
    sProt = WBXTFGetProt()
    objProcess = WBXTFObject("%s://%s/process" % (sProt,sMachine))
    res=None
    if(sProt==WBXTF_PROT_STAF):
        res = objProcess.Execute('Run(%s,%s, "WAIT %s")' % (sPath, sParam, nTimeout * 1000))
    else:
        sExtend = {"WAIT":nTimeout*1000}
        res = objProcess.Execute('Run(%s,%s, %s)' % (sPath, sParam, sExtend))
    result = {}
    if res['rc'] != 0:
        return res
    if int(res['result']['RC']) == 0:
        result['rc'] = 0
        result['result'] = res['result']['Result']['fileList']
    else:
        result['rc'] = res['result']['RC']
        result['result'] = res['result']['Result']        
    return result


def WBXTFStop(sMachine, processes):
    """
    stop process
        >>> Example - Start Notepad and Stop it
        tools = WBXTFRun("local", "notepad", "", 1)
        if len(tools) == 1:
            print "Success"
            WBXTFStop("local", tools)
        else:
            print "Failed"      
    
    @type processes: list
    @param processes: the handle ID
    @rtype: None
    @return: None
    @see: WBXTFRun
    """
    sProt = WBXTFGetProt()
    objProcess = WBXTFObject("%s://%s/process" % (sProt,sMachine))
    for id in processes:
        res = objProcess.Execute("Stop(%s)" % (id))


def WBXTFRunObject(sMachine, sPath, sParam = '', timeout = 30,sExtend=""):   
    """
    Run a WBXTF tool and return a WBXTFCObject util it joins WBXTF or timeout
        >>> Example
        tools = WBXTFRunObject("local", "attendee.exe", "", 1)
        if tools == None:
            print "Failed"
        else:
            tools.Execute("meeting.Open")
                
    @type sMachine: string
    @param sMachine: the target machine
    @type sPath: string
    @param sPath: command path or command
    @type sParam: string
    @param timeout: float
    @param timeout: 
    @rtype: WBXTFCObject
    @return: If success, return a WBXTFCObject Object.
             If failed, return None.
    @see: WBXTFRunObjects
    """        
    res = WBXTFRun(sMachine, sPath, sParam, 1,sExtend)
    if len(res) != 1:
        return None
    sProt = WBXTFGetProt()
    if(sProt==WBXTF_PROT_STAF):
        obj = WBXTFObject("staf://%s:%s" % (sMachine, res[0]))
    else:
        obj = WBXTFObject("wbxtf://%s/tool.$%s" % (sMachine, res[0]))
    last = time.time()
    now = last
    bRes = False
    while(now - last <= timeout):
        resExist = obj.Execute("WBXTFGetTags()")
        if resExist['rc'] == 0:
            bRes = True
            break
        time.sleep(0.5)
        now = time.time()
    if bRes == False:
        WBXTFStop(sMachine, res)
        obj = None    
    return obj


def WBXTFRunObjects(sMachine, sPath, sParam, nNum, timeout = 60,sExtend=""):   
    """
    Run WBXTF tools and return WBXTFCObject objects util them joins WBXTF or timeout
        >>> Example
        tools = WBXTFRunObject("local", "attendee.exe", "", 1)
        if len(tools) == 0:
            print "Failed"
        else:
            tools.Execute("meeting.Open")
                
    @type sMachine: string
    @param sMachine: the target machine
    @type sPath: string
    @param sPath: command path or command
    @type sParam: string
    @type nNum: integer
    @param nNum: The number of tools  
    @param timeout: float
    @param timeout: 
    @rtype: list
    @return: If success, return a list of WBXTFCObject Objects.
             If failed, return [].
    @see: WBXTFRunObject
    """          
    group = WBXTFObjectGroup()
    res = WBXTFRun(sMachine, sPath, sParam, nNum,sExtend)
    if len(res) != nNum:
        return []
    objs = []
    sProt = WBXTFGetProt()
    if(sProt==WBXTF_PROT_STAF):
        for handle in res:
            obj = WBXTFObject("staf://%s:%s" % (sMachine, handle))
            objs.append(obj)     
            group.add(obj)
    else:
        for handle in res:
            obj = WBXTFObject("wbxtf://%s/tool.$%s" % (sMachine, handle))
            objs.append(obj)     
            group.add(obj)

    last = time.time()    
    now = last    
    bRes = False
    while(now - last <= timeout):         
        now = time.time()        
        ress = group.execute("WBXTFGetTags()")
        for  res in ress:
            if res['result']['rc'] == 0:
                group.remove(res['object'])
        if group.getCount() == 0:
            bRes = True
            break        
        time.sleep(0.5)        
               
    if bRes == False:
        WBXTFStop(sMachine, res)
        objs = []         
    return objs

def WBXTFKillObject(obj):  
    """
    Kill obejct
        >>> Example - Start Attendee and Kill it
        tool = WBXTFRunObject("local", "attendee.exe", "")
        tool != None:
            print "Success"
            WBXTFKillObject(tool)
        else:
            print "Failed"      
    
    @type objs: list
    @param objs: the objects who will be killed
    @rtype: None
    @return: None
    @see: WBXTFRun
    """
    sProt = WBXTFGetProt()
    if obj.nPort > 0: 
        objProcess = WBXTFObject("%s://%s/process" % (sProt,obj.sMachine))
        objProcess.Execute("Stop(%s)" % (obj.nPort))
        return True
    else:
        return False    

def WBXTFKillObjects(objs):  
    """
    Kill obejcts
        >>> Example - Start Attendee and Kill it
        tools = WBXTFRunObjects("local", "attendee.exe", "", 1)
        if len(tools) == 1:
            print "Success"
            WBXTFKillObjects(tools)
        else:
            print "Failed"      
    
    @type objs: list
    @param objs: the objects who will be killed
    @rtype: None
    @return: None
    @see: WBXTFRun
    """      
    requestPool = WBXTFRequestThreadPool()
    ress = []
    requests = []
    sProt = WBXTFGetProt()
    for obj in objs:
        if obj.nPort > 0: 
            objProcess = WBXTFObject("%s://%s/process" % (sProt,obj.sMachine))
            command = "Stop(%s)" % (obj.nPort)
            requests.append(requestPool.pushRequest(objProcess, command))                
    for request in requests:        
        res = requestPool.waitResult(request)            
        
    requestPool.cancel()
            
def WBXTFKillToolsOnMachine(machine):
    sProt = WBXTFGetProt()
    obj = WBXTF.WBXTFObject("%s://%s/process" % (sProt,machine))
    res = obj.StopAll()
    print res
    if res['rc'] == 0:
        return True
    else:
        return False

def WBXTFKillToolsOnMachines(machines):
    group = WBXTF.WBXTFObjectGroup()
    sProt = WBXTFGetProt()
    for machine in machines:
        obj = WBXTF.WBXTFObject("%s://%s/process" % (sProt,machine))
        group.add(obj)
    ress = group.execute("StopAll()")
    if len(ress) != len(machines):
        return False
    for res in ress:
        if res['result']['rc'] != 0:
            return False
    return True

def WBXTFRunObjectsOnMachines(rules, sPath, sParam, timeout = 60, bIgnoreFail = False,sExtend=""):   
    """
    Run WBXTF tools on machines and return WBXTFCObject objects util them joins WBXTF or timeout
        >>> Example
        rules = [{'machine':'local', 'num':1}]
        tools = WBXTFRunObject(rule, "attendee.exe", "", 1)
        if len(tools) == 0:
            print "Failed"
        else:
            tools.Execute("meeting.Open")
                
    @type rules: list
    @param rules: the rule of running tools. It is a list.
                  Every item must be map.
                  It includes the following keys:
                  machine - required, the machine name or IP
                  num     - required, the tools num
                  path    - optional, the path of the tool
                  param   - optional, the parameters of the tool                  
    @type sPath: string
    @param sPath: command path or command
    @type sParam: string 
    @param timeout: float
    @param timeout: 
    @rtype: list
    @return: If success, return a list of WBXTFCObject Objects.
             If failed, return [].
    @see: WBXTFRunObject
    """      
    # Check
    if type(rules) != types.ListType and type(rules) != types.TupleType: 
        return []
    # Start Tools
    requestPool = WBXTFRequestThreadPool()
    ress = []
    requests = []
    total = 0
    objs = []
    bRes = True
    sProt = WBXTFGetProt()
    for rule in rules:
        if type(rule) != types.DictionaryType and type(rule) != types.DictType:
            bRes = False
            break    
        if not rule.has_key('machine'):
            bRes = False
            break 
        if not rule.has_key('num'):
            bRes = False
            break         
        sToolPath = sPath
        sToolParam = sParam
        sToolMachine = rule['machine']
        nToolNum = rule['num']
        total = total + nToolNum
        if rule.has_key('path') and len(rule['path']) > 0:
            sToolPath = rule['path']
        if rule.has_key('param') and len(rule['param']) > 0:
            sToolParam = rule['param']
        objProcess = None
        command = ""   
        objProcess = WBXTFObject("%s://%s/process" % (sProt,sToolMachine))
        command = "RunMany(%d,%s,%s,%s)" % (nToolNum, sToolPath, sToolParam,sExtend)                
            
        request = {}
        request["num"] = nToolNum
        request["id"] = requestPool.pushRequest(objProcess, command)
        request["obj"] = objProcess
        request["machine"] = sToolMachine
        requests.append(request)    
        
    for request in requests:
        result = requestPool.waitResult(request["id"])
        num = 0  
        bRes = True
        if result != None:
            try:
                if result["result"]["rc"] == 0:               
                    for handle in result["result"]["result"]["Result"]:
                        if result["result"]["result"].has_key('RC') and result["result"]["result"]['RC'] != 0:
                            pass
                        else:
                            if(sProt==WBXTF_PROT_STAF):
                                obj = WBXTFObject("staf://%s:%s" %(request["machine"], handle))
                                objs.append(obj)
                            else:
                                obj = WBXTFObject("wbxtf://%s/tool.$%s"%(request["machine"], handle))
                                objs.append(obj)
                            num += 1
            except Exception, e:
                pass        
        if num != request["num"]:
            WBXTF.WBXTFWarning("Cannot run all tools on the machine %s, expect:%d, actual:%d"\
                                % (request["machine"], request["num"], num))
    requestPool.cancel() 
    
    if len(objs) == 0:
        return objs  

    # exit all if fails
    if len(objs) != total and bIgnoreFail == False:
        WBXTFKillObjects(objs)
        objs = [] 
        return objs       
    
    # Check the tools
    group = WBXTFObjectGroup()
    for obj in objs:    
        group.add(obj)             
        
    last = time.time()    
    now = last    
    bRes = False    
    times = 0
    while(now - last <= timeout):         
        now = time.time()        
        ress = group.execute("WBXTFGetTags()")
        for  res in ress:
            if res['result']['rc'] == 0:
                group.remove(res['object'])
        if group.getCount() == 0:
            bRes = True
            break        
        time.sleep(0.5)        
               
    if bRes == False:
        if bIgnoreFail == False:
            WBXTFKillObjects(objs)
            objs = []
        else:
            count = group.getCount()
            failMachines = {}
            for index in range(count):                
                obj = group.getObject(index)
                machine = obj.sMachine
                if not failMachines.has_key(machine):
                    failMachines[machine] = 1
                else:
                    failMachines[machine] += 1
                WBXTFKillObject(obj)                
                objs.remove(obj)   
            for machine,count in  failMachines.items():
                WBXTFWarning("%s tools fails in machine %s because cannot detect it" % (count, machine))                          
    return objs

##################################################################
##
## WBXTF Util
##
#################################################################
global __fun, __modeWBXTFError

modeIgnore     = "ignore" 
"""
When the module occur an error, the module ignores it.
"""

modeStop       = "stop"
"""
When the module occur an error, the script will stop
"""

modeException  = "exception"
"""
When the module occur an error, the module raises a WBXTFException exception 
"""

__funWBXTFError = {}
__modeWBXTFError = modeStop
#############################################
def WBXTFGetErrorMode():
    """
    Get the Error Mode
    The function is a global function 
    
    @rtype: string
    @return: modeIgnore - "ignore"
             modeStop - "stop"
             modeException - "exception"
    @see: WBXTFSetErrorMode
    """
    return __modeWBXTFError

def WBXTFSetErrorMode(mode):
    """
    Set the error mode
    @type mode: string
    @param mode: the error mode
                There are three mode:
                    modeIgnore - "ignore"
                    modeStop - "stop"
                    modeException - "exception"
                    
    @rtype: string
    @return: the old mode
    @see: WBXTFGetErrorMode
    """
    global __modeWBXTFError
    old = __modeWBXTFError
    __modeWBXTFError = mode
    return old

def WBXTFSetErrorFun(mode, fun):
    """
    Set the error function
    When the module occurs an error, the module will call the indicated function
    Every mode has itself function.
    
    @type mode: string
    @param mode: the error mode
    @type fun: function 
    @param fun: the callback function
    @rtype: function
    @return: the old function
    @see: WBXTFGetErrorFun    
    """
    global __funWBXTFError
    old = None
    if __funWBXTFError.has_key(mode):
        old = __funWBXTFError[mode]
    __funWBXTFError[mode] = fun
    return old

def WBXTFCallErrorFun(fun, exception):
    """
    Call the error function
    """
    if None == fun:
         return
    fun(exception)
    
def WBXTFGetErrorFun(mode = None):
    """
    get the error function    
    @type mode: string
    @param mode: the error mode
    @type fun: function 
    @param fun: the callback function
    @rtype: function
    @return: the function
    @see: WBXTFSetErrorFun    
    """
    old = None
    if mode != None:
        if __funWBXTFError.has_key(mode):
            old = __funWBXTFError[mode]
        return old
    else:
        return WBXTFGetErrorFun(WBXTFGetErrorMode())

   
#############################################
def WBXTFSetErrorModeAsIgnore():
    """
    Set the error mode as Ignore Mode
    
    @rtype: string
    @return: the old mode
    @see: WBXTFSetErrorMode
    """    
    return WBXTFSetErrorMode(modeIgnore)

def WBXTFSetErrorModeAsStop():
    """
    Set the error mode as Stop Mode
    
    @rtype: string
    @return: the old mode
    @see: WBXTFSetErrorMode
    """        
    return WBXTFSetErrorMode(modeStop)
    
def WBXTFSetErrorModeAsException():
    """
    Set the error mode as Exception Mode
    
    @rtype: string
    @return: the old mode
    @see: WBXTFSetErrorMode
    """        
    return WBXTFSetErrorMode(modeException)

#############################################
def WBXTFSetErrorFunAsIgnore(fun):
    """
    set the callback function of Error Mode  
    @return: the old function
    @see: WBXTFSetErrorFun    
    """    
    return WBXTFSetErrorFun(modeIgnore, fun) 

def WBXTFSetErrorFunAsStop(fun):
    """
    set the callback function of Stop Mode  
    @return: the old function
    @see: WBXTFSetErrorFun    
    """   
    return WBXTFSetErrorFun(modeStop, fun) 

def WBXTFSetErrorFunAsException(fun):
    """
    set the callback function of Exception Mode  
    @return: the old function
    @see: WBXTFSetErrorFun    
    """ 
    return WBXTFSetErrorFun(modeException, fun) 
   
##################################################################
##
## Report System
##
#################################################################
class WBXTFException(Exception):
    """
    Wrap WBXTF Exception  
    """
    def __init__(self, info = "", type = None):
        Exception.__init__(self, info)
        """
        @type info: string
        @param info: the exception information      
        """
        self.info = info
        self.type = type
        
    def GetInfo(self):
        """
        Get the exception information
        
        @rtype: string
        @return the exception information
        """
        return self.info
    
    def GetType(self):
        return self.type

  
global gInsideErrorFunction
gInsideErrorFunction = 0  
def WBXTFError(infoException, type = "", nExit = 1 , mode = None):
    """
    Call this function to indicate an error
    
    @type nExit: integer
    @param nExit: the exit code 
    @type mode: string
    @param mode: the error mode. If set it as None,
                use the global setting
    """     
    WBXTFOutputError(infoException)
    exInfo = WBXTF.WBXTFException(infoException, type)
    if mode == None:
        mode = WBXTF.WBXTFGetErrorMode()
    fun = WBXTF.WBXTFGetErrorFun()
    bPass = True
    if fun != None:
        global gInsideErrorFunction
        if gInsideErrorFunction == 0:
            gInsideErrorFunction = 1
            try:                          
                bPass = fun(exInfo)
            except Exception, e:
                WBXTFOutputWarning("Exception on the exception function, %s" % str(e))
            gInsideErrorFunction = 0
    if bPass != None and bPass == False:
        return        
    if mode == WBXTF.modeIgnore:
        pass
    elif mode == WBXTF.modeException:
        raise exInfo
    else:
        sys.exit(nExit)  
        
def WBXTFCheck(sText, bRes):
    """
    Verify the result.
    If the result is not passed, raise an error.
    
    @type bRes: bool
    @param bRes: Whether the result is passed.
    """      
    WBXTFOutputCheckPoint(sText, bRes)
    if not bRes:
        WBXTFError("Check Point (%s) Failed" % (sText)) 
        

class ITestEnv:
    """
    The interface for every kind of test env.
    """
    def __init__(self):
        pass
    
    def Create(self):
        pass
    
    def Destroy(self):
        pass

class ITestCase:
    """
    The interface for every test case.
    """
    m_Params = {};
    def __init__(self):
        pass
    
    def OnSetUp(self):
        pass
    
    def OnTearDown(self):
        pass
    
    def OnRun(self):        
        pass
    
    def OnError(self, exception):
        pass    
        
    def SetParam(self, name, value):
        self.m_Params[name] = value;
        
    def Run(self):
#        try:
            self.OnSetUp();
            self.OnRun();
            self.OnTearDown();
#        except Exception, e:
#            self.OnError(e)
#            print sys.exc_info()

    
#===============================================================================
#    for index in range(10000):
#        print index
#        group = WBXTFObjectGroup()
#        obj = WBXTF.WBXTFObject("staf://local/wbxtf.util")
#        group.add(obj)
#        group.add(obj, True)
#        group.setTimeout(0)    
#        group.execute("GetVersion")
#        #time.sleep(0.5)
#===============================================================================

    
