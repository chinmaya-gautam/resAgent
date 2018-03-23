from string import lower
import threading
import thread
import time
import sys
import types
import os
import re
import string
import WBXTF
import WBXTFConfig
import smtplib
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from wbxtf.WBXTFLogex import *

typeStep = "stepInfo"
"""
Trace leve: case step infomation
"""

typeInfo = "info"
"""
Trace level: information
"""

typeError = "error"
"""
Trace level: error
"""

typeWarning = "warning"
"""
Trace level: warning
"""

typeCheck = "check"
"""
Trace level: check point
"""

typeDebug = "debug"
"""
Trace level: debug
"""

##############################################
## Class __WBXTFLogCallBack
##############################################
class WBXTFLogCallBack:
    m_listFuns = []
    def AddSink(self, fun):
        if fun in self.m_listFuns:
            return True
        self.m_listFuns.insert(0, fun)
        return True
            
    def RemoveSink(self, fun):
        if not fun in self.m_listFuns:
            return True
        self.m_listFuns.remove(fun)
        return True
            
    def OnLog(self, log):
        for fun in self.m_listFuns:
            fun(log)

            
################################################
## Class WBXTFLog
###############################################
class WBXTFLog(WBXTFLogCallBack):   
    m_scope = None
    m_logs = []
    m_lock = threading.RLock() 
    def __init__(self):
        WBXTFLogCallBack.AddSink(self, self.__outputToConsole)
                
    def output(self, sText, type = typeInfo, more = None, scope = None):
        """
        Output trace
        
        @type type:string
        @param type: trace type, there are the following stock type:
                    typeInfo, typeError, typeWarning, typeCheck, typeDebug
        @type more:any
        @param more: this is an extend parameter. It is design for the
                specific trace level
                For typeCheck, you can set more as True or False
        """
        log = {}
        log["log"] = sText
        log["type"] = type
        log["time"] = time.time()
        if scope != None:
           log["scope"] = scope 
        elif self.m_scope != None:
            log["scope"] = self.m_scope
        if more != None:
            log["more"] = more     
        self.m_lock.acquire()
        self.m_logs.append(log)   
        self.__onOutput(log) 
        self.m_lock.release()
        
    def outputError(self, sText):
        """
        Output trace
        
        @type sText: string
        @param sText: Trace text
        """    
        self.output(sText, typeError)
        
        
    def outputWarning(self, sText):

        """

        Output trace

        

        @type sText: string

        @param sText: Trace text

        """    

        self.output(sText, typeWarning)        
    
    def outputCheckPoint(self, sText, bPass = True):
        """
        Output trace
        
        @type sText: string
        @param sText: Trace text
        @type bPass: bool
        @param bPass: whether pass the check point  
        """       
        self.output(sText, typeCheck, bPass)  
            
    def configOutputScope(self, scope):
        old = self.m_scope
        self.m_scope = scope    
        return old     
                
    def getLog(self):
        """
        Get the trace log
        
        @rtype: list
        @return: the trace list
        """      
        return self.m_logs  

    def clearLog(self):
        """
        Clear the trace log
        
        @rtype: void
        @return: void
        """      
        self.m_logs = []

    def formatLog(self, log):
        try:
            sText = ""    
            sText = sText + "[" + time.strftime("%X", time.localtime(log["time"])) + "]"
            sText = sText + "[" + log["type"] + "]"
            if log.has_key("scope") and log["scope"].has_key("caseName"):
                sText = sText + "[caseName_" + '%s'%(log["scope"]["caseName"])+"]"
            elif log.has_key("scope") and log["scope"].has_key("cid"):
                sText = sText + "[cid_" + '%s' %(log["scope"]["cid"]) + "]"
            sText = sText + "[tid=%s]"%(thread.get_ident())
            sText = sText + '%s' % log["log"]
            if log["type"] == typeError:
                bStdError = True
            elif log["type"] == typeCheck:
                if log.has_key("more") and log["more"] == True:
                    sText = sText + " -- Passed"
                else:
                    sText = sText + " -- Failed" 
            return sText
        except Exception, e:
            return ""
            
    def __onOutput(self, log):
        WBXTFLogCallBack.OnLog(self, log)
        
    def __outputToConsole(self, log):
        sText = self.formatLog(log)
        bStdError = False 
        if log["type"] == typeError:
            bStdError = True         
        if bStdError:
            sText = sText + "\n"
            sys.stderr.write(sText)
            
            sys.stderr.flush()
        else:
            print(sText)  
            sys.stdin.flush() 
             
##############################################
## Class WBXTFBaseReport
##############################################
class WBXTFBaseReport:
    pass

class WBXTFCenterReport(WBXTFBaseReport):
    m_runID = 0
    m_caseID = 0
    m_moduleID = 0
    m_result = ''
    m_author = ''
    m_startTime = ''
    m_dbhost = ''
    m_dbuser = ''
    m_dbpassword = ''
    m_dbname = ''
    m_dbtable = ''
    m_log = None
    m_team = ''
    m_logServer = ''
    m_logPath = ''
    m_ciServer = '10.224.70.151'
    m_ciLogDirBase = 'D:/TaskManagerFolder/TestRun/'
    
    def __init__(self, log):
        self.m_log = log
        
    def setDB(self,dbhost,dbuser,dbpassword,dbname,dbtable):
        self.m_dbhost = dbhost
        self.m_dbuser = dbuser
        self.m_dbpassword = dbpassword
        self.m_dbname = dbname
        self.m_dbtable = dbtable
    
    def setInfo(self,runID,moduleID,caseID,startTime,strResult,strAuthor):
        self.m_runID = runID
        self.m_caseID = caseID
        self.m_moduleID = moduleID
        self.m_result = strResult
        self.m_author = strAuthor
        self.m_startTime = startTime

    def setLogInfo(self, team,logServer,logPath):
        self.m_team = team
        self.m_logServer = logServer
        self.m_logPath = logPath

    def sendLog(self):
        if len(self.m_team) == 0 or len(self.m_logServer) == 0 or len(self.m_logPath) == 0:
            return;
        
        request =  'copy file ' + self.m_logPath + ' todirectory ' + self.m_ciLogDirBase + self.m_team + '/' + str(self.m_runID) + ' tomachine ' +  self.m_ciServer
        print request
        sendLogResponse = WBXTF.g_wbxtfSTAF.submit(self.m_logServer, 'fs', request)
        if 0 != sendLogResponse.get('rc'):
            WBXTF.WBXTFOutput("Send additional log file failed!")
            WBXTF.WBXTFOutput(sendLogResponse)
            return True;
        return False;
    
    def report(self):
        print "report.........."
        conn = ""
        cur = ""
        try:
            print self.m_dbhost
            print self.m_author            
            strResult = self.m_result
            strStartTime = self.m_startTime
            strAuthor = self.m_author
            strlog = self.__formatLog()
            print strlog
            import MySQLdb
            print self.m_dbhost
            print self.m_dbuser
            conn = MySQLdb.connect(self.m_dbhost, self.m_dbuser, self.m_dbpassword, self.m_dbname)
            cur = conn.cursor()
            endTime = time.localtime()
            strendTime = time.strftime('%Y-%m-%d %H:%M:%S', endTime)
            strSQL = """insert into %s (version,endtime,runid,moduleid,caseid,result,starttime,strlog,author)values (%d, '%s', %d, %d, %d,'%s','%s','%s','%s')"""% (self.m_dbtable, 0, strendTime, int(self.m_runID),int(self.m_moduleID),int(self.m_caseID),strResult,strStartTime,strlog.replace("\\","\\\\").replace("'","\\'"),strAuthor)
            cur.execute(strSQL)
            cur.close()
            #conn.commit()
            conn.close()

            WBXTF.WBXTFOutput("Succeed to update report to WBXTFCenter DB")
            return True
        except Exception ,e:
            WBXTF.WBXTFOutput("Fail to report to WBXTFCenter DB exception:%s\n"% e)
            if cur != "":
                cur.close()
            if conn != "":
                conn.close()
            return False

    def __formatLog(self):
        sLog = ''
        for log in self.m_log.getLog():
            #if not log.has_key('scope'):
                #continue
            #if not log['scope'].has_key('cid'):
                #continue            
            #sCaseID1 = str(log['scope']['cid'])
            #sCaseID2 = str(self.m_caseID)
            #if sCaseID1 != sCaseID2:
                #continue
            sLog = sLog + self.m_log.formatLog(log)
            sLog = sLog + "\r\n"
        return sLog  
##############################################
## Class WBXTFMailReport
##############################################
class WBXTFMailReport(WBXTFBaseReport):
    m_SMTPServer = ""
    m_SMTPUser = ""
    m_SMTPPass = ""
    m_Sender = ""    
    m_log = None
    def __init__(self, log):
        self.m_log = log
    
    def configMail(self, smtp, sender = "", userName = "", passWord = ""):
        """
        Config the mail server
        
        You also config the mail by the environment
        smtp - WBXTF_MAIL_SERVER
        sender - WBXTF_MAIL_SENDER - WBXTF_MAIL_SENDER
        userName - WBXTF_MAIL_USER
        passWord - WBXTF_MAIL_PASSWORD
        @type sender: string
        @param sender: the email address of the sender
        @type userName: string
        @param userName: the username of the sender
        @type passWord: string
        @param passWord: the password of the sender
        """    
        self.m_SMTPServer = smtp
        self.m_SMTPUser = userName
        self.m_SMTPPass = passWord
        self.m_Sender = sender 
    
    def report(self, toMail, title = "Case Report"):
        """
        Send a report by mail
        
        @type toMail: string
        @param toMail: the mail address of the receivers
                    for example, "test@hf.wbeex.com;test1@hf.webex.com"
        @type title: string
        @param title: the mail title
        @see: WBXTFConfigMail
        """     
        if self.m_SMTPServer == "":
            self.m_SMTPServer = os.environ.get("WBXTF_MAIL_SERVER")
        if self.m_SMTPUser == "":
            self.m_SMTPUser = os.environ.get("WBXTF_MAIL_USER")
        if self.m_SMTPPass == "":
            self.m_SMTPPass = os.environ.get("WBXTF_MAIL_PASSWORD")
        if self.m_Sender == "":
            self.m_Sender = os.environ.get("WBXTF_MAIL_SENDER")
    
        if self.m_SMTPServer == None or len(self.m_SMTPServer) == 0:
            WBXTFOutput("Please indicate the mail server")
            return
        if self.m_SMTPServer == None or len(self.m_Sender) == 0:
            WBXTFOutput("Please indicate the mail sender")
            return     
           
        # Convert Text
        sMail = ""
        data = {}
        data["checkpoint_pass"] = 0
        data["checkpoint_fail"] = 0
        for log in self.m_log.getLog():
            type = log["type"]
            if not data.has_key(type):
                data[type] = 0
            data[type] = data[type] + 1                    
            if type == typeCheck:
                if log["more"]:
                    data["checkpoint_pass"] = data["checkpoint_pass"] + 1
                else:
                    data["checkpoint_fail"] = data["checkpoint_fail"] + 1 
       
        sMail = sMail + "<H3>Report</H3>"
        bPass = True
        if data.has_key(typeError) and data[typeError] > 0:
            bPass = False
        if data.has_key("checkpoint_fail") and data["checkpoint_fail"] > 0:
            bPass = False       
        sMail = sMail + '<table border="1" cellpadding="0" cellspacing="0">'
        sMail = sMail + "<tr><td>Total Logs</td><td width=50>%d</td></tr>" % len(self.m_log.getLog())
        if data.has_key(typeInfo) and data[typeInfo] > 0:
            sMail = sMail + "<tr><td>Information Logs</td><td>%d</td><tr>" % data[typeInfo]
        if data.has_key(typeWarning) and data[typeWarning] > 0:
            sMail = sMail + "<tr><td>Warning Logs</td><td>%d</td><tr>" % data[typeWarning]
        if data.has_key(typeError) and data[typeError] > 0:
            sMail = sMail + '<tr><td><font color="red">Error Logs</font></td><td><font color="red">%d</font></td><tr>' % data[typeError]
        if data.has_key(typeDebug) and data[typeDebug] > 0:
            sMail = sMail + "<tr><td>Debug Logs</td><td>%d</td><tr>" % data[typeDebug]        
        if data.has_key(typeCheck) and data[typeCheck] > 0:
            sMail = sMail + "<tr><td>Check Point Logs</td><td>%d</td><tr>" % data[typeCheck]           
        if data.has_key("checkpoint_pass") and data["checkpoint_pass"] > 0:
            sMail = sMail + '<tr><td><font color="green">Check Point Logs (Passed)</font></td><td><font color="green">%d</font></td><tr>' % data["checkpoint_pass"]
        if data.has_key("checkpoint_fail") and data["checkpoint_fail"] > 0:
            sMail = sMail + '<tr><td><font color="red">Check Point Logs (Failed)</font></td><td><font color="red">%d</font></td><tr>' % data["checkpoint_fail"]
    
        if bPass:
            sMail = sMail + '<tr><td><font color="green">Passed!</td><td></td></tr>'
        else:
            sMail = sMail + '<tr><td><font color="red">Failed!</td><td></td></tr>'      
        sMail = sMail + '</table>'          
        sMail = sMail + "<br><hr><p><H3>Logs</H3>"    
        for log in self.m_log.getLog():
            sHead = ""
            sEnd = ""
            sBody = ""
            color = ""
            type = log["type"]
            if not data.has_key(type):
                data[type] = 0
            data[type] = data[type] + 1                    
            if type == typeError:
                color = "red"
            elif type == typeWarning:
                color = "yellow"
            elif type == typeCheck:
                if log["more"]:
                    data["checkpoint_pass"] = data["checkpoint_pass"] + 1
                    color = "green"
                else:
                    data["checkpoint_fail"] = data["checkpoint_fail"] + 1
                    color = "red"
            elif type == typeDebug:
                color = "#666666"                                     
            if color != "":             
                sHead = '<font color = "%s">' % (color)
                sEnd = '</font>'                            
            sBody = self.m_log.formatLog(log)
            sMail = sMail + sHead
            sMail = sMail + sBody
            sMail = sMail + sEnd              
            sMail = sMail + "<br>"             
            
        strFrom = self.m_Sender
        strTo = toMail
        smtp = smtplib.SMTP()
        msgRoot = MIMEBase('multipart', 'mixed', boundary='BOUNDARY')
        msgRoot['Subject'] = title
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgAlternative = MIMEBase('multipart', 'mixed', boundary='BOUNDARY')
        msgRoot.attach(msgAlternative)    
        msgText = MIMEText(sMail, 'html')
        msgAlternative.attach(msgText)
        #smtp.set_debuglevel(1)
        smtp.connect(self.m_SMTPServer)
        if self.m_SMTPUser != None and len(self.m_SMTPUser) > 0:
            smtp.login(self.m_SMTPUser, self.m_SMTPPass)
        smtp.sendmail(strFrom, strTo, msgRoot.as_string())

##############################################
## Class WBXTFConsoleReport
##############################################
class WBXTFConsoleReport:
    m_log = None
    def __init__(self, log):
        self.m_log = log
            
    def report(self):
        """
        Ouput a report to stdout stream
        """     
        sText = "============ Report =============\r\n"
        data = {}
        data["checkpoint_pass"] = 0
        data["checkpoint_fail"] = 0
        for log in self.m_log.getLog(): 
            type = log["type"]
            if not data.has_key(type):
                data[type] = 0
            data[type] = data[type] + 1                    
            if type == typeCheck:
                if log["more"]:
                    data["checkpoint_pass"] = data["checkpoint_pass"] + 1
                else:
                    data["checkpoint_fail"] = data["checkpoint_fail"] + 1    
        bPass = True
        if data.has_key(typeError) and data[typeError] > 0:
            bPass = False
        if data.has_key("checkpoint_fail") and data["checkpoint_fail"] > 0:
            bPass = False       
        sText = sText + "Total Logs: %d\r\n" % len(self.m_log.getLog())
        if data.has_key(typeInfo) and data[typeInfo] > 0:
            sText = sText + "Information Logs: %d\r\n" % data[typeInfo]
        if data.has_key(typeWarning) and data[typeWarning] > 0:
            sText = sText + "Warning Logs: %d\r\n" % data[typeWarning]
        if data.has_key(typeError) and data[typeError] > 0:
            sText = sText + 'Error Logs: %d\r\n' % data[typeError]
        if data.has_key(typeDebug) and data[typeDebug] > 0:
            sText = sText + "Debug Logs: %d\r\n" % data[typeDebug]        
        if data.has_key(typeCheck) and data[typeCheck] > 0:
            sText = sText + "Check Point Logs: %d\r\n" % data[typeCheck]           
        if data.has_key("checkpoint_pass") and data["checkpoint_pass"] > 0:
            sText = sText + 'Check Point Logs (Passed): %d\r\n' % data["checkpoint_pass"]
        if data.has_key("checkpoint_fail") and data["checkpoint_fail"] > 0:
            sText = sText + 'Check Point Logs (Failed): %d\r\n' % data["checkpoint_fail"]
        if bPass:
            sText = sText + "Passed!\r\n"
        else:   
            sText = sText + "Failed!\r\n" 
        sText = sText + "-------------------------------\r\n"       
        print sText   
        
          
##############################################
## Class EurekaPETADBReport
##############################################
class EurekaPETADBReport:
    m_log = None
    m_host = ''
    m_user = ''
    m_password = ''
    m_db = ''
    m_db = ''
    m_runID = 0
    m_taskID = 0
    m_moduleID = 0
    m_caseID = 0
    m_result = ''
    m_author = ''
    m_startTime = ''
    
    #->support write case log into file.In previously,case log will write to PETA DB 
    m_bIsEureka=False    
    #<-Russell
    
    def __init__(self, log):
        self.m_log = log
        
    def setDB(self, host = 'localhost', user = 'root', passwd='', db = 'WBXPETADB'):
        self.m_host = host
        self.m_user = user
        self.m_password = passwd
        self.m_db = db        
    
    def setInfo(self, runID, taskID, moduleID, caseID, startTime, strResult, strAuthor,bIsEureka=False):
        #->add param bIsEureka to support write case log into file.In previously,case log will write to PETA DB
        self.m_runID = runID
        self.m_taskID = taskID
        self.m_moduleID = moduleID
        self.m_caseID = caseID    
        self.m_result = strResult
        self.m_author = strAuthor
        self.m_startTime = startTime
        
        #->support write case log into file.In previously,case log will write to PETA DB
        self.m_bIsEureka=bIsEureka
        #<-Russell
            
    def report(self):
#        print 'm_host:%s' % self.m_host
#        print 'm_user:%s' % self.m_user
#        print 'm_password:%s' % self.m_password
#        print 'm_db:%s' % self.m_db
#        print 'm_runID:%s' % self.m_runID
#        print 'm_taskID:%s' % self.m_taskID
#        print 'm_moduleID:%s' % self.m_moduleID
#        print 'm_caseID:%s' % self.m_caseID
#        print 'm_result:%s' % self.m_result
#        print 'm_author:%s' % self.m_author
#        print 'm_startTime:%s' % self.m_startTime
#        Added by polar
        conn = ""
        cur = ""
#        Added by polar
        try:            
            import MySQLdb
            conn = MySQLdb.connect(self.m_host, self.m_user, self.m_password, self.m_db)
            cur = conn.cursor() 
            strResult = self.m_result
            strAuthor = self.m_author
            strStartTime = self.m_startTime                
            # Format Log
            strLog = self.__formatHTMLLog()
            strLog = re.sub("\'"," ",strLog)
            strResult = self.__checkWarning(strResult, strLog)
            if self.m_bIsEureka:
                #create corresponding store dir and file to save case log
                import os
                slogParentPath='/opt/TA/logs/'
                sCaseStorePath=slogParentPath+'T'+str(self.m_taskID)+'/'+'M'+str(self.m_moduleID)+'/'
                if not os.path.exists(sCaseStorePath):                
                    #create log store dir
                    os.makedirs(sCaseStorePath)
                slogFileName='C'+str(self.m_caseID)+'.log'
                fd = file(sCaseStorePath+slogFileName,'a')                
                fd.write(strLog)
                fd.close()    
                strSQL = """insert into %s (runid,taskid,moduleid,caseid,result,starttime,log,author) values (%d,%d,%d,%d,'%s','%s','%s','%s')""" \
                % ('WBXCASERESULT',int(self.m_runID),int(self.m_taskID),int(self.m_moduleID),int(self.m_caseID),strResult,strStartTime,'RefTologFile',strAuthor)                           
            else:
                strSQL = """insert into %s (runid,taskid,moduleid,caseid,result,starttime,log,author) values (%d,%d,%d,%d,'%s','%s','%s','%s')""" % ('WBXCASERESULT',int(self.m_runID),int(self.m_taskID),int(self.m_moduleID),int(self.m_caseID),strResult,strStartTime,strLog,strAuthor)
            cur.execute(strSQL)
            cur.close()   #added by polar
            conn.close()  #added by polar
            scope = {}
            scope["cid"] = self.m_caseID
            scope["mid"] = self.m_moduleID
            WBXTFOutput("Succeed to update report to DB",scope = scope)
            return True
        except Exception, e:  
            import traceback
            traceback.print_exc()          
            if cur != "":
                cur.close()
            if conn != "":
                conn.close()
            #print e
            WBXTFOutput("Fail to update report to DB", WBXTF.typeWarning)
            return False
                        
    def __formatLog(self):
        sLog = ''
        for log in self.m_log.getLog():
            if not log.has_key('scope'):
                continue
            if not log['scope'].has_key('cid'):
                continue            
            sCaseID1 = str(log['scope']['cid'])
            sCaseID2 = str(self.m_caseID)
            if sCaseID1 != sCaseID2:
                continue
            sLog = sLog + self.m_log.formatLog(log)
            sLog = sLog + "\r\n"            
        return sLog       
    
    def __formatHTMLLog(self):
        sLog = ''
        for log in self.m_log.getLog():
            if not log.has_key('scope'):
                continue
            if not log['scope'].has_key('cid'):
                continue            
            sCaseID1 = str(log['scope']['cid'])
            sCaseID2 = str(self.m_caseID)
            if sCaseID1 != sCaseID2:
                continue
            sLine = self.m_log.formatLog(log)

            color = ''
            if log['type'] == typeWarning:
                    color = '#C8C800'
            elif log['type'] == typeStep:
                    color = 'blue'  
            elif log['type'] == typeError:
                    color = 'red'  
            elif log['type'] == typeCheck:
                if log.has_key("more"):               
                    color = 'green'
                else:
                    color = 'red'
            elif string.find(log['log'],'Case Passed') != -1:
                color = 'green'
            elif string.find(log['log'],'Case Failed') != -1:
                color = 'red'
            elif string.find(log['log'],'Module Failed') != -1:
                color = 'red'   
                
            if color != '':
                sLine = "<font color=%s><b>" % (color) + sLine + "</b></font>"
                                                                
            sLog = sLog + sLine            
            sLog = sLog + "\r\n"            
        return sLog    
    
    def __checkWarning(self,res,log):
        strWarningTag = "][warning]["
        if (string.find(log,strWarningTag) != -1):
            if (string.find(res,"Issue") != -1):
                return res
            else:
                return "Warning"
        else:
            return res
        
##############################################
## Global variables
##############################################
#global __g_log
__g_log = WBXTFLog()
global __g_MailReport
__g_MailReport = None


##############################################
## Global functions
############################################## 
def WBXTFLogAddFun(fun):
    """
    Register a callback function to process the logs
        >>> Example:
        def OnLog(log):
            print "==== Log in OnLog======="
            print log    
        WBXTF.WBXTFLogAddFun(OnLog)
        
        >>> Example:
        class Log:
            def OnLog(self, log):
                print "==== Log in Log::OnLog======="
                print log  
        logObj = Log()
        WBXTF.WBXTFLogAddFun(OnLog)
        
    @type fun: function 
    @param fun: a callback function for log.
                The function must has a param.
                The param is a dict. There are the follow items:
                log['type'], log['time'], log['log'] and etc.
    @rtype: bool
    @return: True
    @see: WBXTFLogRemoveFun
    """     
    __g_log.AddSink(fun)
   
    
def WBXTFLogRemoveFun(fun):
    """
    Unregister a callback function

    @type fun: function 
    @param fun: a callback function for log
    @see: WBXTFLogAddFun   
    """
    __g_log.RemoveSink(fun)   
    
              
def WBXTFConfigOutputScope(scope):
    return __g_log.configOutputScope(scope)

def WBXTFOutput(sText, type = typeInfo, more = None, scope = None):
    """
    Output trace
    
    @type type:string
    @param type: trace type, there are the following stock type:
                typeInfo, typeError, typeWarning, typeCheck, typeDebug
    @type more:any
    @param more: this is an extend parameter. It is design for the
            specific trace level
            For typeCheck, you can set more as True or False
    """
    #return __g_log.output(sText, type, more, scope)
    WBXTFLogInfo(sText)

def WBXTFOutputStep(sText, type = typeStep, more = None, scope = None):
    """
    Output step trace
    
    @type type:string
    @param type: trace type, there are the following stock type:
                typeInfo, typeError, typeWarning, typeCheck, typeDebug
    @type more:any
    @param more: this is an extend parameter. It is design for the
            specific trace level
            For typeCheck, you can set more as True or False
    """
    return __g_log.output(sText, type, more, scope)


    
def WBXTFOutputError(sText):
    """
    Output trace
    
    @type sText: string
    @param sText: Trace text
    """
    #return __g_log.outputError(sText)
    WBXTFLogError(sText)

def WBXTFOutputWarning(sText):
    #return __g_log.outputWarning(sText)
    WBXTFLogWarning(sText)

def WBXTFOutputCheckPoint(sText, bPass = True):
    """
    Output trace
    
    @type sText: string
    @param sText: Trace text
    @type bPass: bool
    @param bPass: whether pass the check point  
    """       
    return __g_log.outputCheckPoint(sText, bPass)
    
def WBXTFExit(nExit):
    """
    Exit the script
    
    @type nExit: integer
    @param nExit: the exit code 
    """     
    sys.exit(nExit)  
    
def WBXTFWarning(sText):
    """
    Call this function to indicate a warning
    
    @type sText: the message of the warning
    """      
    #WBXTFOutputWarning(sText)
    WBXTFLogWarning(sText)
    
def WBXTFGetLog():
    """
    Get the trace log
    
    @rtype: list
    @return: the trace list
    """      
    return __g_log.getLog()   

def WBXTFClearLog():
    """
    Clear the trace log
    @return: void
    """
    __g_log.clearLog()


def WBXTFGetLogObject():
    """
    Get the global log object 
    @rtype: 
    @return: the global log object
    """ 
    return __g_log

def WBXTFConfigMail(smtp, sender = "", userName = "", passWord = ""):
    """
    Config the mail server
    
    You also config the mail by the environment
    smtp - WBXTF_MAIL_SERVER
    sender - WBXTF_MAIL_SENDER - WBXTF_MAIL_SENDER
    userName - WBXTF_MAIL_USER
    passWord - WBXTF_MAIL_PASSWORD
    @type sender: string
    @param sender: the email address of the sender
    @type userName: string
    @param userName: the username of the sender
    @type passWord: string
    @param passWord: the password of the sender
    """     
    global __g_MailReport
    if __g_MailReport == None:
        __g_MailReport = WBXTFMailReport(__g_log)
    __g_MailReport.configMail(smtp, sender, userName, passWord)

def WBXTFReportByMail(toMail, title = "Case Report"):
    """
    Send a report by mail
    
    @type toMail: string
    @param toMail: the mail address of the receivers
                for example, "test@hf.wbeex.com;test1@hf.webex.com"
    @type title: string
    @param title: the mail title
    @see: WBXTFConfigMail
    """      
    global __g_MailReport
    if __g_MailReport == None:
        __g_MailReport = WBXTFMailReport(__g_log)
    return __g_MailReport.report(toMail, title)    
        
def WBXTFReportByStdout():
    """
    Ouput a report to stdout stream
    """      
    report = WBXTFConsoleReport(__g_log)
    return report.report()
   
def WBXTFReportEurekaCaseLog(moduleID, caseID, startTime, result, author,bIsEureka=False):
    dbInfo = WBXTFConfig.getEurekaPETADB()
    taskInfo = WBXTFConfig.getTaskID()
    if dbInfo['isEureka'] == False:
        return False        
    report = EurekaPETADBReport(__g_log)
    report.setDB(dbInfo['host'], dbInfo['user'], dbInfo['password'])    
    report.setInfo(taskInfo['runid'], taskInfo['taskid'], moduleID, caseID, startTime, result, author,bIsEureka)    
    return report.report()

def WBXTFCenterReportLog(dbhost,dbuser,dbpassword,dbname,dbtable,runID,moduleID, caseID, startTime, result, author, team='', logServer='', logPath=''):
    report = WBXTFCenterReport(__g_log)
    report.setDB(dbhost,dbuser,dbpassword,dbname,dbtable)
    report.setInfo(runID, moduleID, caseID, startTime, result, author)
    report.setLogInfo(team, logServer, logPath)
    report.sendLog()
    return report.report()
    

class WBXTFSectionLog:
    def __init__(self, bDisableTrace = False):
        self.__m_bEnableTrace = not bDisableTrace
        
    def enableTrace(self, bEnable):
        self.__m_bEnableTrace = bEnable
        
    def isEnabledTrace(self):
        try:
            return self.__m_bEnableTrace
        except:
            self.__m_bEnableTrace = True
            return True
    
    def trace(self, text):  
        if not self.isEnabledTrace():
            return                  
        WBXTF.WBXTFOutput(text, "trace")
        
    def traceSep(self):
        self.trace("-------------------")
        
    def traceTitle(self, title, add = None):
        extend = ""
        if add == None:
            extend = ""
        else:
            extend = "- %s " % (add)         
        self.trace("=============== %s %s=============" % (title, extend))
                                  
    def traceHead(self, head):
        self.trace('')
        self.traceTitle(head, "Start")
        
    def traceTail(self, tail):
        self.traceTitle(tail, " End ")
        
    
