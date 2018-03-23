#!/usr/bin/python
"""
This case is design for supplying base cases for test cases
You can get an example from PETA2.0/Examples/Case 

@author: $Author: russell $
@version: $Revision: 1.51 $
@license: Copyright Cisco-Webex Corp
"""

import WBXTF
import time
import sys
import string
import traceback
import OutPutter

#Define constant here
NORMAL_EXIT_CODE = "EUREKA_NORMAL_EXIT"

class ITestCase:
	"""
	The interface for every test case.
	"""
	m_Params = {};
	def __init__(self):
		pass
	
	def OnSetUp(self):
		"""
		OnSetUp is called first when we run a case.
		You can do some things about setup in the function. 
		"""
		self.onSetUp()
		pass
	
	def OnTearDown(self):
		"""
		OnTearDown is called before a case normally finish.
		You can do some things about tear down the environment.
		"""
		self.onTearDown()
		pass
	
	def OnRun(self):	
		"""
		This function is called when a case is running.
		It is called after OnSetUp().
		You can do the main steps in the functions.
		"""	
		self.onRun()
		pass
	
	def OnError(self, exception):
		"""
		When a check point fails, OnError() is called,
		and OnTearDown() is not called again.
		So you must tear down the environment inside the function.
		
		@type exception: WBXTFException\
		@param exception: the exception object 
		"""
		self.onError(exception)
		pass

	def OnFinished(self):
		pass

	#To add this function for verify case result. #July,15 2010 Atom 
	def OnVP(self):
		pass

	def onSetUp(self):
		pass
	
	def onTearDown(self):
		pass
	
	def onRun(self):
		pass
	
	def onError(self, exception):
		pass
	

	def SetParam(self, name, value):
		"""
		Set the parameters of the case
		
		@type name: any
		@param name: the parameter name
		@type value: any
		@param type: the value of the parameter			 
		"""
		if len(self.m_Params) == 0:
			self.m_Params = {}
		self.m_Params[name] = value;
		
	def Run(self):
		"""
		Call the function to run the case
		
		@rtype: None
		@return: None
		"""
		try:
			self.OnSetUp();
			self.OnRun();
			#To add this function for verify case result. #July,15 2010 Atom
			self.OnVP()
			self.OnTearDown();
			self.OnFinished()
		except Exception, e:
			self.OnError(e)
#			print sys.exc_info()
	
		
class BaseCase(ITestCase):
	"""
	This is a super class. All case must derive from it.
	But we do not recommend that your class inherits it directly. 
	"""
	m_MID = 0
	m_CID = 0
	m_AUTHOR = ''
	m_caseName = ""
	m_moduleName = ""
	m_info = None
	
	m_oldFun = None
	m_oldScope = None
	
	m_startTime = None
	m_version = 0
	def __init__(self,version = 0):
		self.m_version = version		
		
	def __delete__(self):
		pass
	
	def setID(self, idCase = -1, idModule = -1):
		"""
		Set the case id and the module id
		
		@type idCase: string
		@param idCase: the case id. If it is -1, not change it
		@type idModule: string
		@param idCase: the module id. If it is -1, not change it
		@rtype: None	 
		"""
		if idCase >= 0:
			self.m_CID = idCase
		if idModule >= 0:
			self.m_MID = idModule			
		
	def getInfo(self, name):
		"""
		Get the parameters
		  
		@type name: any
		@param name: the name of the parameter
		@rtype: any
		@return: the value of the parameter 
		"""	
		if self.m_info == None or not self.m_info.has_key(name):
			return None
		else:
			return self.m_info[name] 
				  
	def setInfo(self, name, value):
		"""
		Set the parameters of the case
		
		@type name: any
		@param name: the parameter name
		@type value: any
		@param type: the value of the parameter			 
		"""
		if self.m_info == None:
			self.m_info = {}
		if self.m_info.has_key(name) and self.m_info[name] == value:
			#->Russell @2010/5/26 
			#return	#override this statement for user will call outStatusAsFail with same key-value twice
			#in try exception
			self.onChangeInfo(name, value)
			#<-Russell @2010/5/26        	
		self.m_info[name] = value
		self.onChangeInfo(name, value) 
		
		
	def outInfo(self, name, value):
		"""
		same to setInfo
		
		@see: setInfo
		"""
		return self.setInfo(name, value) 
		   
	def outLog(self, type, log, more = None):
		"""
		Output trace
		
		@type type: string
		@param type: the log type. There are the following types:
			typeInfo, typeWarning, typeError, typeDebug, typeStep
		@type log: string
		@param log: the trace text
		@type more: string
		@param more: For extension  
		"""
		scope = {}
		if(self.m_version == 0):
                        scope['cid'] = self.m_CID
                        scope['mid'] = self.m_MID
                else:
                        scope['caseName'] = self.m_caseName
                        scope['moduleName'] = self.m_moduleName
		return WBXTF.WBXTFOutput(log, type, more, scope)   
	
	def verify(self, description, bRes):
		WBXTF.WBXTFCheck(description, bRes)
	  
	def outStatusAsPass(self, description = ""):
		"""
		Identify that the case is passed
		
		@type description: string
		@param description: the description   
		"""
		self.outInfo("status", "pass")
		if len(description):
			self.outLog(WBXTF.typeInfo, "%s" % (description))		 
						  
	def outStatusAsFail(self, description = ""):
		"""
		Identify that the case is failed
		
		@type description: string
		@param description: the description   
		"""
		self.outInfo("status", "fail")
		if len(description):
			self.outLog(WBXTF.typeError, "%s" % (description))
						
	def outProgress(self, fProgress):
		"""
		Identify the progress of the case
		
		@type fProgress: double
		@param fProgress: the progress value (0...1)   
		"""		
		self.outInfo("progress", fProgress)
 
	
	def Run(self):
		if WBXTF.WBXTFGetSysConfig(WBXTF.WBXTF_SYS_CONFIG_DEBUG) != True:
			try:
				self.onCaseBegin()
				self.__SaveScope()
				# Change the scope
				ITestCase.Run(self)
				# Restore the scope
				self.onCaseEnd()
				self.__RestoreScope()
			except Exception, e: 
				if str(e) == NORMAL_EXIT_CODE:
					return
				else:
					type, value, tb = sys.exc_info()
					TrackBackList = traceback.format_exception(type, value, tb)
					strContext = string.join(TrackBackList)
					WBXTF.WBXTFOutput(strContext,WBXTF.typeError)
					self.inError(WBXTF.WBXTFException('%s' % e))
		else:
				self.onCaseBegin()
				self.__SaveScope()
				# Change the scope
				ITestCase.Run(self)
				# Restore the scope
				self.onCaseEnd()
				self.__RestoreScope()			
		
	def __onError(self, error):
		self.outLog(WBXTF.typeError, "OnError: %s" % error.GetInfo())
		
	def __SaveScope(self):
		scope = {}
		if(self.m_version == 0):
                        scope['cid'] = self.m_CID
                        scope['mid'] = self.m_MID
                else:
                        scope['caseName'] = self.m_caseName
                        scope['moduleName'] = self.m_moduleName
		self.m_oldScope = WBXTF.WBXTFConfigOutputScope(scope)
		self.m_oldFun = WBXTF.WBXTFSetErrorFunAsStop(self.__onException) 
	
	def __RestoreScope(self):
		WBXTF.WBXTFConfigOutputScope(self.m_oldScope)
		WBXTF.WBXTFSetErrorFunAsStop(self.m_oldFun)	
		status = self.getInfo("status")
		self.m_oldFun = None
		self.m_oldScope = None 
		
	def __onException(self, exception):
		bPass = True
		bPass = self.OnError(exception)
		"""
		if 'onError' in dir(self):
			bPass = self.onError(exception)
		else:
			bPass = self.OnError(exception)
		"""
		self.onCaseEnd() 
		oldFun = self.m_oldFun 
		self.__RestoreScope()
							
		if(oldFun and (bPass == None or bPass == True)):
			oldFun(exception)
			
	def onEurekaException(self,exception):
		pass
	
	def onChangeInfo(self, name, value):
		if name == "status" and value == "pass":
			self.outLog(WBXTF.typeInfo, "Case Passed")
		elif  name == "status" and value == "fail":
			self.inError(WBXTF.WBXTFException("Case Failed"))
			
	def onCaseEnd(self):
		pass
	
	def onCaseBegin(self):
		self.m_startTime = time.localtime()
  
	def inError(self, exception):
		WBXTF.WBXTFError(exception.info, exception.type, 3)
		self.__onException(exception)
		
	def onSaveScope(self):
		self.__SaveScope()
	
	def onRestoreScope(self):
		self.__RestoreScope()
				  
class BaseEurekaCase(BaseCase):
	"""
	This is a base class for Eureka cases.
	If you write Eureka cases, your cases can inherit it.
	"""
	__caseExit = False
	__exitStatus = ""
	exeTearDown = False
	__writeTADB = True
	
	def onCaseEnd(self):
		if not self.__caseExit:
			if self.__exitStatus == "":
				if self.m_info == None:
					self.m_info = {}
					self.m_info["status"] = "GoNextIssue" 
				else:
					if not self.m_info.has_key("status"):
						self.m_info["status"] = "GoNextIssue"
				self.outLog(WBXTF.typeInfo, "Case Failed (default case exit value)")
			else:
				if self.m_info == None:
					self.m_info = {}
					self.m_info["status"] = self.__exitStatus
				else:
					if not self.m_info.has_key("status"):
						self.m_info["status"] = self.__exitStatus
				self.outLog(WBXTF.typeInfo, self.__exitStatus)				
		strStartTime = ""
		result = self.getInfo("status")
		if result == None:
			result = "Pass"
		if self.m_startTime != None:
			strStartTime = time.strftime('%Y-%m-%d %H:%M:%S', self.m_startTime)
		else:
			strStartTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		if len(sys.argv)>=2:			
			for arg in sys.argv[1:]:
				if arg=="W2DB" and self.__writeTADB == True:
					#->add param bIsEureka to support write case log into file.In previously,case log will write to PETA DB.
					WBXTF.WBXTFReportEurekaCaseLog(self.m_MID, self.m_CID, strStartTime, result, self.m_AUTHOR,bIsEureka=True)
					#Russell
					break		

	def flushLogToDB(self,mid,cid,result,author):
		if self.m_startTime != None:
			strStartTime = time.strftime('%Y-%m-%d %H:%M:%S', self.m_startTime)
		else:
			strStartTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		#=======================================================================
		# if result:
		#	self.outInfo("status", "Pass")
		# else:
		#	self.outInfo("status", "GoNextIssue")
		#=======================================================================
		WBXTF.WBXTFReportEurekaCaseLog(mid,cid,strStartTime,result,author)
		WBXTF.WBXTFClearLog()
		self.__writeTADB = False

	def changeExitStatus(self,exitStatus):
		self.__exitStatus = exitStatus
	
	def outStatusAsWarning(self,descrition = ""):
		self.outLog(WBXTF.typeWarning,"Case Warning")
	
	def outStatusAsPass(self, description = ""):
		"""
		Identify that the case is passed
		
		@type description: string
		@param description: the description   
		"""
		self.__caseExit = True
		self.outInfo("status", "Pass")
		if len(description) != 0:
			self.outLog(WBXTF.typeInfo, "%s" % (description))		 
						  
	def outStatusAsFail(self, description = ""):
		"""
		Identify that the case is failed
		
		@type description: string
		@param description: the description   
		"""
		self.__caseExit = True
		self.outInfo("status", "GoNextIssue")
		if len(description) != 0:
			self.outLog(WBXTF.typeError, "%s" % (description))

	def outStatusAsBlock(self, description = ""):
		"""
		Identify that the case is failed
		
		@type description: string
		@param description: the description   
		"""
		self.__caseExit = True
		self.outInfo("status", "BlockedIssue")
		if len(description) != 0:
			self.outLog(WBXTF.typeError, "%s" % (description))

	def onChangeInfo(self, name, value):
		if name == "status" and value == "Pass":
			self.outLog(WBXTF.typeInfo, "Case Passed")
			if not self.exeTearDown:
				self.OnTearDown()
			self.onCaseEnd()
			raise Exception,NORMAL_EXIT_CODE
			#sys.exit(NORMAL_EXIT_CODE)
		elif  name == "status" and value == "GoNextIssue":
			#To un-comment the below line , Atom
			self.outLog(WBXTF.typeError,"Case Failed")
			if not self.exeTearDown:
				self.OnTearDown()
			self.onCaseEnd()
			raise Exception,NORMAL_EXIT_CODE
			#sys.exit(NORMAL_EXIT_CODE)
		elif name == "status" and value == "BlockedIssue":
			self.outLog(WBXTF.typeError,"Module Failed")
			if not self.exeTearDown:
				self.OnTearDown()
			self.onCaseEnd()
			raise Exception,NORMAL_EXIT_CODE
			#sys.exit(NORMAL_EXIT_CODE)

	def onEurekaException(self,exception):
		isNormal = (str(exception) == NORMAL_EXIT_CODE)
		if isNormal:
			return
		else:
			#self.outLog(WBXTF.typeError, str(exception))
			if self.m_info == None:
				self.m_info = {}
				self.m_info["status"] = "GoNextIssue"
			else:
				self.m_info["status"] = "GoNextIssue"
			bPass = True
			if 'onError' in dir(self):
				bPass = self.onError(exception)
			else:
				bPass = self.OnError(exception)
			self.outLog(WBXTF.typeError, "Case Failed")
			if not self.__caseExit:
				self.outStatusAsFail()
			self.onCaseEnd()

	def inError(self, exception):
		#Atom modified for catch exception
		try:
			self.onEurekaException(exception)
		except:
			pass
		
	def Run(self):
		try:
			self.onCaseBegin()
			# Change the scope
			self.onSaveScope()
			ITestCase.Run(self)
			self.onCaseEnd()
			# Restore the scope
			self.onRestoreScope()
		except Exception, e: 
			if str(e) == NORMAL_EXIT_CODE:
				return
			else:
				type, value, tb = sys.exc_info()
				TrackBackList = traceback.format_exception(type, value, tb)
				strContext = string.join(TrackBackList)
				self.outLog(WBXTF.typeError, strContext)
				self.inError(WBXTF.WBXTFException('%s' % e))
				
class BaseTelephonyCase(BaseCase):
	"""
	This is a base class for Telephony cases.
	If you write Telephony cases, your cases can inherit it.
	"""
	def __init__(self):
		BaseCase.__init__(self)
		WBXTF.WBXTFSysConfig(WBXTF.WBXTF_SYS_CONFIG_STRINGRESULT, True)
		self.m_CaseStartTime = time.time()#Return the seconds since the epoch
		self.m_CaseExitCode = None; #the exit code when case execute finished or some errors occur
								  #0 --- success,  1---failure
		self.SetOutPutter(OutPutter.DefaultOutPutter())
		print "BaseTelephonyCase__init__"
		
	def GetExitCode(self):
		return self.m_CaseExitCode
	
	def SetOutPutter(self, outPutter):
		"""
		Set the specific output,  it can be log2db, text file, xml etc.
		We can use the subclass inherit from class IOutPutter,  It is more flexiable like this.
		"""
		self.__outPutter = outPutter
		self.__outPutter.BindWithTestCase(self)
		
	def outLog(self, type, log, more = None):
		return self.__outPutter.outLog(type,log)

	def InfoLog(self, log):
		return self.__outPutter.outLog(WBXTF.typeInfo,log)
	
	def WarningLog(self, log):
		return self.__outPutter.outLog(WBXTF.typeWarning,log)
	
	def ErrorLog(self, log):
		return self.__outPutter.outLog(WBXTF.typeError,log)
	
	def outStatusAsPass(self, description = ""):
		#self.outInfo("status", "pass")
		self.m_CaseExitCode = 0
		return self.__outPutter.outStatusAsPass(description)
	
	def outStatusAsFail(self, description = ""):
		#self.outInfo("status", "fail")
		#self.m_CaseExitCode = 1
		return self.__outPutter.outStatusAsFail(description)

	def __onException(self, exception):
		print "BaseTelephonyCase::__onException"
		self.m_CaseExitCode = 2
		self.OnError(exception)
		
	def Run(self):
		try:
			self.m_CaseExitCode = 0
			WBXTF.WBXTFSetErrorFunAsException(self.__onException)
			WBXTF.WBXTFSetErrorMode(WBXTF.modeException)
			self.onCaseBegin()
			# Change the scope
			ITestCase.Run(self)
			# Restore the scope
			self.onCaseEnd()
		except Exception, e: 
			self.m_CaseExitCode = 2
			type, value, tb = sys.exc_info()
			from org.telephony.BVT.BVTRetryCase_ErrorMessage import RetryErrorMessage
			#print RetryErrorMessage
			for errorMess in RetryErrorMessage:
				if errorMess in str(value):
					self.m_CaseExitCode = 11
					print "set m_CaseExitCode to 11"
			TrackBackList = traceback.format_exception(type, value, tb)
			self.ErrorLog("".join(TrackBackList))
			try:
				self.OnError("exception")
			except Exception, e:
				self.ErrorLog("".join(e))