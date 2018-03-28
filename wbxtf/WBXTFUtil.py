#!/usr/bin/python
##############################################
## class WBXTFDyncFunNameSupport
##############################################
import sys
import os
from types import *
import time

def WBXTFFormatUnicodeByte(var):
    newtext = ""
    if(len(var)==2):
        var = "00" + var
    if(len(var)%4!=0):
        return newtext
    index = 0
    while(index<len(var)/4):
        newtext = newtext + var[4*index+2:4*index+4]+var[4*index+0:4*index+2]
        index +=1
    return newtext

class WBXTFCompatibilitySupport:
    __m_items = []
    __m_alias = {}
    __m_feature = {"capital": True, "alias": True}
    def __init__(self, bCapital = True, bAlias = True):
        self.__m_items = dir(self)
        self.enableCapital(bCapital)
        self.enableAlias(bAlias)
        
    def enableCapital(self, bEnable):
        self.__m_feature["capital"] = bEnable
        
    def enableAlias(self, bEnable):
        self.__m_feature["alias"] = bEnable
        
    def addAlias(self, function, alias):
        self.__m_alias[alias] = function
                
    def removeAlias(self, alias):
        if self.__m_alias.has_key(alias):
            self.__m_alias.pop(alias)  

    def __getattr__(self, name):
        if self.__m_feature["capital"]:           
            if len(name) > 0:
                newname = ''                           
                newname = newname + name[0].lower() + name[1:]
                if newname in self.__m_items:
                    return eval('self.%s' % newname) 
        if self.__m_feature["alias"]:
            if self.__m_alias.has_key(name):
                return self.__m_alias[name]
        raise AttributeError, name
   

class STAFPerformancePatch:
    m_machines = []
    m_staf = None
    m_bOpt = True  
    def __init__(self, staf):
        self.m_staf = staf
        if os.environ.has_key('WBXTF_OPT_DNS_LOOUP') and \
            (os.environ['WBXTF_OPT_DNS_LOOUP'] == '0' or os.environ['WBXTF_OPT_DNS_LOOUP'] == 'false'):
            self.m_bOpt = False 
            
    def optimizeMachine(self, machine):                     
        if (not self.m_bOpt) or (not self.__isIP(machine)):
            return        
        if machine in self.m_machines:
            return
        self.m_machines.append(machine)        
        self.__doOptimize(machine)  
                
    def __doOptimize(self, machine):
        if self.m_staf == None:
            return False         
        res = self.m_staf.do_submit(machine, 'VAR', 'get SYSTEM VAR STAF/Config/Machine')
        if res['rc'] != 0:
            return False
        sHostName = res['result']
        sIP = machine    
        return self.__addToHost(sHostName, sIP)  
    
    def __isIP(self, machine):
        for chr in machine:
            if chr == '.' or (chr >= '0' and chr <= '9'):
                continue
            return False        
        return True   
    
    def __addToHost(self, host, ip):
        try:
            sHostFile = ''
            if sys.platform.find('win') >= 0:
                sHostFile = os.environ['SystemRoot']
                sHostFile = sHostFile + r"\system32\drivers\etc\hosts"
            else:
                return False # Disable Optimizing under Linux Platform
                sHostFile = '/etc/hosts'
                                            
            file = open(sHostFile, 'r')
            lines = file.readlines()
            hosts = []
            for line in lines:
                newline = line.strip()            
                if len(newline) == 0:
                    continue
                if newline[0] == '#':
                    continue            
                nFind = newline.find('#')
                if nFind >= 0:
                    newline = newline[0:nFind] 
                group = newline.split(' ')
                if len(group) == 0:
                    continue
                if group[0] != ip:
                    continue
                for index in range(len(group)):
                    if index == 0:
                        continue
                    item = group[index].strip()
                    if len(item) == 0:
                        continue
                    hosts.append(item)
            file.close()
            if host in hosts:
                return True
                    
            # Write the host name
            sNewline = '\n%s %s  # Auto Add by WBXTF Py Libary\n' % (ip, host)
            file = open(sHostFile, 'a+')
            file.write(sNewline)
            file.close()
            return False
        except Exception, e:
            print 'Fail to update host: %s' % (e)
            return False
        
def __WBXTFSplitString(sText, sep):
    res = []
    nPos = sText.find(sep)
    if nPos < 0:
        res.append(sText)
        res.append('')
        res.append('')
    else:
        res.append(sText[0:nPos])
        res.append(sep)
        res.append(sText[nPos + 1])
    return res
 
 
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

     def readUnicode(self, num):
         nNextPos = self.__m_pos + num
         nFromPos = self.__m_pos
         if nNextPos > len(self.__m_text):
             nNextPos = len(self.__m_text)
         if nNextPos == self.__m_pos:
             return ''
         self.__m_pos = nNextPos
         res = self.__m_text[nFromPos : nNextPos]
         res = WBXTFFormatUnicodeByte(res)
         newText = ""
         index =0
         while(index<len(res)/4):
             newText += "\u"+res[index*4+0:index*4+4]
             index +=1
         return newText
          
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
    elif type == 'unicode':
        data = stream.readUnicode(size)
        newText = eval('u"'+data+'"')
        return newText
    else:
       data = stream.read(size)
       return data 

def WBXTFDefaultResultFormat2Var(text):
    if type(text) != StringType and type(text) != type(''):
        print "Fail to WBXTFDefaultResultFormat2Var: %s" % (text)        
        return text
    stream = __WBXTFStringStream(text)
    try: 
        return __WBXTFDefaultResultFormat2Var(stream)
    except Exception,e:
        print "Warning:WBXTFDefaultResultFormat2Var:%s:%s" % (e, text)            

def WBXTFVar2DefaultResultFormat(var):
    sText = ""    
    typeVar = type(var)
    if typeVar == StringType:        
        sText = '@WSH:text:%s@%s' % (len(var), var)
    elif typeVar == IntType:
        sData = '%s' % var
        sText = '@WSH:int:%s@%s' %(len(sData), sData)
    elif typeVar == LongType:
        sData = '%s' % var
        sText = '@WSH:int64:%s@%s' %(len(sData), sData)
    elif typeVar == BooleanType:
        if sys.version > '2.3':
            if var:
                sData = '1'
            else:
                sData = '0'
            sText = '@WSH:bool:%s@%s' %(len(sData), sData)
        else:
            if var:        
                sText = '@WSH:bool:1@1'
            else:
                sText = '@WSH:bool:1@0'        
    elif typeVar == NoneType:
        sText = '@WSH:none:0@'       
    elif typeVar == FloatType:
        sData = '%s' % var
        sText = '@WSH:double:%s@%s' %(len(sData), sData)                    
    elif typeVar == ListType or typeVar == TupleType:
        sText = '@WSH:array:%s@' % (len(var))
        value = [sText]
        for item in var:
            value.append(WBXTFVar2DefaultResultFormat(item))
        sText = "".join(value)
    elif typeVar == DictType:
        value = ['@WSH:map:%s@' % (len(var))]
        for k,v in var.items():     
            sData = '%s' % k
            value.append('@WSH:item:%s@%s%s' % (len(sData), sData, WBXTFVar2DefaultResultFormat(v)))
        sText = "".join(value)
 
    elif typeVar == UnicodeType:
        sData = ""
        for chr in var:
            item = ord(chr)
            tmp = '%04X' % item
            tmp = WBXTFFormatUnicodeByte(tmp)
            sData = sData + tmp
        #sData = '%s' % (var)
        sText = '@WSH:unicode:%s@%s' % (len(sData), sData) 
        return sText                
    else:        
        sData = '%s' % (var)
        sText = '@WSH:text:%s@%s' % (len(sData), sData)     
    return sText

def WBXTFEncodeDefault(var):
    newtext = ''
    #var = var.replace("\"","")
    for chr in var:
        item = ord(chr)
        bConvert = True
        if item >= ord('0') and item <= ord('9'):
            bConvert = False
        elif item >= ord('a') and item <= ord('z'):
            bConvert = False
        elif item >= ord('A') and item <= ord('Z'):
            bConvert = False  
        if bConvert:
            tmp = '^%02X' % item
            newtext = newtext + tmp
        else:
            newtext = newtext + chr
    return newtext            
#        if ord(chr) >
#    needreplacechrs = "^,; \t\r\n()\"'[]{}<>\\`:" 
#    for item in needreplacechrs:
#        text = '^%02X' % ord(item)
#        var = var.replace(item, text)
#    return var

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
    if type(var) != StringType:
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
        print 'Except at decode:%s' % (var)
        return var

def __WBXTFConvertNoType(var):
    newVar = ""
    if type(var) == ListType or type(var) == TupleType:
        newVar = "("
        for item in var:
            if len(newVar) != 1:
                newVar = newVar + ","
            newVar += __WBXTFConvertNoType(item)
        newVar = newVar + ")"
    elif type(var) == DictType:
        newVar = "{"
        for k,v in var.items():
            if len(newVar) != 1:
                newVar = newVar + ","
            newVar += __WBXTFConvertNoType(k)
            newVar += ":"
            newVar += __WBXTFConvertNoType(v)
        newVar = newVar + "}"
    else:
        newVar = str(var) 
    return newVar

def WBXTFEqualWithoutType(var1, var2):
    return __WBXTFConvertNoType(var1) == __WBXTFConvertNoType(var2)

def WBXTFConvert2OldVar(var):
    newVar = None
    if type(var) == ListType or type(var) == TupleType:
        newVar = []
        for item in var:
            newVar.append(WBXTFConvert2OldVar(item))        
    elif type(var) == DictType:
        newVar = {}
        for k,v in var.items():
            newVar[k] = WBXTFConvert2OldVar(v) 
    else:
        newVar = str(var) 
    return newVar
    
    
"""
def test1():
    result = {}
    for index in range(200000):    
        res = {}
        res["test1"] = 10
        res["test2"] = "good"
        res["test3"] = 3
        res["test4"] = "dfffffffffffffffffffwerwrwererw"
        result["%s" % (index)] = res
    return WBXTFVar2DefaultResultFormat(result)

def test2(text):
    return WBXTFDefaultResultFormat2Var(text)    
    
def testInt():    
    for index in range(200000):
        result = 10
        WBXTFVar2DefaultResultFormat(result)  
          
def testString():    
    for index in range(200000):
        result = "test"
        WBXTFVar2DefaultResultFormat(result) 
             
def testList():    
    for index in range(200000):
        result = []
        WBXTFVar2DefaultResultFormat(result) 
        
def testList2():
    result = []
    for index in range(200000):
        result.append("test")
    WBXTFVar2DefaultResultFormat(result)       
          
def testMap():    
    for index in range(200000):
        result = {"value":1}
        WBXTFVar2DefaultResultFormat(result)     
              
def testMap2():  
    result = {}      
    for index in range(200000):
        result[index] = "value"
    WBXTFVar2DefaultResultFormat(result) 
                     
def testFunction(fun, *args):
    last = time.time()
    fun(*args)
    used = time.time() - last
    print "%s, Used Time:%0.2f" % (fun.__name__, used)
   
#import profile
#text = test1()
#profile.run("test2(text)")
#profile.run("test1()")
#testFunction(testInt)
#testFunction(testString)
#testFunction(testList2)
#testFunction(testMap2)

#testFunction(test2, test1())
"""