#!/usr/bin/python
###################################
##
###################################

import types
import sys
import time
import threading
import imp

global g_usingCtype
g_usingCtype = False

try:
    import ctypes
except Exception,e:
    pass
try:
    import PWBXTFCORBAClient
except Exception,e:
    pass


def checkPythonVersion():
    #print sys.version
    version = sys.version_info
    global g_usingCtype
    if((version[0]==2 and version[1]>=5) or version[0]>2):
        g_usingCtype = True
        #import ctypes
    else:
        g_usingCtype = False
        #import PWBXTFCORBAClient

def checkUsingCtype():
    global g_usingCtype
    return g_usingCtype

checkPythonVersion()

#################################
## Reserved
################################

#################################
## Setting
################################
WB_CONFIG_TIMEOUT = 360
WB_CONFIG_DEBUG = False

#################################
## Error
################################
WBRES_Error = -10
WBRES_NotObject = -11
WBRES_NotMethod = -12

WB_INFINIT  = sys.maxint

WB_VERSION = "1"
#################################
## Exception
################################
class WBException(Exception):
    m_code = -1
    m_description = ''
    def __init__(self, code, description = None):
        self.m_code = code
        if description == None:
            self.m_description = self.__GetDefaultDescript(code)
        else:
            self.m_description = description        
        self.message = self.m_description
        
    def GetCode(self):
        return self.m_code
    
    def GetDescription(self):
        return self.m_description
    
    def __GetDefaultDescript(self, code):
        if code == WBRES_NotObject:
            return "Not find object"
        elif code == WBRES_NotMethod:
            return "Not find method"
        return ""


#################################
## Filter 
################################
global __gSupportModule
__gSupportModule = {}

def supportModule(module):
    global __gSupportModule
    moduleID = id(module)
    __gSupportModule[moduleID] = True
        
def unSupportModule(module):
    global __gSupportModule
    moduleID = id(module)
    if __gSupportModule.has_key(moduleID):
        del __gSupportModule[moduleID]

def isSupportModule(module):
    moduleID = id(module)
    if __gSupportModule.has_key(moduleID):
        return __gSupportModule[moduleID]
    else:
        return False

def trace(log):
    if WB_CONFIG_DEBUG:
       print log
    
__gHideObjects = {}
def hideObject(obj):
    global __gHideObjects
    objID = id(obj)
    __gHideObjects[objID] = True
    
def showObject(obj):
    global __gHideObjects   
    objID = id(obj) 
    if __gHideObjects.has_key(objID):
        del __gHideObjects[objID]

def isHiddenObject(obj):
    global __gHideObjects  
    objID = id(obj) 
    if __gHideObjects.has_key(objID):
        return __gHideObjects[objID]
    else:
        return False  
    
def clearHiddenObject():    
     global __gHideObjects
     __gHideObjects.clear()

#################################
## The Delegate Object
################################
class WBDObject:
    m_object = None
    m_subObjs = {}
    m_methods = {}      
    def __init__(self, obj):
        self.m_object = obj
        self.__enum__()   
    
    def WBXTFGetSubObjs(self):
        objects = []
        for name,item in self.m_subObjs.items():
            obj = {}
            obj['name'] = name
            obj['subid'] = name
            obj['objid'] = name
            objects.append(obj)
        return objects     
    
    def WBXTFGetMethods(self):
        methods = []  
        methods.append(self.__GetFunction("WBXTFGetSubObjs"))
        methods.append(self.__GetFunction("WBXTFGetMethods"))
        methods.append(self.__GetFunction("WBXTFGetTags"))
        methods.append(self.__GetFunction("WBXTFGetStyle"))
        methods.append(self.__GetFunction("WBXTFGetClassID"))
        methods.append(self.__GetFunction("WBXTFGetItems"))
        for name,item in self.m_methods.items():
            method = {}
            method['method'] = name    
            method['return'] = 'python'
            sFunParam = ""
            if type(item['obj']) == types.FunctionType:
                for index in range(item['obj'].func_code.co_argcount):
                    if index >= len(item['obj'].func_code.co_varnames):
                                    break
                    if index > 0:
                        sFunParam = sFunParam + ", "
                    sFunParam = sFunParam + item['obj'].func_code.co_varnames[index]
            elif type(item['obj']) == types.MethodType:
                for index in range(item['obj'].im_func.func_code.co_argcount):
                    if index >= len(item['obj'].im_func.func_code.co_varnames):
                                    break
                    if index == 0:
                        continue
                    if index > 1:
                        sFunParam = sFunParam + ", "
                    sFunParam = sFunParam + item['obj'].im_func.func_code.co_varnames[index]
                        
            method['param'] = sFunParam
            method['class'] = 'WBXTFCPython'    
            methods.append(method)
        return methods   
    
    def WBXTFGetTags(self):
        return "python"
    
    def WBXTFGetStyle(self):
        return 0
    
    def WBXTFGetClassID(self):
        return "python"
    
    def WBXTFGetItems(self, nDeep = 0):
        nIndex = int(nDeep)
        res = {}
        res['methods'] = self.WBXTFGetMethods()
        res["style"] = self.WBXTFGetStyle()
        res["classid"] = self.WBXTFGetClassID()
        res["tags"] = self.WBXTFGetTags()
        subObjs = []
        for name, obj in self.m_subObjs.items():
            sub = {}
            sub['name'] = name
            sub['subid'] = name
            sub['objid'] = name
            obj = WBDObject(obj["obj"])
            if nIndex > 0:
                sub['items'] = obj.WBXTFGetItems(nIndex - 1)
            subObjs.append(sub)            
        res["subobjs"] = subObjs
        return res   
    
    def __GetFunction(self, name, res = "WBXTFValue"):
        method = {}
        method['method'] = name    
        method['return'] = res
        method['param'] = ''
        method['class'] = 'CWBXTFCBaseObject'
        return method  
    
    def Execute(self, command):
        nPosDot = command.find(".")
        nPosBracket = command.find("(")                 
        
        if nPosDot >= 0 and nPosBracket >= 0 and nPosBracket < nPosDot:
            nPosDot = -1
        if nPosDot >= 0:
            sObjName = command[0 : nPosDot]
            sNewCommand = command[nPosDot + 1:]
            trace("Object:%s" % sObjName)
            trace("Comamnd:%s" % sNewCommand)   
            objSub = self.__GetObj(sObjName)
            if objSub == None:
                raise WBException(WBRES_NotObject)
                return
            objDSub = WBDObject(objSub)
            return objDSub.Execute(sNewCommand) 
        else:
            trace("Method:%s" % command)    
            return self.__ExecuteMethod(command)
        
    def __enum__(self):        
        items = []
        self.m_subObjs = {}
        self.m_methods = {}
        if type(self.m_object) == types.DictType or type(self.m_object) == types.DictionaryType:
            for k,v in self.m_object.items():
                item = {}
                item['name'] = k
                item['obj'] = v
                items.append(item)     
        elif type(self.m_object) == types.ListType or type(self.m_object) == types.TupleType:
            index = 0
            for var in self.m_object:
                item = {}
                item['name'] = '%s' % index
                item['obj'] = self.m_object[index]
                items.append(item) 
                index = index + 1                               
        else: 
            subitems = dir(self.m_object)        
            for subitem in subitems:
                item = {}
                item['name'] = subitem
                item['obj'] = eval("self.m_object.%s" % (subitem))
                items.append(item)
        for item in items:
            if type(item['name']) != types.StringType or item['name'] == '' or item['name'][0] == '_':
                continue
            bMethod = False
            bSubObj = False
            if isHiddenObject(item['obj']):
                continue
                        
            if type(item['obj']) == types.FunctionType:                
                self.m_methods[item['name']] = item
            if type(item['obj']) == types.MethodType :
                self.m_methods[item['name']] = item
            elif type(item['obj']) == types.InstanceType: 
                self.m_subObjs[item['name']] = item
            elif type(item['obj']) == types.ModuleType and isSupportModule(item['obj']):
                self.m_subObjs[item['name']] = item
            elif type(item['obj']) == types.DictType or type(item['obj']) == types.DictionaryType:
                self.m_subObjs[item['name']] = item
            elif type(item['obj']) == types.ListType or type(item['obj']) == types.TupleType:
                self.m_subObjs[item['name']] = item
                
    def __strip(self, sText, sChar = "   "):
        nFirst = 0
        nLast = len(sText)
        for chr in sText:            
            if not chr in sChar:
                break
            nFirst = nFirst + 1
        for index in range(len(sText)):
            chr = sText[len(sText) - index - 1]
            if not chr in sChar:
                break
            nLast = nLast - 1
        return sText[nFirst:nLast]
    
    def __GetObj(self, name):
        name = self.__strip(name, '()[]{}<>     ')
        if self.m_subObjs.has_key(name):
            return self.m_subObjs[name]['obj']
        else:
            return None    
    
    def __ExecuteMethod(self, command):
        res = None
        if WB_CONFIG_DEBUG:
	        command = self.__ConvertCommand(command)		     
	        method = self.__GetMethodName(command)
	        param = self.__GetParamString(command)
	        if method[0:5] == 'WBXTF' and not self.m_methods.has_key(method):
	            res = eval("self.%s" % (command))
	            return res       
	        if type(self.m_object) != types.DictType:  
	            trace('self.m_object.%s' % command)
	            res = eval('self.m_object.%s' % command)
	        else:
	            res = eval('self.m_object["%s"]%s' % (method, param))    	
        else:
	        try:     
		        command = self.__ConvertCommand(command)
		     
		        method = self.__GetMethodName(command)
		        param = self.__GetParamString(command)
		        if method[0:5] == 'WBXTF' and not self.m_methods.has_key(method):
		            res = eval("self.%s" % (command))
		            return res       
		        if type(self.m_object) != types.DictType:  
		            trace('self.m_object.%s' % command)
		            res = eval('self.m_object.%s' % command)
		        else:
		            res = eval('self.m_object["%s"]%s' % (method, param))
	        except AttributeError, e:
	            trace(e.message)
	            raise WBException(WBRES_NotMethod)  
	        except Exception, e:
	            trace(e.message)
	            raise WBException(WBRES_Error, e.message)
        return res
    
    def __ConvertCommand(self, command):
        nPos = command.find("(")
        if nPos < 0:
            command = command + "()"
        nPos1 = command.find("(")
        nPos2 = command.rfind(")")
        params = command[nPos1: nPos2]
#        listParam = params.split(',')
        return command
    
    def __GetMethodName(self, command):
        method = command
        nPos = method.find("(")
        if nPos >= 0:
            method = method[0:nPos]
        return method  
    
    def __GetParamString(self, command):
        sParam = ""
        nPos = command.find("(")
        if nPos >= 0:
            sParam = command[nPos:]
        return sParam  

global __gRoot
__gRoot = None

def setRoot(root = globals()):
    global __gRoot
    __gRoot = root


class WBXTFConvertException(Exception):
    pass

class WBXTFInputStream:
    m_sText = ""
    m_nPos = 0
    def __init__(self, sText):
        self.m_sText = sText
       
    def setPos(self, nPos):
        self.m_nPos = nPos
       
    def getPos(self):
        return self.m_nPos
       
    def skipWhite(self):
        while self.m_nPos < len(self.m_sText):
            chr = self.m_sText[self.m_nPos]
            if chr != ' ' and chr != '\t' and chr != '\r':
                return
            self.m_nPos = self.m_nPos + 1
           
    def lookup(self):
        if self.m_nPos >= len(self.m_sText):
            return None
        return self.m_sText[self.m_nPos]
   
    def read(self, num = 0):
        if self.m_nPos + num > len(self.m_sText):
            return None
        if num == 0:           
            res = self.m_sText[self.m_nPos : ]
            self.m_nPos = len(self.m_sText)
            return res
        else:
            res = self.m_sText[self.m_nPos : self.m_nPos + num]
            self.m_nPos = self.m_nPos + num
            return res
       
    def readUtilChr(self, chrs, spec = None):
        bSpec = False
        pos = self.m_nPos
        value = ""
        last = pos    
        while pos < len(self.m_sText):
            if bSpec:               
                pos = pos + 1
                bSpec = False
                continue
            tmp = self.m_sText[pos]
            if tmp in chrs:              
                break
            elif tmp == spec:
                bSpec = True
                value = value + self.m_sText[last : pos]
                last = pos + 1         
            pos = pos + 1
        value = value + self.m_sText[last : pos]
        if pos > self.m_nPos:
            self.m_nPos = pos
        if len(value) == 0:
            return None
        return value 
    
class WBXTFConverter:
    m_stream = None
    def __init__(self):
        pass
           
    def convertVar2Text(self, var):
        text = ''
        if type(var) == types.StringType:
            text = '"' + var + '"'
        else:
            text = str(var)
        return text
    
    def convert2Var(self, command):
        self.m_stream = WBXTFInputStream(command)       
        res = self.__parseObject()
        return res     
       
    def __parseObject(self, sep = []):
        self.m_stream.skipWhite()
        chr = self.m_stream.lookup()
        oldPos = self.m_stream.getPos()
        try:
            if chr == '"':
                return self.__parseString(sep)
            elif chr == '(':
                return self.__parseList(sep)
            elif chr == '{':
                return self.__parseMap(sep)
            elif chr == None:
                return None           
        except WBXTFConvertException:
            self.m_stream.setPos(oldPos)       
        return self.__parseScale(sep)
       
    def __parseString(self, sep = []):
        start = self.m_stream.read(1)       
        value = self.m_stream.readUtilChr(['"'], '`')       
        end = self.m_stream.read(1) 
        length = 0
        if value != None:
            length = len(value)
        else:
            value = ""
        if start == '"' and end == '"':
            return value
        else:           
            newvalue = ""
            if start != None:
                newvalue = newvalue + start
            if value != None:
                newvalue = newvalue + value
            if end != None:
                newvalue = newvalue + end
            return newvalue
       
    def __parseScale(self, sep = []):
        value = self.m_stream.readUtilChr(sep)
        newdata = None
        try:
            newdata = eval(value)
        except Exception, e:
            if value != None:
                newdata = value.strip()
            else:
                newdata = None
        return newdata        
   
    def __parseList(self, sep = []):
        start = self.m_stream.read(1)
        res = []
        bAppend = False
        while True:
            obj = self.__parseObject([',',')'])
            self.m_stream.skipWhite()
            spec = self.m_stream.read(1)            
            if spec == ',':
                res.append(obj)
                bAppend = True
                continue
            elif spec == ')':
                if obj != None or bAppend:
                    res.append(obj)
                break
            else:
                raise WBXTFConvertException()
        return res        
       
    def __parseMap(self, sep = []):
        start = self.m_stream.read(1)
        res = {}
        bAppend = False
        while True:
            objKey = self.__parseObject([':'])
            chr = self.m_stream.read(1) 
            if chr != None:
                bAppend = True     
            objValue = self.__parseObject([',','}'])
            chr = self.m_stream.read(1)
            self.m_stream.skipWhite() 
            if chr == '}':
                if objKey != None or objValue != None or bAppend:
                    res[objKey] = objValue
                break
            elif chr == ',':
                bAppend = True
                res[objKey] = objValue
                continue
            else:
                raise WBXTFConvertException()               
        return res 

def __testConvertParam2Var(varParam, varExpect):
    converter = WBXTFConverter()
    varActual = converter.convert2Var(varParam)
    bRes = (varActual == varExpect)
    sCommand = ''
    if bRes:
        sCommand = '[PASS]'
    else:
        sCommand = '[FAIL]'
    sCommand = sCommand + 'Input:%s\t' % varParam
    sCommand = sCommand + 'Expert:%s\t' % varExpect
    sCommand = sCommand + 'Actual:%s\t\n' % str(varActual)
    if bRes:
        sys.stdout.write(sCommand)
    else:
        sys.stderr.write(sCommand)
  
        
def execute(command):
    trace('execute(%s)' % command)
    nPosBracket = command.find("(")
    # Replace the parameters
    if nPosBracket >= 0:
        param = command[nPosBracket:]
        converter = WBXTFConverter()
        var = converter.convert2Var(param)           
        param = converter.convertVar2Text(var)            
        if len(param) > 1 and param[0] == '[' and param[len(param) - 1] == ']':
            param = param[1:len(param) - 1]   
        command = command[:nPosBracket]
        command = command + "(" + param + ")"
    trace('convert to %s' % command)
    objRoot = WBDObject(__gRoot)     
    return objRoot.Execute(command)

def __formatWBXTFValue(var):
    sText = ""
    if type(var) == types.StringType:
        sText = '"%s"' % (var)
    elif type(var) == types.ListType or type(var) == types.TupleType:
        sText = "("
        nCount = 0
        for item in var:
            if nCount > 0:
                sText = sText + ", "            
            sText = sText + __formatWBXTFValue(item)
            nCount = nCount + 1            
        sText = sText + ")"
    elif type(var) == types.DictType:
        sText = '{'
        nCount = 0
        for k,v in var.items():
            if nCount > 0:
                sText = sText + ", " 
            sText = sText + __formatWBXTFValue(k)
            sText = sText + ":"
            sText = sText + __formatWBXTFValue(v)   
            nCount = nCount + 1 
        sText = sText + '}'
    else:
        sText = '%s' % (var)        
    return sText

def formatWBXTFValue(var):
    return __formatWBXTFValue(var)

def formatWBXTFValue2(var):
    sText = ""
    if type(var) == types.StringType:
        sText = '@WSH:text:%d@%s' % (len(var), var)
    elif type(var) == types.IntType:
        sData = '%s' % var
        sText = '@WSH:int:%d@%s' %(len(sData), sData)
    elif type(var) == types.LongType:
        sData = '%s' % var
        sText = '@WSH:int64:%d@%s' %(len(sData), sData)        
    elif sys.version > '2.3' and type(var) == types.BooleanType:
        if var:
            sData = '1'
        else:
            sData = '0'
        sText = '@WSH:bool:%d@%s' %(len(sData), sData)
    elif type(var) == types.FloatType:
        sData = '%s' % var
        sText = '@WSH:double:%d@%s' %(len(sData), sData)                    
    elif type(var) == types.ListType or type(var) == types.TupleType:
        sText = '@WSH:array:%d@' % (len(var))
        for item in var:
            sText = sText + formatWBXTFValue2(item)
    elif type(var) == types.DictType or type(var) == types.DictionaryType:        
        sText = '@WSH:map:%d@' % (len(var))
        for k,v in var.items():
            sData = '%s' %(k)
            sText = sText + '@WSH:item:%d@%s' % (len(sData), sData)
            sText = sText + formatWBXTFValue2(v) 
    else:
        sData = '%s' % (var)
        sText = '@WSH:text:%d@%s' % (len(sData), sData)  
    return sText


class ExecuteSepThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.m_result = ''
        self.m_command = None 
        self.m_bFinish = False
        self.m_event = threading.Event() 
        self.m_lock = threading.Lock()
        self.m_bCancel = False
        self.m_eventCommand = threading.Event()        
    
    def pushCommand(self, command):
        self.m_lock.acquire()
        self.m_command = command
        self.m_lock.release()        
        self.__setFinishStatus(False)
        self.m_eventCommand.set()
    
    def readCommand(self):
        self.m_lock.acquire()
        command = self.m_command
        self.m_command = None
        self.m_lock.release()
        return command
    
    def putResult(self, res):
        self.m_lock.acquire()
        self.m_result = res
        self.m_lock.release()        
        self.__setFinishStatus(True)
    
    def getResult(self):
        self.m_lock.acquire()
        res = self.m_result
        self.m_result = None
        self.m_lock.release()
        return res 
    
    def waitFinish(self, timeout):
        if self.isFinished():
            return True                
        nRes = self.m_event.wait(timeout)
        if nRes != None:
            return False        
        return self.isFinished()
    
    def waitResult(self, timeout):
        res = self.waitFinish(timeout)
        if res == False:
            return None
        else:
            return self.getResult()
    
    def __setFinishStatus(self, bFinish):
        self.m_lock.acquire()
        if bFinish:
            self.m_bFinish = True
            self.m_event.set()
        else:
            self.m_bFinish = False
            self.m_event.clear()
        self.m_lock.release()        
    
    def isFinished(self):
        self.m_lock.acquire()
        res = self.m_bFinish
        self.m_lock.release()
        return res    
    
    def cancel(self):
        self.m_bCancel = True
        self.m_eventCommand.set()
        
    def run(self):
        while True:
            command = self.readCommand()
            if command == None:
                self.m_eventCommand.wait()
                self.m_eventCommand.clear()
                if self.m_bCancel:
                    break
                else:
                    continue                            
            res = {}
            try:
                res['rc'] = 0;
                res['result'] = execute(command)
            except WBException, e:
                res['rc'] = e.GetCode()
                res['result'] = e.GetDescription()      
            except Exception, e:
                res['rc'] = WBRES_Error
                res['result'] = str(e)
            self.putResult(res)  
    
global __gExecuteThread
__gExecuteThread = None
global __gExecuteTimeout
__gExecuteTimeout = WB_CONFIG_TIMEOUT # MS

def executeByWBXTF(command):      
    if __gExecuteTimeout == 0:
        res = {}
        if WB_CONFIG_DEBUG:
            try:
                res['rc'] = 0;
                res['result'] = execute(command)
            except WBException, e:
                res['rc'] = e.GetCode()
                res['result'] = e.GetDescription()      
            except Exception, e:
                res['rc'] = WBRES_Error
                res['result'] = str(e)
        else:
             res['rc'] = 0;
             res['result'] = execute(command)           
        return formatWBXTFValue2(res)
    else:
        global __gExecuteThread
        if __gExecuteThread == None:
            __gExecuteThread = ExecuteSepThread()
            __gExecuteThread.start()
        __gExecuteThread.pushCommand(command)
        bFinish = __gExecuteThread.waitFinish(__gExecuteTimeout)
        res = None
        if bFinish == False: # Abort the thread if timeout
            __gExecuteThread.cancel()
            __gExecuteThread = None 
            res = {}
            res['rc'] = -1
            res['result'] = 'Timeout for execute %s' % (command)
            return formatWBXTFValue2(res)
        res = formatWBXTFValue2(__gExecuteThread.getResult())
        return res


    ##############################################################
class __WBXTFStringStream:
     __m_text = ""
     __m_pos = 0
     
     def __init__(self, text = ""):
         self.__m_text = text
         self.__m_pos = 0
         
     def read(self, num):
         nNextPos = self.__m_pos + num
         nFromPos = self.__m_pos
         if nNextPos > len(self.__m_text):
             nNextPos = len(self.__m_text)
         if nNextPos == self.__m_pos:
            return ''
         self.__m_pos = nNextPos
         res = self.__m_text[nFromPos : nNextPos]
         return res
     
     def readUtilText(self, flag):
         nPos = self.__m_text.find(flag, self.__m_pos)
         nFromPos = self.__m_pos
         if nPos < 0:
             self.__m_pos = len(self.__m_text) - 1
             if self.__m_pos < 0:
                 self.__m_pos = 0
             res = self.__m_text[nFromPos:]
             return res
         else:
             nPos = nPos
             self.__m_pos = nPos + 1
             res = self.__m_text[nFromPos:nPos]
             return res
     
     def seek(self, nPos):
         self.__m_pos = nPos  
     
     def getPos(self):
         return self.__m_pos
     
     def isEOF(self):
         if self.__m_pos >= len(self.__m_text):
             return True
         else:
             return False
            
def __WBXTFDefaultResultFormat2Var(stream):
    head = stream.readUtilText(':')
    if head != '@WSH':
        return head
    type = stream.readUtilText(':') 
    size = int(stream.readUtilText('@'))       
    if type == 'none':
        data = stream.read(size)
        return None
    elif type == 'int':
        data = stream.read(size)
        return int(data)
    elif type == 'int64':
    	data = stream.read(size)
    	return long(data)
    elif type == 'text':
        data = stream.read(size)
        return data 
    elif type == 'double':
        data = stream.read(size)      
        return float(data)     
    elif type == 'bool':
        data = stream.read(size)
        if data == '0':
            return False
        else:
            return True
    elif type == 'time':
        data = stream.read(size)     
        return data
    elif type == 'array':
        var = []
        for index in range(size):
            var.append(__WBXTFDefaultResultFormat2Var(stream))            
        return var
    elif type == 'map':
        var = {}
        for index in range(size):
            subhead = stream.readUtilText(':')
            if subhead != '@WSH':
                return var
            subtype = stream.readUtilText(':') 
            subsize = int(stream.readUtilText('@')) 
            if subtype != 'item':
                return var
            key = stream.read(subsize)
            var[key] = __WBXTFDefaultResultFormat2Var(stream)                               
        return var
    else:
       data = stream.read(size)
       return data 

def WBXTFDefaultResultFormat2Var(text):
    if type(text) != types.StringType:
        return text
    stream = __WBXTFStringStream(text)
    try:
        return __WBXTFDefaultResultFormat2Var(stream)
    except Exception,e:
        print "Warning:WBXTFDefaultResultFormat2Var:%s:%s" % (e, text)
    return ""



class WBXTFCORBA:
    __m_lock = threading.RLock()
    def __init__(self,name="Test"):
        self.m_handle = 0
        self.name = name
        self.m_bInit = False
        self.dll = None
        
    def __del__(self):
        self.destroy()
              
    def create(self):
        try:
            if(checkUsingCtype()):
                if self.dll !=None:
                    return True
                if sys.platform == "win32":
                    self.dll = ctypes.cdll.LoadLibrary("WBXTFCORBAClient.dll")
                elif sys.platform == "darwin":
                    self.dll = ctypes.cdll.LoadLibrary("WBXTFCORBAClient.dylib")
                else:
                    self.dll = ctypes.cdll.LoadLibrary("WBXTFCORBAClient.so")
                num = ctypes.c_uint()
                self.dll.WBXTFCreateClient(0,ctypes.byref(num),0)
                self.m_handle = num
                if self.m_handle <=0:
                    self.dll = None
                    return False
                else:
                    return True
            else:
                hr,handle = PWBXTFCORBAClient.WBXTFCreateClient(0)
                if(hr==0 and handle !=0):
                    self.m_handle = handle
                    self.m_bInit = True
                    return True
                else:
                    return False
        except Exception,e:
            print e
            return False
        
    def __createOnce(self):
        self.__m_lock.acquire()
        if(checkUsingCtype()):
            if self.dll ==None:    
                res = self.create()
                self.__m_lock.release()
                return False
            
            else:
                self.__m_lock.release()
                return True
        else:
            if self.m_bInit == False:
                res = self.create()
                self.__m_lock.release()
                return res
            else:
                self.__m_lock.release()
                return True
            
    def destroy(self):
        if(checkUsingCtype()):
            if self.dll != None:
                self.dll.WBXTFDestroyClient(self.m_handle)
                self.dll = None
        else:
            if self.m_bInit == False:
                return
            PWBXTFCORBAClient.WBXTFDestroyClient(self.m_handle)
        
        
    def execute(self, machine, command):
        self.__createOnce()
        if(checkUsingCtype()):
            if self.dll == None:
                return {'rc':-1,'result':None}
            hrRes = ctypes.c_long()
            sResult = ctypes.c_char_p() 
            hr = self.dll.WBXTFExecuteClient(self.m_handle,
                                            ctypes.c_char_p(machine),
                                            ctypes.c_char_p(command),
                                            0,
                                            ctypes.byref(sResult),
                                            0)
            result = {}
            if hr!=0:
                result['rc']= hr
                result['result'] =None
            else:
                result["rc"]= hrRes.value
                result["result"]= WBXTFDefaultResultFormat2Var(sResult.value)
            self.dll.WBXTFFreeResult(sResult)
            return result
        else:   
            if self.m_handle == 0:
                return {'rc':-1, 'result':None}
            hr, sResult = PWBXTFCORBAClient.WBXTFExecuteClient(self.m_handle,
                                                machine,command,"",0)
            result = {}
            if hr != 0:
                result['rc'] = hr
                result['result'] = None
            else:
                result["rc"] = hr
                result["result"] = WBXTFDefaultResultFormat2Var(sResult)
            #self.dll.WBXTFFreeResult(sResult)
            return result  
    
def __getHex(text):
    if len(text) != 2:
        return [False, 0]  
    total = 0  
    for index in range(len(text)):
        item = text[index]
        num = 0
        bValid = False
        if item >= 'a' and item <= 'f':
            bValid = True
            num = 10 + ord(item) - ord('a')
        elif item >= 'A' and item <= 'F': 
            bValid = True
            num = 10 + ord(item) - ord('A')            
        elif item >= '0' and item <= '9':
            bValid = True
            num = ord(item) - ord('0')
        if not bValid:
            return [False, 0] 
        total = total +  pow(16,(len(text) - index - 1)) * num
    return [True, total] 
    
def WBXTFDecodeDefault(var):
    if type(var) != types.StringType:
       return var   
    try:
        sNewVar = ''
        nLastPos = 0
        while nLastPos >= 0 and nLastPos < len(var):
            nFindPos = var.find('^', nLastPos)
            if nFindPos < 0:
                sNewVar = sNewVar + var[nLastPos:]
            else:
                sNewVar = sNewVar + var[nLastPos : nFindPos]
                hexvalue = var[nFindPos + 1 : nFindPos + 3]
                res = __getHex(hexvalue)
                if res[0] == False:
                    sNewVar = sNewVar + var[nFindPos : nFindPos + 3]
                else: 
                    item = chr(res[1])
                    sNewVar = sNewVar + item
                nFindPos = nFindPos + 3         
            nLastPos = nFindPos  
        return sNewVar
    except Exception:
        trace('Except at decode:%s' % (var))
        return var
    ##############################################################
    
class WBTool:
    m_WBXTFCorba = None
    m_sName = ""
    m_bRegister = False
    m_bCancelFlag = False
    def __init__(self, name,dependThreadName = "MainThread"):
        self.m_handle =0
        self.m_sName = name
        self.m_pid = self.__getPID()
        self.m_WBXTFCorba = WBXTFCORBA(self.m_sName)
        self.m_DependThreadName = dependThreadName
        pass
    
    def Register(self):
        if self.IsRegister():
            return
        self.__registerHandle()
        if(self.m_handle>0):
            self.m_bRegister = True

    def __registerHandle(self):
        sCmd = "handle.Register"
        sCmd += "(" + str(self.m_pid) +"," + self.m_sName +")"
        res = self.m_WBXTFCorba.execute("local",sCmd)
        if(res["rc"]==0 and res["result"]!=None):
            self.m_handle = int(res["result"])
        if(self.m_handle ==0 ):
            print "Register to WBXTF Failed."
            return #need exception???
        #print "tool handle is %d"%(self.m_handle)


    def __unRegisterHandle(self):
        if(self.m_handle<=0 or self.m_pid<=0):
            return
        sCmd = "handle.UnRegister"
        sCmd +="("+str(self.m_pid) +"," +self.m_sName
        res = self.m_WBXTFCorba.execute("local",sCmd)
        if(res["rc"]!=0):
            return

    def __getPID(self):
        import os
        return os.getpid()

    def UnRegister(self):
        if not self.IsRegister():
            return
        self.__unRegisterHandle()
        self.m_bRegister = False
                     
    def IsRegister(self):
        return self.m_bRegister

    # def isMainThreadAlive(self):
    #     for oThread in threading.enumerate():
    #         print oThread.name
    #         if oThread.name == "MainThread":
    #             return oThread.is_alive()


    def isDependThreadAlive(self):
        for oThread in threading.enumerate():
            #print oThread.name
            if oThread.name == self.m_DependThreadName:
                return oThread.is_alive()
        return False

    def Run(self, timeout):
        self.m_bCancelFlag = False
        if(self.m_handle<=0):
            return
        while not self.m_bCancelFlag:
            if self.isDependThreadAlive() == False:
                break
            self.__Check()
            time.sleep(0.5)
        #tmLast = time.time()
        #tmNow = tmLast
        #while tmNow - tmLast <= timeout and (not self.m_bCancelFlag):
        #    self.__Check()
        #    time.sleep(1)
        #    tmNow = time.time()
    
    def Cancel(self):
        self.m_bCancelFlag = True        
    
    def __Check(self):
        while self.__ReadQueue():
            print "1"        
        
    def __ReadQueue(self):
        sCmd = "event.Get("
        sCmd += str(self.m_handle)+","+ str(5000)+")"
        res = self.m_WBXTFCorba.execute("local",sCmd)
        if(res["rc"]==0 and res["result"]!=None):
            res = res["result"]
            if(res["RC"]==0 and res["result"]):
                events = res["result"]
                for event in events:
                    eventID = event["eventID"]
                    request = event["request"]
                    param = event["param"]
                    if(param==None):
                        command = request + "()"
                    else:
                        command = request + formatWBXTFValue(param)
                    hresult = 0
                    sresult = ''
                    if not WB_CONFIG_DEBUG:
                        try:	                
                            sresult = execute(command)
                            sresult = formatWBXTFValue2(sresult)
                        except WBException, e:
                            hresult = e.GetCode()
                            sresult = e.GetDescription()
                            sresult = formatWBXTFValue2(sresult)
                        except Exception, e:
                            hresult = WBRES_Error
                            sresult = "Fail to execute"
                            sresult = formatWBXTFValue2(sresult)
                    else:
                        sresult = execute(command)
                        sresult = formatWBXTFValue2(sresult)
                    cmd = "event.Reply2"
                    paramValue = (self.m_handle,eventID,hresult,sresult)
                    cmd += formatWBXTFValue(paramValue)
                    res = self.m_WBXTFCorba.execute("local",cmd)
        
       
global gTools
gTools = {}     
def runAsTool(name, timeout = WB_INFINIT, dependThreadName = "MainThread"):
    global gTools
    tool = WBTool(name,dependThreadName)
    gTools['tool'] = tool
    tool.Register()
    tool.Run(timeout)
    tool.UnRegister()
    pass

def cancelAsTool():
    if gTools.has_key('tool'):
        gTools['tool'].Cancel()            


def registerAsTool(name,dependThreadName = "MainThread"):
    global gTools
    tool = WBTool(name,dependThreadName)
    gTools['tool'] = tool
    tool.Register()
    if tool.IsRegister() == True:
        return tool
    else:
        return None

def runningRegisterTool(tool,timeout = WB_INFINIT):
    try:
        tool.Run(timeout)
    except Exception,e:
        print "python tool runtime error:%s" % e
    finally:
        tool.UnRegister()


    ##############################################################






"""
if __name__ == "__main__":    
    __testConvertParam2Var('()', [])
    __testConvertParam2Var('(,)', [None,None])
    __testConvertParam2Var('{}', {})
    __testConvertParam2Var('{:}', {None:None})
    __testConvertParam2Var('test', "test")
    __testConvertParam2Var('"test"', "test")
    __testConvertParam2Var('"tes,:{}()t"', "tes,:{}()t")
    __testConvertParam2Var('1', 1)   
    __testConvertParam2Var('2.4', 2.4)
    __testConvertParam2Var(r'"`"2.4"', '"2.4')
    __testConvertParam2Var(r'test1', 'test1')
    __testConvertParam2Var(r' test1   ', 'test1')
    __testConvertParam2Var(r' " test1"   ', ' test1')
    __testConvertParam2Var(r'(1,2,3)', [1,2,3])
    __testConvertParam2Var(r'(1,"test",10.143)', [1,"test",10.143])
    __testConvertParam2Var(r' ( 1  ,  "test"  ,  10.143  ) ', [1,"test",10.143])
    __testConvertParam2Var(r' ( 1  ,  "test"  ,  False  ) ', [1,"test",False])
    __testConvertParam2Var(r' ( 1  ,  (12, "test", 65.76) ,  False  ) ', [1,[12, "test",65.76] ,False])
    __testConvertParam2Var(r'{test:value}', {"test":"value"})
    __testConvertParam2Var(r'  { test :  value1  } ', {"test":"value1"})
    __testConvertParam2Var(r'{1:"test"}', {1:"test"})
    __testConvertParam2Var(r'{1:"test", "2":"value", "china":(1,"2",{"zone":"china"},4)}', {1:"test", "2":"value", "china":[1,"2",{"zone":"china"},4]})    

    __testConvertParam2Var('""', "")  
    __testConvertParam2Var('', None)      
    __testConvertParam2Var('"test"', "test")
    __testConvertParam2Var('"2009-10-21 09:30:12"', "2009-10-21 09:30:12")
    __testConvertParam2Var('("2009-10-21 09:30:12", "2009-10-21 09:30:13", "test/test2/test3")', ["2009-10-21 09:30:12", "2009-10-21 09:30:13", "test/test2/test3"])
    __testConvertParam2Var('"()"', "()")
    __testConvertParam2Var('"2009-10-21()09:30:12"', "2009-10-21()09:30:12")
    __testConvertParam2Var('"2009-10-21,09:30:12"', "2009-10-21,09:30:12")
    __testConvertParam2Var('test,value', "test,value")
    __testConvertParam2Var('test"value', "test\"value")
    __testConvertParam2Var(r'"test`"value"', "test\"value")
    __testConvertParam2Var('"test{}value"', "test{}value")
    __testConvertParam2Var('"test()value"', "test()value")
    __testConvertParam2Var('test', "test")
    __testConvertParam2Var('("10", "20")', ["10", "20"])
    __testConvertParam2Var('( "10" , "20")', ["10", "20"])
    __testConvertParam2Var('( "10"     ,     "20" ) ', ["10", "20"])
    __testConvertParam2Var('( 10     ,     20 ) ', [10, 20])
    __testConvertParam2Var('1', 1)
    __testConvertParam2Var('786767', 786767)
    __testConvertParam2Var('1.6', 1.6)
    __testConvertParam2Var('True', True)
    __testConvertParam2Var('False', False)
    __testConvertParam2Var('(1)', [1])
    __testConvertParam2Var('(1,2,3)', [1,2,3])
    __testConvertParam2Var('(1,(1,2,3),3)', [1,[1,2,3],3])
    __testConvertParam2Var('(1, (1, 2 , 3),3)', [1,[1,2,3],3])
    __testConvertParam2Var('(1,"2",3)', [1,"2",3])
    __testConvertParam2Var('{"test":"value"}', {'test':'value'})
    __testConvertParam2Var('{test:25}', {'test':25})
    __testConvertParam2Var("{'test':25}", {'test':25})
    __testConvertParam2Var("{'test':(1,2,{test:10})}", {'test':[1,2,{"test":10}]})
#    __testConvertParam2Var(r"{'te`"st':(1,2,{test:10})}", {'te"st':[1,2,{"test":10}]})        
    
    __testConvertParam2Var(r'"test', '"test')
    __testConvertParam2Var(r'("test', '("test')
    __testConvertParam2Var(r'("test", "good"', '("test", "good"')
    __testConvertParam2Var(r'{"test":"good"', '{"test":"good"')
    __testConvertParam2Var(r'{"test":', '{"test":')    
    
    setRoot(globals())
    execute("testFun((1,good,{hello:world},2))")
"""
