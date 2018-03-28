import tempfile
import os
import ConfigParser
import string
import time
import smtplib
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage 
from WBXTFDBI import CWBXTFDBI


#################################################
# Config
#################################################
defaultBaseSection = "base"

configMainTemplate = 'ReportTemplate_Main.htm'
configCaseTemplate = 'ReportTemplate_Case.htm' 
configTitleTemplate = 'ReportTemplate_Title.htm' 

headCaseID = "{CASE_ID}"
headCaseName = "{CASE_NAME}"
headCaseResult = "{CASE_RESULT}"
headCaseColor = "{CASE_COLOR}"
headCaseResultColor = "{CASE_RESULT_COLOR}"
headCaseLink = "{CASE_LINK}"
headCaseCustomResult = "{CASE_CUSTOM_RESULT}"

headDuration = "{DURATION}"
headRunID = "{RUN_ID}"
headReportLink = "{REPORT_LINK}"
headOwner = "{OWNER}"
headOwnerMail = "{OWNER_MAIL}"
headYahooID = "{YAHOO_ID}"
headCasePass = "{CASE_PASS}"
headCaseFail = "{CASE_FAIL}"
headResult = "{RESULT}"
headResultColor = "{RESULT_COLOR}"
headCaseItems = "{CASE_ITEMS}"

headBuildID = "{BUILD_ID}"
headCaseNum = "{CASE_NUM}"
headStartTime = "{START_TIME}"
headEndTime = "{END_TIME}"
headTitle = "{TITLE}"

kTitle = "title"
kOwner = "owner"
kOwnerMail = "owner_mail"
kOwnerYahoo = "owner_yahoo"

kStartTime = "starttime"
kEndTime = "endtime"

kName = "name"
kResult = "result"
kCaseCustomResult = "CustomResult"

colorPassCaseColor = "black"
colorPassCaseResultColor = "green"
colorFailCaseColor = "red"
colorFailCaseResultColor = "red"

SMTPUser = "automail"
SMTPPass = "AutSendWe8008"
SMTPPort = 25
SMTPServer = "10.224.30.41"
SMTPFrom = "testtool@hf.webex.com"


configRunLink = "http://ta.webex.com.cn/tasche/reports/viewPythonBuildReport.action?projectCode=%s&buildNumber=%s&reportType=pythonReport&subReportType=byPythonBuildReport"
configCaseLink = "http://wbxtf.hf.webex.com/query/queryAllResult/"
        
class CWBXTFDBEmailReport:
    m_bLogCase = True
    m_mailTo_Pass = ""
    m_mailTo_Fail = ""
    m_SMTPServer = None
    m_SMTPPort = None
    m_SMTPUser = None
    m_SMTPPass = None
    m_mailFrom = None
      
    def __init__(self, project, build_id, run_id):
        self.project = project
        self.build_id = build_id
        self.run_id = run_id
        pass
    
    def setupDB(self,host, user, passwd, database):
        self.db = CWBXTFDBI()
        self.db.setupDB(host, user, passwd, database)
    
    def setMailTo(self, mail_pass, mail_fail = None):
        self.m_mailTo_Pass = mail_pass
        if mail_fail == None:
            self.m_mailTo_Fail = mail_pass
        else:
            self.m_mailTo_Fail = mail_fail
        
    def setMailServer(self, server, port, user, password, sender):
        self.m_SMTPServer = server
        self.m_SMTPPass = password
        self.m_SMTPPort = port
        self.m_SMTPUser = user
        self.m_mailFrom = sender
    
    def enableSelfLog(self, bEnable = True):
        self.m_bLogCase = bEnable

    def sendReport(self):
        context = self.__generateMainReport()
        who = ""
        if context[0]: # Pass
           who = self.m_mailTo_Pass
        else:
            who = self.m_mailTo_Fail     
        self.__sendMail(who, context[1], context[2])      
        
    def __sendMail(self, to, title, sMail):
    	if self.m_SMTPServer == None:
    	    self.m_SMTPServer = SMTPServer
    	if self.m_SMTPPort == None:
            self.m_SMTPPort = SMTPPort
        if self.m_SMTPUser == None:
            self.m_SMTPUser = SMTPUser
        if self.m_SMTPPass == None:
            self.m_SMTPPass = SMTPPass
        if self.m_mailFrom == None:
            self.m_mailFrom = SMTPFrom
        try:         
            smtp = smtplib.SMTP()
            msgRoot = MIMEBase('multipart', 'mixed', boundary='BOUNDARY')
            msgRoot['Subject'] = title
            msgRoot['From'] = self.m_mailFrom
            msgRoot['To'] = to
            rcpts = to.split(";")
            msgAlternative = MIMEBase('multipart', 'mixed', boundary='BOUNDARY')
            msgRoot.attach(msgAlternative)    
            msgText = MIMEText(sMail, 'html')
            msgAlternative.attach(msgText)
#            smtp.set_debuglevel(1)
            smtp.connect(self.m_SMTPServer)
            if self.m_SMTPUser != None and len(self.m_SMTPUser) > 0:
                smtp.login(self.m_SMTPUser, self.m_SMTPPass)
            smtp.sendmail(self.m_mailFrom, rcpts, msgRoot.as_string()) 
            return True
        except Exception, e:
            WBXTF.WBXTFOutput("Fail to send mail:%s" % (e), WBXTF.typeWarning)
            return False      
   

    def __generateCaseReport(self, caseID):
        caseID = '%s' % (caseID)
        
        reportContext = TemplateGenerator()
        reportContext.setTemplate(configCaseTemplate)   

        case_info = self.db.getCaseInfo(caseID)
        (run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, end, result, log) = case_info
        case_name = str(case_name)
        startTime = str(start)
        endTime = str(end)
        if str(result) == "PASS":
            result  = "pass"
        else:
            result = "fail"
            
        reportContext.addReplace(headCaseID, caseID)
        
        reportContext.addReplace(headCaseName, case_name)
        
        reportContext.addReplace(headCaseResult, result) 
        
        reportContext.addReplace(headCaseCustomResult, result) 
     
        if result == "pass":
            reportContext.addReplace(headCaseColor, colorPassCaseColor)
            reportContext.addReplace(headCaseResultColor, colorPassCaseResultColor)
        else:
            reportContext.addReplace(headCaseColor, colorFailCaseColor)
            reportContext.addReplace(headCaseResultColor, colorFailCaseResultColor)                  
        
        reportContext.generate()        
        return reportContext.getText()
     
    def __generateMainReport(self):
        #generate template
        reportContext = TemplateGenerator()
        reportContext.setTemplate(configMainTemplate)
        titleContext = TemplateGenerator()
        titleContext.setTemplate(configTitleTemplate)
                
        # Set Case
        reportContext.addReplace(headBuildID , self.build_id)  
        run_info = self.db.getRunInfo(self.run_id)
        (run_name, run_description, start_time,  end_time, run_status, run_machine, case_amount, mail_to, send_mail) = run_info

        reportContext.addReplace(headCaseNum, case_amount)        
        
        reportContext.addReplace(headStartTime, start_time)   
        
        reportContext.addReplace(headEndTime, end_time)
        
        title = self.__getDefaultTitle()
        reportContext.addReplace(headTitle, title) 
            
        # if starttime != None and endtime != None and float(endtime) > float(starttime):
        #     duration = self.__formatSecond(float(endtime) - float(starttime))
        # else:
        #     duration = None
        # reportContext.addReplace(headDuration, duration)    
        
        reportContext.addReplace(headRunID, self.run_id)
        reportContext.addReplace(headReportLink, (configRunLink % (self.project, self.build_id)))            
        
        reportContext.addReplace(headOwner, mail_to)   
               
        reportContext.addReplace(headOwnerMail, mail_to) 
        
        passCount = self.db.getAmountByStatus(self.run_id, "PASS")
        failCount = self.db.getAmountByStatus(self.run_id, "FAIL")

        reportContext.addReplace(headCasePass, passCount)
        reportContext.addReplace(headCaseFail, failCount)
        
        bPass = False
        if passCount == case_amount:
        #if failCount == 0:
            bPass = True
            
        if bPass:
            reportContext.addReplace(headResult, "PASS")
            reportContext.addReplace(headResultColor, "green")
        else:
            reportContext.addReplace(headResult, "FAIL")
            reportContext.addReplace(headResultColor, "red")
        
        caseText = ""
        cases = self.db.getCaseByRun(self.run_id)
        for case in cases:
            caseText +=  self.__generateCaseReport(case)        
        
        reportContext.addReplace(headCaseItems, caseText)
        
        titleContext.setRule(reportContext.getRule())        
        reportContext.generate() 
        titleContext.generate()               
        return [bPass, titleContext.getText(), reportContext.getText()]    
    
    
    def __formatSecond(self, sec):
        return '%dh%dm%ds' % ((sec / 3600), ((sec % 3600) / 60), sec % 60)
    
    def __getDefaultTitle(self):
        return "WAPI 2.0 Test Run %s Report" % self.run_id
    

        
class TemplateGenerator:
    m_path = "" 
    m_text = ""    
    def __init__(self):
        self.m_items = {}
     
    def setTemplate(self, template):
        self.m_path = template
        
        
    def addReplace(self, source, dest):
        if dest == None:
            dest = ""
        self.m_items[source] = dest
        
    def getRule(self):
        return self.m_items
    
    def setRule(self, rule):
        self.m_items = rule
    
    def generate(self):
        fp = open(self.m_path, "r")
        lines = fp.readlines()
        newlines = ""
        for line in lines:
            nPos = 0   
            newline = line         
            for k,v in self.m_items.items():                
                newline = newline.replace('%s' % (k), '%s' % (v))
            newlines += newline            
        fp.close()
        self.m_text = newlines                               
        
    def getText(self):
        return self.m_text     
            
     
# if __name__ == "__main__":

#     myreport = CWBXTFDBEmailReport("waip2.0", "qa_test", 463)
#     myreport.setupDB("10.224.65.45", "root", "wist1234", "wist")
#     myreport.setMailTo("haoran@hf.webex.com")
#     myreport.sendReport()
    
    
       
    



