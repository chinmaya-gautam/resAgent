from com import WBXTF
import time
import random
import types

global mtSchedule, mtStart, mtNone
mtSchedule = 1
mtStart = 2
mtNone = 0

class Attendee(WBXTF.WBXTFObject):
	def __init__(self):
          pass 
      
class ASKGroup(WBXTF.WBXTFObjectGroup):
    def __int__(self):
        WBXTF.WBXTFObjectGroup.__init__(self)            
    
class AttendeeCP:
    pass


class ASKStrategy:
    def setEnv(self, env):
        self.m_env = env
    def run(self):
        pass
    
class ASKS_GetAnyAttendee(ASKStrategy):
    def __init__(self, num=1):
        self.m_num = num
            
    def run(self):        
        listObj = range(len(self.m_env.groupAttendee))
        nNum = len(listObj)
        for index in range(nNum):
            other = random.randint(0, nNum - 1)
            tmp = listObj[other]
            listObj[other] = listObj[index]
            listObj[index] = tmp
        if self.m_num > nNum:
            self.m_num = nNum
        group = ASKGroup()
        for index in range(nNum):
           group.add(self.m_env.groupAttendee.getObject(listObj[index]))           
        return group   

class ASKCheckPoint(WBXTF.WBXTFCompatibilitySupport):
    def __init__(self, env):
        WBXTF.WBXTFCompatibilitySupport.__init__(self)    
        self.env = env
        
    def checkChatAllLastInfo(self, sCommand):
        nNum = 0
        if self.env.getHost() != None:
            nNum = nNum + 1
        nNum = nNum + len(self.env.getAttendees())      
        ress = self.env.sendToAll("chat.GetAllChatMsg()")
        if len(ress) != nNum:
            WBXTF.WBXTFCheck("Verify chat", False)
            return False            
        for res in ress:
            try:
                nCount = len(res["result"]["result"])
                if nCount == 0:
                    WBXTF.WBXTFCheck("Verify the last chat string: not get the chat from attendee", False)
                    return False
                lastText = res["result"]["result"][nCount - 1]["Chatmsg"]
                if lastText != sCommand:
                    WBXTF.WBXTFCheck("Verify the last chat string: chat message does not match", False)
                    return False
            except Exception:
                WBXTF.WBXTFCheck("Verify the last chat string" % (ress), False)
                return False
        WBXTF.WBXTFCheck("Verify the last chat string", True)
        return True
  
    def checkPollingAnswers(self):
        resAttendees = self.env.sendToAttendee("polling.GetPollAnswers()")
        resHosts = self.env.sendToHost("polling.GetPollAnswers()")

        for resA in resAttendees:
            try:
                bCorrect = 0
                for resH in resHosts[0]["result"]["result"]:
                    if resA["result"]["result"][0] == resH:
                        bCorrect = 1     
                if bCorrect == 0:
                    strErrorMsg = "Verify polling data:" \
                          "Sender userid=" + str(resA["result"]["result"][0]["userid"]) + \
                          "answer:" + str(resA["result"]["result"][0]["answer"])
                    WBXTF.WBXTFCheck(strErrorMsg, False)
                    return False
                elif bCorrect == 1:
                    strResMsg = "Verify polling data:"\
                          "Sender userid=" + str(resA["result"]["result"][0]["userid"])
                    WBXTF.WBXTFCheck(strResMsg, True)
                    return True
            except Exception:
                WBXTF.WBXTFCheck("Verify polling data: Error", False)
                return False
    
    def checkAttendeeInMeeting(self,group,nodeid):
    	if group.getCount() == 0:
    			return
    	ress = group.execute("meeting.IsAttendeeInMeeting(%s)" % nodeid)
    	try:
    		for res in ress:
    			if res["result"]["rc"] != 0 or res["result"]["result"] != '1':
    				return False
    		return True
    	except Exception:
    		return False
			          	     	              
class ASKEnv(WBXTF.WBXTFCompatibilitySupport):
    def __init__(self):  
          WBXTF.WBXTFCompatibilitySupport.__init__(self)
            
          #################################
          ## Config
          #################################
          self.sHostMachine = ""
          self.sMachines = []
          self.sAttendeeMachines = []
          self.sClientMachines = []
          
          self.nToolNumHost = 0
          self.nToolNumAttendee = 0
          self.nToolNumClient = 0

          self.sDeploySourceMachine = ""
          self.sDeploySourcePath = ""
          self.sDeployTargetPath = ""
          self.sDeployPackName = "Attendee"
          self.sToolPath = "d:/test/ask/attendee.exe"

          self.sScheduleSite = ""
          self.sScheduleUser = ""
          self.sSchedulePass = ""
          self.sScheduleName = "Test_%s" % (int(random.random() * 100000))
          self.sScheduleMT = "MC"
          self.nScheduleP2P = 1
          self.sScheduleTCParam = ""
          self.nPCNAccountIndex = 0
          self.dictSchOptionParam = {}
          
          self.sClientIEPath = "C:/Program Files/Internet Explorer/iexplore.exe"          

          self.sConfMZM = ""
          self.sConfMeetingKey = ""
          self.sConfMeetingID = ""
          self.sConfMCC = ""
          self.sGDMEnable = 0
          self.sGDMParams = ""
          self.sMeetingDName = ""
          self.sGDMDNameList = ""
          
          self.sParamHost = "/role:host /trace:high"
          self.sParamAttendee = "/role:attendee /trace:high"

          self.bNeedUpateMeetingInfo = False

          self.nTimeout = 30
          
          self.bEnableTrace = True  
          
          ###############################
          ## Inside Variables
          ###############################
          self.groupHost = ASKGroup()
          self.groupAttendee = ASKGroup()
          self.objClients = []
          
          self.nMeetingCreateType = mtNone # 0 - Directly, 1 - Meeting Info, 2 - Schedule
         
        
    def CopySettingFrom(self, env):
            self.sHostMachine = env.sHostMachine
            self.sMachines = env.sMachines[:]
            self.sAttendeeMachines = env.sAttendeeMachines[:]
            self.sClientMachines = env.sClientMachines[:]
            
            self.nToolNumHost = env.nToolNumHost
            self.nToolNumAttendee = env.nToolNumAttendee
            self.nToolNumClient = env.nToolNumClient

            self.sDeploySourceMachine = env.sDeploySourceMachine
            self.sDeploySourcePath = env.sDeploySourcePath
            self.sDeployTargetPath = env.sDeployTargetPath
            self.sDeployPackName = env.sDeployPackName
            self.sToolPath = env.sDeployPackName

            self.sScheduleSite = env.sDeployPackName
            self.sScheduleUser = env.sScheduleUser
            self.sSchedulePass = env.sSchedulePass
            self.sScheduleName = env.sScheduleName
            self.sScheduleMT = env.sScheduleMT
            self.nScheduleP2P = env.nScheduleP2P
            self.sScheduleTCParam = env.sScheduleTCParam
            self.nPCNAccountIndex = env.nPCNAccountIndex
            self.dictSchOptionParam = env.dictSchOptionParam
            
            self.sClientIEPath = env.sClientIEPath            

            self.sConfMZM = self.sConfMZM
            self.sConfMeetingKey = env.sConfMeetingKey
            self.sConfMeetingID = env.sConfMeetingID
            self.sConfMCC = env.sConfMCC
            self.sGDMEnable = env.sGDMParams
            self.sGDMParams = env.sGDMParams
            self.sMeetingDName = env.sMeetingDName
            self.sGDMDNameList = env.sGDMDNameList

            self.sParamHost = env.sParamHost
            self.sParamAttendee = env.sParamAttendee

            self.bNeedUpateMeetingInfo = env.bNeedUpateMeetingInfo

            self.nTimeout = env.nTimeout
            
            self.nMeetingCreateType = env.nMeetingCreateType # 0 - Directly, 1 - Meeting Info, 2 - Schedule
            
    def Clone(self):
          env = ASKEnv()
          env.CopySettingFrom(self)
          return env 
            
      ##############################################
      ## Set
      #############################################      
    def setHostMachine(self, machine):
          if type(machine) == types.ListType or type(machine) == types.TupleType:
              self.sHostMachine = machine[0]
          else:
              self.sHostMachine = machine
          self.__mergeMachines()
      
    def setAttendeeMachines(self, machines):
          self.sAttendeeMachines = machines
          self.__mergeMachines()
     
    def setClientMachines(self, machines):
          self.sClientMachines = machines

    def setToolNum(self, nHost, nAttendee, nClient=0):
          self.nToolNumHost = nHost
          self.nToolNumAttendee = nAttendee
          self.nToolNumClient = nClient
      
    def setDeployPath(self, sourceMachine, sourcePath, targetPath, targetPack="Attendee"):
          self.sDeploySourceMachine = sourceMachine
          self.sDeploySourcePath = sourcePath.replace("\\", "/")
          self.sDeployTargetPath = targetPath.replace("\\", "/")
          self.sDeployPackName = targetPack

    def setScheduleInfo(self, siteUrl, userName, passWord, name=None, meetingType="MC", meetingPassword="", tcParam="", nPCNAccountIndex=0, dictSchOptionParam = {}):
          self.nMeetingCreateType = mtSchedule

          self.sScheduleSite = siteUrl
          self.sScheduleUser = userName
          self.sSchedulePass = passWord
          self.sScheduleMeetingPWD = meetingPassword
          if name != None and name != "":
                self.sScheduleName = name          
          self.sScheduleMT = meetingType
          self.sScheduleTCParam = tcParam
          self.nPCNAccountIndex = nPCNAccountIndex
          self.dictSchOptionParam = dictSchOptionParam
          
    def setMeetingInfo(self, mzmIP, meetingID, mccIP, meetingKey="12345678", SetGDMEnable=0, GDMParams="",meetingDName="",GDMDNameList="" ):
          self.nMeetingCreateType = mtStart
          self.sConfMZM = mzmIP
          self.sConfMeetingKey = meetingKey
          self.sConfMeetingID = meetingID
          self.sConfMCC = mccIP
          self.sGDMEnable = SetGDMEnable
          self.sGDMParams = GDMParams
          self.sMeetingDName = meetingDName
          self.sGDMDNameList = GDMDNameList

    def setClientIEPath(self, path):
          self.sClientIEPath = path

    def setHostParam(self, hostParam):
          self.sParamHost = hostParam

    def setAttendeeParam(self, attendeeParam):
          self.sParamAttendee = attendeeParam

    def setTimeout(self, nTimeout=30):
          self.nTimeout = nTimeout

    def setToolPath(self, path):
          self.sToolPath = path
      
      ##############################################
      ## Information
      #############################################
    def getAttendees(self):
          return self.groupAttendee

    def getHost(self):
          return self.groupHost
        
    def getGroupByStrategy(self, strategy):
          strategy.setEnv(self)
          return strategy.run()
        
    def getGroup_AnyAttendee(self, num=1):
          return self.getGroupByStrategy(ASKS_GetAnyAttendee(num))
    
    def getMeetingId(self): 
          return self.sConfMeetingID
    
    def getNodeIdFromGroup(self,group):
    	nodeidlist = []
    	if group.getCount() == 0:
    		return
    	self.__output("Start to get nodeid in group (%s)" % group.getName)           
        ress = group.execute("config.GetNodeID")
        for res in ress:
        	if res["result"]["rc"] != 0 or not res["result"]["result"].isdigit():
        		return -1
        	nodeidlist.append(res["result"]["result"])
        return nodeidlist

      ##############################################
      ## Action
      #############################################
    def init(self):
          pass
      
    def unInit(self):
          pass

    def deploy(self):
          self.__output("Start to deploy the tool")
          if len(self.sDeploySourceMachine) == 0:
                WBXTF.WBXTFError("Fail to deploying: not set source machine")
                return
          if len(self.sDeploySourcePath) == 0:
                WBXTF.WBXTFError("Fail to deploying: not set source path")
                return
          if len(self.sDeployTargetPath) == 0:
                WBXTF.WBXTFError("Fail to deploying: not set target path")
                return          
          bRes = True
          for machine in self.sMachines:
                objMachine = WBXTF.WBXTFObject("staf://%s/pack" % (machine))
                res = objMachine.Execute("Install(%s, %s, %s, %s)" % (self.sDeployPackName, self.sDeploySourceMachine, self.sDeploySourcePath, self.sDeployTargetPath))
                try:
                    if res["rc"] != 0 or int(res["result"]["rc"]) != 0:
                          bRes = False
                          WBXTF.WBXTFError("Fail to deploy on machine %s:%s" % (machine, res))                                         
                except Exception:
                          bRes = False
                          WBXTF.WBXTFError("Fail to deploy on machine %s" % machine)
          self.sToolPath = self.sDeployTargetPath
          self.sToolPath = self.sToolPath + "/attendee.exe"
          return bRes
      
    def runHost(self):
          if self.groupHost.getCount() > 0:
                return ASKGroup()

          self.__output("Start to run the host")
          objHost = WBXTF.WBXTFRunObject(self.sHostMachine, self.sToolPath, self.sParamHost, self.nTimeout)
          bRes = objHost != None
          self.__check("Verify running host", bRes)
          if bRes: 
              self.groupHost.add(objHost)
              WBXTF.WBXTFOutput("RunHost SetUniqueAttendeeId %s" % self.sHostMachine)
              self.groupHost.execute("config.SetUniqueAttendeeId(%s)" % self.sHostMachine);
          group = ASKGroup()
          group.copyFrom(self.groupHost)
          return group

    def runAttendee(self):
          if len(self.sAttendeeMachines) <= 0:
                return ASKGroup()
          return self.__runAttendee(self.sAttendeeMachines, self.nToolNumAttendee)
          
    def runMoreAttendee(self, sMachines, nToolNum= - 1):
          if nToolNum <= 0:
            nToolNum = len(sMachines) 
          return self.__runAttendee(sMachines, nToolNum)

    def runClient(self, attendeename = None):
          sURL = "%s/m.php?MT=3&AT=JM&BU=%s/&MK=%s&AE=test@test.com&AN=%s" % (self.sScheduleSite, self.sScheduleSite, self.sConfMeetingKey, attendeename)                
          if len(self.sClientMachines) <= 0 or self.nToolNumClient <= 0:
                return
          if len(self.objClients) > 0:
                return
          self.__output("Start to run the clients")
          bRes = True
          nEveryTool = int((self.nToolNumClient + len(self.sClientMachines) - 1) / len(self.sClientMachines))
          nRemained = self.nToolNumClient
          for machine in self.sClientMachines:
                nTool = nEveryTool
                if nTool > nRemained:
                     nTool = nRemained
                if nTool == 0:
                    break                
                objs = WBXTF.WBXTFRun(machine, self.sClientIEPath, sURL, nTool)
                if len(objs) != nTool:
                    bRes = False
                    break
                for obj in objs:
                    addObj = {}
                    addObj['machine'] = machine
                    addObj['handle'] = obj
                    self.objClients.append(addObj)
          self.__check("Verify running clients", bRes)
          
    def createMeeting(self):
          if self.nMeetingCreateType == mtSchedule:
                return self.createMeetingByScheduleInfo()
          elif self.nMeetingCreateType == mtStart:
                return self.createMeetingByMeetingInfo()
          else:
                return self.CreateMeetingByNone()                

    def scheduleJBHMeeting(self):
          self.__output("Start to schedule a JBH meeting")
          res = self.groupHost.execute("meeting.Schedule(%s,,%s,%s,%s,%s,%s,%s,0,%d,1)" % 
                 (self.sScheduleSite, self.sScheduleUser, self.sSchedulePass, self.sScheduleMT, self.sScheduleName, self.sScheduleMeetingPWD, self.sScheduleTCParam, self.nPCNAccountIndex))
          if not self.__checkResultsAsTrue(res):
                self.__check("Verify Schedule meeting", False)
                return False
          self.__output("Wait for schedule meeting...")
          time.sleep(20)
          self.bNeedUpateMeetingInfo = True
          self.__updateMeetingInfoFromHost()
          self.__output("Schedule meeting succ.")
          return True

    def createMeetingByScheduleInfo(self):
          self.__output("Start to schedule a meeting")
          res = self.groupHost.execute("meeting.Schedule(%s,,%s,%s,%s,%s,%s,%s,1,%d,0,%s)" % 
                 (self.sScheduleSite, self.sScheduleUser, self.sSchedulePass, self.sScheduleMT, self.sScheduleName, self.sScheduleMeetingPWD, self.sScheduleTCParam, self.nPCNAccountIndex, WBXTF.WBXTFVar(self.dictSchOptionParam)))
          if not self.__checkResultsAsTrue(res):
                self.__check("Verify creating meeting", False)
                return False
          bRes = self.waitMeetingCreate()
          self.bNeedUpateMeetingInfo = True
          self.__updateMeetingInfoFromHost()
          return bRes

    def createMeetingByMeetingInfo(self):
          self.__output("Start to create a meeting")
          if not self.__updateMeetingToHost():                 
                WBXTF.WBXTFError("Fail to update meeting information")
                return False          
          res = self.groupHost.execute("meeting.Open()")
          if not self.__checkResultsAsTrue(res):
                WBXTF.WBXTFError("Fail to create meeting")
                return False
          bRes = self.waitMeetingCreate()
          self.bNeedUpateMeetingInfo = True
          return bRes

    def createMeetingByNone(self):
          self.__output("Start to create a meeting")
          res = self.groupHost.execute("meeting.Open()")
          if not self.__checkResultsAsTrue(res):
                WBXTF.WBXTFError("Fail to create meeting")
                return False
          bRes = True
          bRes = self.waitMeetingCreate()
          self.bNeedUpateMeetingInfo = True
          self.__updateMeetingInfoFromHost()
          return bRes

    def joinMeeting(self):
          self.__output("Start to join the meeting")         
          if self.bNeedUpateMeetingInfo and (not self.__updateMeetingToAttendee()):
                WBXTF.WBXTFError("Fail to update meeting information")
                return False
          
          res = self.SendToAttendee("meeting.Open()")
          if not self.__checkResultsAsTrue(res):
                WBXTF.WBXTFError("Fail to join meeting")
                return False          
          return self.waitMeetingJoin()
        
    def joinMeetingForGroup(self, group):
          self.__output("Start to join the meeting")         
          if self.bNeedUpateMeetingInfo and (not self.__updateMeetingToGroup(group)):
                WBXTF.WBXTFError("Fail to update meeting information")
                return False
                      
          res = group.execute("meeting.Open()")
          if not self.__checkResultsAsTrue(res):
                WBXTF.WBXTFError("Fail to join meeting")
                return False          
          return self.waitMeetingJoin()        
        
    def updateMeetingInfoToGroup(self, group):
          return self.__updateMeetingToGroup(group)
      
    def enableIgnore(self, bEnable=True):
          if bEnable:
            self.m_oldErrorMode = WBXTF.WBXTFSetErrorModeAsIgnore()
            self.m_enableIgnore = True
          elif "m_oldErrorMode" in dir(self):
            self.m_enableIgnore = False
            WBXTF.WBXTFSetErrorMode(self.m_oldErrorMode)
          
    def sendToAll(self, command):
          ress = self.sendToHost(command)
          ress = ress + self.sendToAttendee(command)
          return ress

    def sendToHost(self, command):
          ress = self.groupHost.execute(command)
          return ress

    def sendToAttendee(self, command):
          ress = self.groupAttendee.execute(command)
          return ress

    def lockMeeting(self):
    	self.__output("Start to lock the meeting")
    	bres = self.sendToHost("meeting.Lock()")
    	if bres == "1" or bres == 1:
            return True
        else:
            return False
    
    def unLockMeeting(self):
    	self.__output("Start to unlock the meeting")
    	bres = self.sendToHost("meeting.UnLock()")
    	if bres == "1" or bres == 1:
            return True
        else:
            return False
           
    def leaveMeeting(self):
          self.__output("Start to leave the meeting") 
          result = self.SendToAttendee("meeting.Close")
          if not self.__checkResultsAsTrue(result):
          	return False
          bRes = self.__waitResult(self.groupAttendee, "meeting.IsOpen", '0', self.nTimeout)
          return bRes
          

    def closeMeeting(self):
          self.__output("Start to close the meeting") 
          result = self.sendToHost("meeting.Close")
          if not self.__checkResultsAsTrue(result):
          	return False
          bRes = self.__waitResult(self.groupAttendee, "meeting.IsOpen", '0', self.nTimeout)
          return bRes
         
    def createSession(self, sessionName):
          self.__output("Start to open session:%s" % (sessionName))  
          res = self.sendToHost("%s.Open" % (sessionName))
          if not self.__checkResultsAsTrue(res):
                WBXTF.WBXTFError("Fail to create session %s" % (sessionName))
                return
          self.WaitSessionCreate(sessionName)

    def closeSession(self, sessionName):
          self.__output("Start to close session:%s" % (sessionName))  
          res = self.sendToHost("%s.Close" % (sessionName))
          if not self.__checkResultsAsTrue(res):
                WBXTF.WBXTFError("Fail to create session %s" % (sessionName))
                return False
          return True              

    def waitMeetingCreate(self, nTimeout= - 1):
          bRes = self.__waitMeetingOpen(self.groupHost, nTimeout)
          self.__check("Verify whether the meeting is created", bRes)
          return bRes                

    def waitMeetingJoin(self, nTimeout= - 1):
          bRes = self.__waitMeetingOpen(self.groupAttendee, nTimeout)
          self.__check("Verify whether the meeting is joined", bRes)
          return bRes  
        
    def waitMeetingJoinForGroup(self, group, nTimeout= - 1):
          bRes = self.__waitMeetingOpen(group, nTimeout)
          self.__check("Verify whether the meeting is joined", bRes)
          return bRes

    def waitSessionCreate(self, sessionName, nTimeout= - 1):
          bRes = self.__waitSessionOpen(self.groupHost, sessionName, nTimeout)
          self.__check("Verify whether the session (%s) is created" % (sessionName), bRes)
          return bRes    
           
    def waitSessionJoin(self, sessionName, nTimeout= - 1):
          bRes = self.__waitSessionOpen(self.groupAttendee, sessionName, nTimeout)
          self.__check("Verify whether the session (%s) is joined" % (sessionName), bRes)
          return bRes
              
    def waitSessionJoinForGroup(self, group, sessionName, nTimeout= - 1):
           bRes = self.__waitSessionOpen(group, sessionName, nTimeout)
           self.__check("Verify whether the session (%s) is joined" % (sessionName), bRes)
           return bRes
          
    def terminateHost(self):
          if self.groupHost.getCount() == 0:
                  return    
          self.__output("Start to terminate host")        
          return self.terminateForGroup(self.groupHost)
      
    def terminateAttendee(self):
          if self.groupAttendee.getCount() == 0:
                  return
          self.__output("Start to terminate attendees")
          return self.terminateForGroup(self.groupAttendee)
      
    def terminateTools(self):
          self.exitClient()
          self.terminateHost()
          self.terminateAttendee()
      
    def terminateForGroup(self, group):
          self.__terminateGroup(group)          
          self.groupHost = self.groupHost - group
          self.groupAttendee = self.groupAttendee - group  
                    
       
    def exitForGroup(self, group):
          if group.getCount() == 0:
                return
          self.__output("Start to exit group (%s)" % group.getName)           
          group.execute("wbxtf.sys.Exit")
          self.groupHost = self.groupHost - group
          self.groupAttendee = self.groupAttendee - group           
   
    def exitHost(self):
          if self.groupHost.getCount() == 0:
                return
          self.__output("Start to exit host")  
          self.groupHost.execute("wbxtf.sys.Exit")
          self.groupHost.clear()
      
    def exitAttendee(self):
          if self.groupAttendee.getCount() == 0:
                return
          self.__output("Start to exit attendees")
          self.groupAttendee.execute("wbxtf.sys.Exit")
          self.groupAttendee.clear()

    def exitClient(self):
          if len(self.objClients) == 0:
                return
          self.__output("Start to exit clients")   
          for client in self.objClients:
                handles = []
                handles.append(client["handle"])
                WBXTF.WBXTFStop(client["machine"], handles)
          self.objClients = []

    def exitTools(self):
          self.exitClient()
          self.exitAttendee()
          self.exitHost()     
          
    def verifyCommand(self, group, command, expectation, nTimeout = 30):
    	  self.__waitResult(group, command, expectation, nTimeout)    	     
      ##############################################
      ## Inside
      #############################################
    def   __runAttendee(self, sAttendeeMachines, nToolNum):
          if len(sAttendeeMachines) <= 0:
                return ASKGroup()
          self.__output("Start to run the %d attendees" % nToolNum)
          nEveryTool = int((nToolNum + len(sAttendeeMachines) - 1) / len(sAttendeeMachines))
          nRemained = nToolNum
          bRes = True
          group = ASKGroup()
          for machine in sAttendeeMachines:
                nTool = nEveryTool
                if nTool > nRemained:
                     nTool = nRemained
                if nTool == 0:
                    break
                
                objs = WBXTF.WBXTFRunObjects(machine, self.sToolPath, self.sParamAttendee, nTool, self.nTimeout)
                if len(objs) != nTool:
                    bRes = False
                    break
                self.groupAttendee.addList(objs)
                group.addList(objs)                
                nRemained = nRemained - nTool
          self.__check("Verify running attendees", bRes)        
          return group   
         
    def __checkResult(self, result, expectation):
		try:
			if result["rc"] != 0 or WBXTF.WBXTFEqualWithoutType(expectation, result["result"]["result"]) == False:
				return False
			return True	
		except Exception:
			return False

    def __checkResults(self, results, expectation, nCount = -1):
		  try:
				if nCount >= 0 and nCount != len(results):
					return False
				for res in results:										
					if res["result"]["rc"] != 0: 
						return False
					if WBXTF.WBXTFEqualWithoutType(expectation, res["result"]["result"]) == False:
						return False
				return True
		  except Exception:
				return False           
      
    def __checkResultsAsTrue(self, results, nCount= - 1):
    	  return self.__checkResults(results, 1, nCount)

    def __checkResultAsTrue(self, result):
    	  return self.__checkResult(result, 1)     
  	   
          
    def __mergeMachines(self):
          self.sMachines = []
          if len(self.sHostMachine) > 0:
                self.sMachines.append(self.sHostMachine)
          for machine in self.sAttendeeMachines:
                bSkip = False
                for tmp in self.sMachines:
                    if tmp == machine:
                          bSkip = True
                          break
                if not bSkip:
                    self.sMachines.append(machine)
                    
    def __waitResult(self, group, command, expectation, nTimeout):
          if nTimeout < 0:
              nTimeout = self.nTimeout
          lastTime = time.time()
          nowTime = lastTime
          while nowTime - lastTime < nTimeout:   
                ress = group.execute(command)
                if self.__checkResults(ress, expectation):
                    return True
                time.sleep(1)
                nowTime = time.time()
          return False 

    def __waitMeetingOpen(self, group, nTimeout):
    	  return self.__waitResult(group, "meeting.IsOpen()", 1, nTimeout) 
      
    def __waitSessionOpen(self, group, sessionName, nTimeout):
    	  return self.__waitResult(group, "%s.IsOpen()" % sessionName, 1, nTimeout) 

    def __updateMeetingInfoFromHost(self):
          if not self.bNeedUpateMeetingInfo:
                return True
          try:
                ress = self.sendToHost("config.GetMeetingID()")
                self.sConfMeetingID = ress[0]["result"]["result"]
                ress = self.sendToHost("config.GetMeetingKey()")
                self.sConfMeetingKey = ress[0]["result"]["result"]
                ress = self.sendToHost("config.GetMZMIP()")
                self.sConfMZM = ress[0]["result"]["result"]
                ress = self.sendToHost("config.GetMCCIP()")
                self.sConfMCC = ress[0]["result"]["result"]
                return True
          
          except Exception:
                return False

    def __updateMeetingToAttendee(self):
          try:
                self.SendToAttendee("config.SetMeetingID(%s)" % self.sConfMeetingID)
                self.SendToAttendee("config.SetMeetingKey(%s)" % self.sConfMeetingKey)                
                self.SendToAttendee("config.SetMZMIP(%s)" % self.sConfMZM)
                self.SendToAttendee("config.SetMCCIP(%s)" % self.sConfMCC)                
                return True          
          except Exception:
                return False
            
    def __updateMeetingToGroup(self, group):
          try:
                group.execute("config.SetMeetingID(%s)" % self.sConfMeetingID)
                group.execute("config.SetMeetingKey(%s)" % self.sConfMeetingKey)                
                group.execute("config.SetMZMIP(%s)" % self.sConfMZM)
                group.execute("config.SetMCCIP(%s)" % self.sConfMCC)                
                return True          
          except Exception:
                return False

    def __updateMeetingToHost(self):
          try:
                self.sendToHost("config.SetMeetingID(%s)" % self.sConfMeetingID)
                self.sendToHost("config.SetMeetingKey(%s)" % self.sConfMeetingKey)                
                self.sendToHost("config.SetMZMIP(%s)" % self.sConfMZM)
                self.sendToHost("config.SetMCCIP(%s)" % self.sConfMCC) 
                self.sendToHost("config.SetGDMEnable(%d)" % self.sGDMEnable)
                self.sendToHost("config.SetGDMParams(%s)" % self.sGDMParams)
                self.sendToHost("config.SetMeetingDName(%s)" % self.sMeetingDName)
                self.sendToHost("config.SetGDMDNameList(%s)" % self.sGDMDNameList)
                return True          
          except Exception,e:
                print e
                return False
            
    def __output(self, text, type=WBXTF.typeInfo):
          if self.bEnableTrace:
            WBXTF.WBXTFOutput(text, type)
           
    def __check(self, text, bExpress):
          if "m_enableIgnore" in dir(self) and self.m_enableIgnore:
            return    
          if self.bEnableTrace:         
            WBXTF.WBXTFCheck(text, bExpress)
          else:
            WBXTF.WBXTFCheck("", bExpress)   
            
    def __terminateGroup(self, group):
    	listHandles = []  
        for item in group.m_objs:
        	if item.nPort > 0:        		
        		WBXTF.WBXTFStop(item.sMachine, [item.nPort])
          
