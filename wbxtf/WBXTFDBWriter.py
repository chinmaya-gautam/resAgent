import WBXTF
#import WBXTFLog
import WBXTFDBI
import time

class CWBXTFDBWriter:
    def __init__(self):
        self.__m_db = WBXTFDBI.CWBXTFDBI() 

    def setupDB(self,host,user,passwd,database):
        self.__m_db.setupDB(host, user, passwd, database)

    def setRunInfo(self,runID,caseID):
        self.__m_runID = runID
        self.__m_caseID = caseID
        
    def writeCaseLogToDB(self):
        caseLogs = self.__formatGlobalCaseLog()        
        self.__m_db.updateCaseLog(self.__m_caseID,caseLogs)
        
    def writeStepsToDB(self):
        stepLogs = self.__formatGlobalSteps()
        self.__m_db.addSteps(self.__m_caseID, stepLogs)

    def setAutoWriteStep(self,bAuto = True):
        if(bAuto):
            WBXTF.WBXTFLogAddFun(self.onWriteStepFun)
        else:
            WBXTF.WBXTFLogRemoveFun(self.onWriteStepFun())
                        
    def onWriteStepFun(self,log):
        try:
            if(log["type"] == WBXTFLog.typeStep):
                self.writeStepToDB(log)
        except Exception,e:
            pass
    
    def writeStepToDB(self,log):
        if(log!=None and log!=""):
            logStr = WBXTF.WBXTFGetLogObject().formatLog(log)
            self.__m_db.addStep(self.__m_caseID, logStr)
        
    def __formatGlobalSteps(self):
        logs = WBXTF.WBXTFGetLog()
        stepInfos = []
        for log in logs:
            if(log["type"] == WBXTF.typeStep):
                stepInfos.append(log)
        logList = []
        for step in stepInfos:
            logStr = WBXTF.WBXTFGetLogObject().formatLog(step)
            logList.append(logStr)
        return logList
    
    def __formatGlobalCaseLog(self):
        sText = ""
        try:
            logs = WBXTF.WBXTFGetLog()
            for log in logs:
                sText += WBXTF.WBXTFGetLogObject().formatLog(log)
                sText += "\n"
        except Exception,e:
            pass
        return sText

    def updateCaseModuleCaseName(self,module_name,case_name):
        self.__m_db.updateCaseModuleCaseName(self.__m_caseID, module_name, case_name)
        
    def updateModuleCaseID(self,module_qa_id,case_qa_id):
        self.__m_db.updateCaseQaID(self.__m_caseID, module_qa_id, case_qa_id)

    def updateCaseStatus(self,status):
        self.__m_db.updateCaseStatus(self.__m_caseID,status)

    def getDB(self):
        return self.__m_db
    
"""    
test = DBWriter()
test.setDBInfo("10.224.70.88", "root", "wist1234", "wist")
rid = test.getDB().addRun("test", "", "2010-01-03 12:00:00", "START", "machine","email","No")
caseID = test.getDB().addCase(rid,"test", "testCASE", "case_description", "2010-01-03 12:00:00",  "START","")
print "caseID%d"%caseID
test.setRunInfo(rid,caseID)
test.setAutoWriteStep()
WBXTF.WBXTFOutputStep("ddddddddddddd1")
print test.getDB().getCaseStep(caseID)
"""
