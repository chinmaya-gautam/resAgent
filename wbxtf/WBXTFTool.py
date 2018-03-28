'''
    Base library for WBXTF Tools 
    @author: Fei Liang
    @date: 2010/01/05
    @version: 1.0.0
    @license: Copyright Cisco-Webex Corp.
'''

import WBXTF


class WBXTFToolGroup(WBXTF.WBXTFObjectGroup):
    def __init__(self):
        WBXTF.WBXTFObjectGroup.__init__(self)
    
    def onGetRootGroup(self):
        return self
    
    def exitTool(self):
        group = self.onGetRootGroup()
        objs = group.m_objs
        #return WBXTF.WBXTFKillObjects(objs)
        return group.execute("wbxtf.sys.Kill()")

    def RunAtLoop(self,utcTime,sCommand,nTimes = 1 ,nDuration = 0,nPeriod = 60):
        """
        Execute commands at certain time. The method support WBXTFRE. please Learn WBXTFRE mechanism .
        >>>Example
            mgr = WBXTFToolMgr()
            mgr.setToolPath("d:/deomtool.exe")
            objs = mgr.runToolsOnMachine("local",10)
            group = mgr.getGroup("all")
            gmt = time.gmtime()
            nStartTime = int(time.mktime(gmt)) + 10 #Execute the command after 10 second.
            print group.RunAtLoop(nStartTime,"wbxtf.info.GetPID()")#All tool Execute command at the same time.

            interval =5 #second
            group.setKeyValueNumIncrease("RunAtTime",nStartTime,interval)
            group.RunAtLoop(WBXTF.WBXTFRE("RunAtTime"),"wbxtf.info.GetPID()")#Each tool Execute command,and not at the same time. each distant interval.
        @type utcTime: string
        @param utcTime: The utc time
        @type sCommand: string
        @param sCommand: The command send to tool
        @type nTimes: int
        @param nTimes:
        @type nDuration: int
        @param nDuration:
        @type nPeriod: int
        @param nPeriod: 
        @rtype:  List
        @return: result list
        """ 
        group = self.onGetRootGroup()
        cmd = "wbxtf.util.AtUTCTimeLoop(%s,%s,%d,%d,%d)"%(WBXTF.WBXTFVar(utcTime), \
                                                          WBXTF.WBXTFVar(sCommand), \
                                                          nTimes, \
                                                          nDuration, \
                                                          nPeriod)
        return group.executeRE(cmd)        

    def setKeyValueNumIncrease(self,key,num,interval=1):
        """
        It will set each object param as (key,value), and each object's value is int and increase as interval,the begin number is num.
        >>> Example
                group.setKeyValueNumIncrease("demo",1,5)
                It means:
                        The first object's value of key "demo" is : 1
                        The second object's value of key "demo" is : 1 + 5
                        The third object's value of key "demo" is : 1 + 5*2
                
        @type key: string
        @param key: The object's key
        @type num: int
        @param num: The begin number be set.
        @type interval: int
        @param interval: 
        @rtype:  bool
        @return: True if success
        """ 
        try:
            index =0
            while(index<len(self.onGetRootGroup().m_objs)):
                self.onGetRootGroup().m_objs[index].setKeyValue(key,num+interval*index)
                index+=1
        except Exception,e:
            WBXTF.WBXTFWarning("toolgroup call setKeyValueNumIncrease exception:%s" % e)
            return False
        return True

    def setKeyValueObjectKeys(self,key,objKeys,jointString="_",stringBegin="",stringEnd=""):
        """
        It will set each object param as (key,value), and each object's value is string.
        The string value is stringBegin + object's value of objKeys +StringEnd. The value of each objKeys will be joint by jointString.
        >>> Example
                group.setKeyValueNumIncrease("demo",["machine","url"],"_","TheBeginString","TheEndString")
                It means:
                        The first object's value of key "demo" is : "TheBeginString" + obj.sMachine + "_" + obj.url + "TheEndString"
                        The second object's value of key "demo" is : "TheBeginString" + obj.sMachine + "_" + obj.url + "TheEndString"
                        The third object's value of key "demo" is : "TheBeginString" + obj.sMachine + "_" + obj.url + "TheEndString"
        @type key: string
        @param key: The object's key
        @type objKeys: list
        @param objKeys: key list
        @type jointString: string
        @param jointString:
        @type stringBegin:  string
        @param stringBegin: 
        @type stringEnd: string
        @param stringEnd: 
        @rtype:  bool
        @return: True if success
        """
        try:
            index =0
            while(index<len(self.onGetRootGroup().m_objs)):
                keyIndex = 0
                value = stringBegin
                while keyIndex <len(objKeys):
                    value += "%s"%self.onGetRootGroup().m_objs[index].getKeyValue(objKeys[keyIndex])
                    keyIndex +=1
                    if(keyIndex<len(objKeys)):
                        value += jointString    
                value += stringEnd
                self.onGetRootGroup().m_objs[index].setKeyValue(key,value)
                index+=1
        except Exception,e:
            WBXTF.WBXTFWarning("toolgroup call setKeyValueObjectKeys exception:%s" % e)
            return False
        return True

    def setKeyValueObjectKeysAndNumIncrease(self,key,objKeys,num,interval=1,jointString="_",stringBegin="",stringEnd=""):
        """
        It will set each object param as (key,value), and each object's value is string.
        The string value is stringBegin + object's value of objKeys + an increase number +StringEnd. The value of each objKeys will be joint by jointString.
        >>> Example
                group.setKeyValueObjectKeysAndNumIncrease("demo",["machine","url"],1,5,"_","TheBeginString","TheEndString")
                It means:
                        The first object's value of key "demo" is : "TheBeginString" + obj.sMachine + "_" + obj.url + 1 + "TheEndString"
                        The second object's value of key "demo" is : "TheBeginString" + obj.sMachine + "_" + obj.url + 1+5  +"TheEndString"
                        The third object's value of key "demo" is : "TheBeginString" + obj.sMachine + "_" + obj.url + 1+5*2 +"TheEndString"
        @type key: string
        @param key: The object's key
        @type objKeys: string
        @param objKeys: list of object's key
        @type num: int
        @param num:  The begin number be set.
        @type interval: int
        @param interval: 
        @type jointString: string
        @param jointString: 
        @type stringBegin: string
        @param stringBegin:
        @type stringEnd: string
        @param stringEnd: 
        @rtype:  bool
        @return: True if success
        """
        try:
            index =0
            while(index<len(self.onGetRootGroup().m_objs)):
                keyIndex = 0
                value = stringBegin
                while keyIndex <len(objKeys):
                    value += "%s"%self.onGetRootGroup().m_objs[index].getKeyValue(objKeys[keyIndex])
                    keyIndex +=1
                    if(keyIndex<len(objKeys)):
                        value += jointString
                value += "%s"%(num+index*interval)
                value += stringEnd
                self.onGetRootGroup().m_objs[index].setKeyValue(key,value)
                index+=1
        except Exception,e:
            WBXTF.WBXTFWarning("toolgroup call setKeyValueObjectKeysAndNumIncrease exception:%s" % e)
            return False
        return True

    def setKeyValueMachineAndNumIncrease(self,key,num,interval=1,sJoint="_"):
        """
        It will set each object param as (key,value), and each object's value is string.
        The string value is object's machine name + a increase num.
        >>> Example
                group.setKeyValueMachineAndNumIncrease("demo",1,5)
                It means:
                        The first object's value of key "demo" is : obj.sMachine + "_" + 1 
                        The second object's value of key "demo" is : obj.sMachine + "_" + 1 +5 
                        The third object's value of key "demo" is : obj.sMachine + "_" + 1 + 5*2
        @type key: string
        @param key: The object's key
        @type num: int
        @param num: The begin number be set.
        @type interval: int
        @param interval:  
        @type jointString: string
        @param jointString: 
        @rtype:  bool
        @return: True if success
        """
        try:
            index =0
            while(index<len(self.onGetRootGroup().m_objs)):
                self.onGetRootGroup().m_objs[index].setKeyValue(key,self.onGetRootGroup().m_objs[index].sMachine +sJoint+"%d"%(num+interval*index))
                index+=1
        except Exception,e:
            WBXTF.WBXTFWarning("toolgroup call setKeyValueMachineAndNumIncrease exception:%s" % e)
            return False
        return True
    
    def setKeyValueRunAtTimeByMachineIncrease(self,baseRampupTime,interval,eachNumber,runatKey="RunAtTime"):
        """
        It will set each object param as (key,value), and each object's value is int as UTC time.
        The rule:
                A batch tools has "EachNumber" tools and will Execute at the same time.
                The time of Each batch tools distant "interval" second.
                The first batch 's time is "baseRampupTime"
                Each batch tools will contain as more machine as it can.
        >>> Example
                gmt = time.gmtime()
                nStartTime = int(time.mktime(gmt)) + 10 #Execute the command after 10 second.
                group.setKeyValueRunAtTimeByMachineIncrease(nStartTime,5,10,"RunAtTime")
                It means:
                        The first batch object's value of key "RunAtTime" is : nStartTime  
                        The second batch object's value of key "RunAtTime" is : nStartTime +5*1
                        The third batch object's value of key "RunAtTime" is : nStartTime +5*2
                        Each batch has 10 tools.
        @type baseRampupTime: int
        @param baseRampupTime: utc time
        @type interval: int
        @param interval: 
        @type eachNumber: int
        @param eachNumber:  
        @type runatKey: string
        @param runatKey: 
        @rtype:  bool
        @return: True if success
        """
        
        try:
            objList = self.__sortObjByMachineIncrease()
            objLeft = len(objList)
            atTime = baseRampupTime
            while(objLeft>0):
                if(objLeft<eachNumber):
                    eachNumber = objLeft
                number = objLeft - eachNumber
                while(objLeft>number):
                    objList[objLeft-1].setKeyValue(runatKey,atTime)
                    objLeft -= 1    
                atTime += interval
        except Exception,e:
            WBXTF.WBXTFWarning("toolgroup call setKeyValueRampupTimeByMachineIncrease exception:%s" % e)
            return False
        return True              

    def __sortObjByMachineIncrease(self):
        sortObjs = []
        try:
            mapMachine = {}
            for obj in self.onGetRootGroup().m_objs:
                if(mapMachine.has_key(obj.sMachine)):
                    mapMachine[obj.sMachine].append(obj)
                else:
                    mapMachine[obj.sMachine]= []
                    mapMachine[obj.sMachine].append(obj)
            while mapMachine!={}:
                for each in mapMachine.keys():
                    if(len(mapMachine[each])==0):
                        del mapMachine[each]
                    else:
                        sortObjs.append(mapMachine[each].pop())
        except Exception,e:
            WBXTF.WBXTFWarning("toolgroup call setKeyValueNumIncrease exception:%s" % e)
        return sortObjs
        
    
class WBXTFToolObject(WBXTF.WBXTFObject):
    def __init__(self,url,bselfobject = 0):
        WBXTF.WBXTFObject.__init__(self, url, bselfobject)

    def RunAtLoop(self,utcTime,sCommand,nTimes = 1 ,nDuration = 0,nPeriod = 60):
        """
        Execute an command at a certain time.
        >>>Example
            mgr = WBXTFToolMgr()
            mgr.setToolPath("d:/deomtool.exe")
            objs = mgr.runToolsOnMachine("local",10)
            objName = "firstTool"
            objs[0].setName(objName)
            obj = mgr.getObjectByName(objName)
            gmt = time.gmtime()
            nStartTime = int(time.mktime(gmt)) + 10 #Execute the command after 10 second.
            print obj.RunAtLoop(nStartTime,"wbxtf.info.GetPID()")
        @type utcTime: string
        @param utcTime: The utc time
        @type sCommand: string
        @param sCommand: The command send to tool
        @type nTimes: int
        @param nTimes:
        @type nDuration: int
        @param nDuration:
        @type nPeriod: int
        @param nPeriod: 
        @rtype:  map
        @return: result
        """         
        return self.wbxtf.util.AtUCTTimeLoop(utcTime,sCommand,nTimes,nDuration,nPeriod)

    def onGetRootTool(self):
        return self
    
    def exitTool(self):
        obj = self.onGetRootTool()
        obj.wbxtf.sys.Kill()

WBXTFToolType_C = "c"
WBXTFToolType_Java = "java"
WBXTFToolType_Python = "python"

class WBXTFToolMgr:
    """
    Convert a variable to a WBXTF format
    >>> Example
        mgr = WBXTFToolMgr()
        mgr.setToolPath("d:/deomtool.exe")
        objs = mgr.runToolsOnMachine("local",10)
        objName = "firstTool"
        objs[0].setName(objName)
        obj = mgr.getObjectByName(objName)
        print obj.wbxtf.info.GetPID()
        group = mgr.getGroup("all")
        print group.execute("wbxtf.info.GetPID()")
    @author: Fei Liang
    @date: 2011/4/20   
    """
    
    def __init__(self):
        self.m_sToolWBXTFName = ""
        self.m_machines = []
        self.m_toolPath = ""
        self.m_toolCfgPath = ""
        self.m_group = {}        
        self.m_group["all"] = self.onGetEmptyGroup()
        self.m_toolParams={}
        self.m_processName = ""
        self.m_toolStartParam = ""
        self.m_toolType = WBXTFToolType_C
        self.m_toolStartExtend = ""

    def setToolStartExtend(self,sExtend):
        self.m_toolStartExtend = sExtend

    def getToolStartExtend(self):
        return self.m_toolStartExtend
    
    def setToolType(self,toolType):
        """
        Set The tool type                    
        @type toolType: string
        @param toolType: The tool type,should be one of  WBXTFToolType_C,WBXTFToolType_Java,WBXTFToolType_Python
        @rtype:  None
        @return: None
        """  
        self.m_toolType = toolType
        return
        
    def getToolType(self):
        return self.m_toolType

    def formatToolPath(self,option=0):
        """
        Format the start command with toolpath,toolconfig,startparam
        The default format is:
        c/c++ Tool  : toolPath  startParam
        java Tool   : java -jar toolPath -c toolcfg
        python Tool : python toolpath startparam
        User should overwrite this formatToolPath function if the tool has special start mode.
        If use the default format, User should call setToolType to special the tool type before run tools.
        @type option: any type
        @param option: this is for user extention
        @rtype:  String,String
        @return: command,commandparam
        """ 
        toolType = self.getToolType()
        if(toolType==WBXTFToolType_Java):
            sPath = "java -jar %s"%(self.m_toolPath)
            if(self.m_toolCfgPath!=""):
                sPath+= " -c %s"%(self.m_toolCfgPath)
            sParam = ""
        elif(toolType==WBXTFToolType_Python):
            sPath = "python %s"%(self.m_toolPath)
            if(self.m_toolStartParam!=""):
                sPath += " %s"%self.m_toolStartParam
            sParam = ""        
        else:
            sPath = self.m_toolPath
            sParam = self.m_toolStartParam
        sExtend = self.m_toolStartExtend
        return sPath,sParam,sExtend
    
    def getToolStartParam(self):
        return self.m_toolStartParam
    
    def setToolStartParam(self,param):
        self.m_toolStartParam = param

    def getToolProcessName(self):
        return self.m_processName
    
    def setToolProcessName(self,toolName):
        """
        Set the tool process name when started.
        @type toolName: string
        @param toolName: process name
        @rtype:  None
        @return: None
        """ 
        self.m_processName = toolName
    
    def setToolWBXTFName(self,name):
        """
        Set the tool's instance name when join wbxtf.
        @type name: string
        @param name: instance name
        @rtype:  None
        @return: None
        """ 
        self.m_sToolWBXTFName = name
        
    def getToolWBXTFName(self):
        return self.m_sToolWBXTFName
    
    def getToolParams(self,addParam={}):
        param = self.m_toolParams
        for key in addParam:
            param[key] = addParam[key]
        return param
    
    def setToolParams(self,params):
        self.m_toolParams = params

    def getObjectByName(self,name):
        """
        Set the tool's instance name when join wbxtf.
        >>> Example
            mgr = WBXTFToolMgr()
            objs = mgr.runToolsOnMachine("local",10)
            objName = "firstTool"
            objs[0].setName(objName)
            obj = mgr.getObjectByName(objName)
            print obj.wbxtf.info.GetPID()
        @type name: string
        @param name: object's name
        @rtype:  tool object
        @return: tool object. it's final tool object.
        """ 
        group = self.getGroup("all")
        for obj in group.m_objs:
            if (obj.getName() == name):
                return obj  
        return None
    
    def getObjsByKeyValue(self,key,value):
        """
        Set the tool's instance name when join wbxtf.
        @type key: string
        @param key: object's key
        @type value: any type
        @param value: the value      
        @rtype:  list
        @return: object list. return the list, if object has value.
        """ 
        group = self.getGroup("all")
        objs = []
        for obj in group.m_objs:
            if(obj.getKeyValue(key)!=None and obj.getKeyValue(key)==value):
                objs.append(obj)
        return objs
                  
    
    def setMachines(self,machines):
        self.m_machines = machines
    
    def addMachines(self,machines):
        for machine in machines:
            if(not(machine in self.m_machines)):
                self.m_machines.append(machine)
    
    def addMachine(self,machine):
        if not (machine in self.m_machines):
            self.m_machines.append(machine)
    
    def getMachines(self):
        return self.m_machines
    
    def getToolPath(self):
        return self.m_toolPath
    
    def setToolPath(self,toolPath):
        self.m_toolPath = toolPath

    def setToolCfgPath(self,toolCfgPath):
        self.m_toolCfgPath = toolCfgPath
        
    def getToolCfgPath(self):
        return self.m_toolCfgPath
 
    def getGroup(self,groupName):
        """
        get the group which name equals groupName.
        >>> Example
            mgr = WBXTFToolMgr()
            mgr.runToolsOnMachine("local",10)
            group = mgr.getGroup("all")
            print group.execute("wbxtf.info.GetPID()")
        @type groupName: string
        @param name: group's name
        @rtype:  group
        @return: tool group. it's final tool group.
        """ 
        if(self.m_group.has_key(groupName)):
            return self.m_group[groupName]
        else:
            return self.onGetEmptyGroup()
            
    def addObjToGroup(self,groupName,obj):
        if(self.m_group.has_key(groupName)):
            self.m_group[groupName].add(obj)
        else:
            self.m_group[groupName] = self.onGetEmptyGroup()
            self.m_group[groupName].add(obj)
    
    def addObjListToGroup(self,groupName,objs):
        if(self.m_group.has_key(groupName)):
            self.m_group[groupName].addList(objs)
        else:
            self.m_group[groupName] = self.onGetEmptyGroup()
            self.m_group[groupName].addList(objs)
    
    def addGroupToGroup(self,groupName,group):
        if(self.m_group.has_key(groupName)):
            self.m_group[groupName].addList(group.m_objs)
        else:
            self.m_group[groupName] = self.onGetEmptyGroup()
            self.m_group[groupName].addList(group.m_objs)
    
    def deleteGroup(self,groupName):
        if(self.m_group.has_key(groupName)):
            del self.m_group[groupName]
    
    def updateGroup(self,groupName,group):
        self.m_group[groupName] = group

    
    def runToolsOnMachine(self,machine,nNum,runOption = 0 ,timeout = 60):
        """
        Run tools in one machine, and put tools in group "all"
        >>> Example
            mgr = WBXTFToolMgr()
            mgr.runToolsOnMachine("local",10)
            group = mgr.getGroup("all")
            print group.execute("wbxtf.info.GetPID()")
        @type machine: string
        @param machine: target machine
        @type nNum: int
        @param nNum: tool number to run
        @type runOption: any type
        @param runOption: for user extention
        @type timeout: int
        @param timeout: the wbxtf will return and treat the tool which has not join wbxtf when timeout.
        @rtype:  list
        @return: tool object list. it's final tool object list.
        """ 
        
        if(machine==""):
            WBXTF.WBXTFWarning("runToolsOnMachine.param machine is null")
            return []
        if(nNum <1):
            WBXTF.WBXTFWarning("runToolsOnMachine.param nNum must > 0")
            return []
        sPath,sParam,sExtend = self.formatToolPath(runOption)
        objs  = WBXTF.WBXTFRunObjects(machine, sPath, sParam, nNum, timeout, sExtend)
        objList = []
        for obj in objs:
            finalTool = self.onGetFinalTool(obj.GetURI())
            objList.append(finalTool)
        self.addObjListToGroup("all",objList)
        return objList
        
    def runToolsOnMachines(self,rules,runOption = 0,timeout = 60,bIgnoreFail = False):
        """
        Run tools in many machine, and put tools in group "all".Please see also WBXTF.WBXTFRunObjectsOnMachines in WBXTF.py
        >>> Example
            mgr = WBXTFToolMgr()
            rules = [{'machine':'local', 'num':10}]
            mgr.runToolsOnMachine("local")
            group = mgr.getGroup("all")
            print group.execute("wbxtf.info.GetPID()")
        @type rules: list
        @param rules: rules to run machine
        @type runOption: any type
        @param runOption: for user extention
        @type timeout: int
        @param timeout: the wbxtf will return and treat the tool which has not join wbxtf when timeout.
        @rtype:  list
        @return: tool object list. it's final tool object list.
        """ 

        sPath,sParam,sExtend = self.formatToolPath(runOption)
        objs = WBXTF.WBXTFRunObjectsOnMachines(rules, sPath, sParam, timeout, bIgnoreFail, sExtend)
        objList = []
        for obj in objs:
            finalTool = self.onGetFinalTool(obj.GetURI())
            objList.append(finalTool)
        self.addObjListToGroup("all",objList)
        return objList        


    def runToolsOnMachinesByTotal(self,machines,totalNum,runOption = 0,timeout = 60,bIgnoreFail = False):
        """
        Run tools in many machine,and total run "totalNum" tools.
        And tools will run at each machine as average as possible.
        After tools integrate into WBXTF, put all the tools in group "all".
        >>> Example
            mgr = WBXTFToolMgr()
            machines = ["machine1","machine2"]
            mgr.runToolsOnMachinesByTotal(machines,6) #machine1 will run 3 tools, machine2 will run 3 tools
            print mgr.getToolNumOnMachines(machines)
        @type machines: list
        @param machines: list of machine
        @type eachNum: int
        @param eachNum: the total tool number
        @type runOption: any type
        @param runOption: for user extention
        @type timeout: int
        @param timeout: the wbxtf will return and treat the tool which has not join wbxtf when timeout.
        @rtype:  list
        @return: tool object list. it's final tool object list.
        """
        if(len("machines")<1):
            WBXTF.WBXTFWarning("runToolsOnMachinesByTotal failed: no machines.")
            return None
        averageNum = totalNum/len(machines)
        leftNum = totalNum%len(machines)
        rules = []
        index =0
        while(index<len(machines)):
            rule={}
            rule["machine"]=machines[index]
            if leftNum == 0 :
                rule["num"]=averageNum
            else:
                if(index<leftNum):
                    rule["num"]=averageNum + 1
                else:
                    rule["num"]=averageNum
            rules.append(rule)
            index +=1
        return self.runToolsOnMachines(rules,runOption,timeout,bIgnoreFail)

    def runToolsOnMachinesAvg(self,machines,eachNum,runOption = 0,timeout = 60,bIgnoreFail = False):
        """
        Run tools in many machine,and each machine start the same number of tools.  After tools integrate into WBXTF, put all the tools in group "all".
        >>> Example
            mgr = WBXTFToolMgr()
            machines = ["machine1","machine2"]
            mgr.runToolsOnMachinesAvg(machines,6) #machine1 will run 3 tools, machine2 will run 3 tools
            print mgr.getToolNumOnMachines(machines)
        @type machines: list
        @param machines: list of machine
        @type eachNum: int
        @param eachNum: the tool number in each machine to run.
        @type runOption: any type
        @param runOption: for user extention
        @type timeout: int
        @param timeout: the wbxtf will return and treat the tool which has not join wbxtf when timeout.
        @rtype:  list
        @return: tool object list. it's final tool object list.
        """ 
        rules = []
        for machine in machines:
            rule={}
            rule["machine"]=machine
            rule["num"]=eachNum
            rules.append(rule)
        return self.runToolsOnMachines(rules,runOption,timeout)

    def runTool(self,machine,runOption = 0 ,timeout = 60):
        """
        Run one tool in one machine, and put tools in group "all"
        >>> Example
            mgr = WBXTFToolMgr()
            mgr.runTool("local")
            obj.setName("myTool")
            mgr.getToolByName("myTool").wbxtf.info.GetPID()
        @type machine: string
        @param machine: target machine
        @type runOption: any type
        @param runOption: for user extention
        @type timeout: int
        @param timeout: the wbxtf will return and treat the tool which has not join wbxtf when timeout.
        @rtype:  object
        @return: tool object. it's final tool object list.
        """         
        objs = self.runToolsOnMachine(machine,1,runOption ,timeout)
        if(objs!=None and len(objs)==1):
            return objs[0]
        return None

    def runMoreToolsOnMachines(self,machines,toolNum,runOption = 0 ,timeout = 60):
        """
        Run tools in machines, and it will run tools to make the tool number in machines as average as it can.
        After tools integrate into WBXTF, put all the tools in group "all".
        >>> Example
            #machine1 has 2 tools, machine2 has 3 tools already.
            mgr = WBXTFToolMgr()
            machines = ["machine1","machine2"]
            mgr.runMoreToolsOnMachine(machines,5) #machine1 will run 3 tools, machine2 will run 2 tools
            print mgr.getToolNumOnMachines(machines)
        @type machines: list
        @param machines: list of machine
        @type toolNum: int
        @param toolNum: the tool number to run in machines
        @type runOption: any type
        @param runOption: for user extention
        @type timeout: int
        @param timeout: the wbxtf will return and treat the tool which has not join wbxtf when timeout.
        @rtype:  list
        @return: tool object list. it's final tool object list.
        """ 
        if(len(machines)<1):
            WBXTF.WBXTFWarning("runMoreToolsOnMachines failed. no machines")
            return None
        mapNumber =self.getToolNumOnMachines(machines)
        machineMax = ""
        toolsTotal = 0
        for key in mapNumber.keys():
            toolsTotal += mapNumber[key]
            if(machineMax=="" or mapNumber[key]>mapNumber[machineMax]):
                machineMax = key
        polishingNum = len(machines)*mapNumber[machineMax] - toolsTotal
        toolLeft =toolNum
        toolAddEach =0
        toolAddLeft =0
        if(toolNum>polishingNum):
            toolAddEach = (toolNum-polishingNum)/len(machines)
            toolAddLeft = (toolNum-polishingNum)%len(machines)
        index = 0
        rules = []
        while(index<len(machines) and toolLeft>0):
            rule = {}
            machine = machines[index]
            rule["machine"] = machine
            rule["num"]=0
            maxNum = mapNumber[machineMax] - mapNumber[machine] + toolAddEach
            if(index<toolAddLeft):
                maxNum+=1
            if(toolLeft>maxNum):
                rule["num"] = maxNum
                toolLeft -= maxNum
            else:
                rule["num"] = toolLeft
                toolLeft =0
            if(rule["num"]>0):
                rules.append(rule)
            index +=1
        return self.runToolsOnMachines(rules,runOption,timeout)
        

    def runMoreToolsOnMachine(self,machines,toolNum,runOption = 0 ,timeout = 60):
        """
        Run tools in one machine,and the machine which has the least tool number in machines.
        After tools integrate into WBXTF, put all the tools in group "all".
        >>> Example
            #machine1 has 2 tools, machine2 has 3 tools
            mgr = WBXTFToolMgr()
            machines = ["machine1","machine2"]
            mgr.runMoreToolsOnMachine(machines,6) #machine1 will run 6 tools, machine2 will not run.
            print mgr.getToolNumOnMachines(machines)
        @type machines: list
        @param machines: list of machine
        @type toolNum: int
        @param toolNum: the tool number to run in one machine
        @type runOption: any type
        @param runOption: for user extention
        @type timeout: int
        @param timeout: the wbxtf will return and treat the tool which has not join wbxtf when timeout.
        @rtype:  list
        @return: tool object list. it's final tool object list.
        """ 
        mapNumber = self.getToolNumOnMachines(machines)
        machineMin =""
        for key in mapNumber.keys():
            if(machineMin=="" or mapNumber[key]<mapNumber[machineMin]):
                machineMin = key
        if(machineMin!=""):
            return self.runToolsOnMachine(machineMin,toolNum,runOption,timeout)
        
    def getToolNumOnMachines(self,machines):
        mapNumber = {}
        group = self.getGroup("all")
        for obj in group.m_objs:
            if(mapNumber.has_key(obj.sMachine)):
                mapNumber[obj.sMachine] +=1
            else:
                mapNumber[obj.sMachine] = 1
        mapMachineNumber = {}
        for machine in machines:
            if(mapNumber.has_key(machine)):
                mapMachineNumber[machine] = mapNumber[machine]
            else:
                mapMachineNumber[machine] =0
        return mapMachineNumber


    def getRunningToolsOnMachines(self,machines=[]):
        """
        get the tools in many machine, it will not put tools in group "all".
        >>> Example
            mgr = WBXTFToolMgr()
            objs = mgr.getRunningToolsOnMachines(["local"])
            mgr.addObjListToGroup("all",objs)
            group = mgr.getGroup("all")
            print group.execute("wbxtf.info.GetPID()")
        @type machines: list
        @param machines: machine list
        @rtype:  list
        @return: tool object list. it's final tool object list.
        """ 
        if(len(machines)<1):
            machines = self.m_machines
        objList = []
        requests = []
        results = []
        objGroup = WBXTF.WBXTFObjectGroup()
        sCommand = "WBXTFGetSubObjs()"
        for machine in machines:
            objToolProc = WBXTF.WBXTFGetToolObj(machine)
            objGroup.add(objToolProc)
        results = objGroup.execute(sCommand)
        for result in results:
            resTools = result["result"]
            sToolMachine = result["object"].sMachine
            if resTools["rc"] == 0 and resTools["result"] != None:
                nToolNum = len(resTools["result"])
                for item in resTools["result"]:
                    if item["name"] == self.getToolWBXTFName():
                        oTool = WBXTF.WBXTFGetToolBySubID(sToolMachine, int(item["subid"]))
                        finalTool = self.onGetFinalTool(oTool.GetURI())
                        objList.append(finalTool)
        return objList

    def getRunningToolsOnMachine(self,machine):
        """
        get the tools in single machine, it will not put tools in group "all".
        >>> Example
            mgr = WBXTFToolMgr()
            objs = mgr.getRunningToolsOnMachines("local")
            mgr.addObjListToGroup("all",objs)
            group = mgr.getGroup("all")
            print group.execute("wbxtf.info.GetPID()")
        @type machines: string
        @param machine: machine
        @rtype:  list
        @return: tool object list. it's final tool object list.
        """ 
        objList = []
        objToolProc = WBXTF.WBXTFGetToolObj(machine)
        res = objToolProc.WBXTFGetSubObjs()
        if(res["rc"]==0 and res["result"]!=None):
            #print res["result"]
            for item in res["result"]:
                #print item
                if item["name"] == self.getToolWBXTFName():
                    #print item["name"]
                    oTool = WBXTF.WBXTFGetToolBySubID(machine, int(item["subid"]))
                    finalTool = self.onGetFinalTool(oTool.GetURI())
                    objList.append(finalTool)
        return objList


    def onGetFinalTool(self,url):
        """
        get the final tool. Should overwrite this funcion if User inherit The WBXTFToolMgr and WBXTFToolObject/WBXTFToolGroup
        >>>Example
            User define class DemoToolMgr and DemoToolObject/DemoToolGroup.
            User should overwrite the onGetFinalTool and return DemoToolObject(url)
            User should overwrite the onGetEmptyGroup and return DemoGroupObject()
        @type url: string
        @param url: the WBXTFObject's url
        @rtype:  object
        @return: tool object. it's final tool object.
        """ 
        obj = WBXTFToolObject(url)
        return obj
 
    def onGetEmptyGroup(self):
        """
        get the final tool. Should overwrite this funcion if User inherit The WBXTFToolMgr and WBXTFToolObject/WBXTFToolGroup
        >>>Example
            User define class DemoToolMgr and DemoToolObject/DemoToolGroup.
            User should overwrite the onGetFinalTool and return DemoToolObject(url)
            User should overwrite the onGetEmptyGroup and return DemoGroupObject()
        @rtype:  group
        @return: tool group. it's final tool group.
        """ 
        group = WBXTFToolGroup()
        return group
        
    def exitAllTools(self):
        group = self.getGroup("all")
        group.exitTool()

    def killToolsByNameInMachines(self,machines,nTimeInterval=0,bWindows=True):
        WBXTF.WBXTFKillProcessByName(machines, self.m_processName, nTimeInterval, bWindows)
    
    def LaunchAppByPathInMachines(self,machines,path,nTimeInterval=0,bWindows=True):
        WBXTF.WBXTFRunOneProByPath(machines, path, nTimeInterval, bWindows)

    def killAllToolsByName(self,nTimeInterval =0,bWindows = True):
        WBXTF.WBXTFKillProcessByName(self.m_machines, self.m_processName, nTimeInterval, bWindows)



