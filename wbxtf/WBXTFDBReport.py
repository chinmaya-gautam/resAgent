
"""
Report module for WIST
Author: Haoran
"""
import time
import getopt, sys, os, re
import logging
import string
import cStringIO
from xml.dom.minidom import *
import calendar
import urllib, urllib2
from WBXTFDBI import CWBXTFDBI


class CWBXTFDBReport():
    def __init__(self):
        pass

    def setupDB(self,host, user, passwd, database):
        self.db = CWBXTFDBI()
        self.db.setupDB(host, user, passwd, database)

    def genRunReportByRunID(self, run_id, filename):
        run_info = self.db.getRunInfo(run_id)
        (run_name, run_description, start_time,  end_time, run_status, run_machine, case_amount, mail_to, send_mail) = run_info
        if run_status == "START":
            end_time = "Running"
        #('PASS', 3L), ('FAIL', 1L))
        case_result = {'PASS':0,'FAIL':0,'TIMEOUT':0,'NA':0,'START':0,}
        case_result_db = self.db.getAmountByStatus(run_id)
        for case_status in case_result_db:
            if case_result.has_key(case_status[0]):
                case_result[case_status[0]] = case_status[1]
        file_object = open(filename, 'a+')
        file_object.write("Test Run %d Summary\n" % run_id);
        file_object.write("RunID,Run Name,Run Description,Start Time,End Time,")
        file_object.write("Case Amount,Pass,Fail,Timeout,NA,Running\n")
        file_object.write("%s,%s,%s,%s,%s," % (run_id, run_name, run_description, start_time, end_time))
        file_object.write("%s,%s,%s,%s,%s,%s\n\n" % (case_amount, case_result['PASS'], 
                                                     case_result['FAIL'], case_result['TIMEOUT'], 
                                                     case_result['NA'], case_result['START']))
        file_object.close()
    
    # Return the run info in map by run_id
    def getRunInfoByRunID(self, run_id):
        run_info_db = self.db.getRunInfo(run_id)
       
        (run_name, run_description, start_time,  end_time, run_status, run_machine, case_amount, mail_to, send_mail) = run_info_db
        if run_status == "START":
            end_time = "Running"
        pass_amount = self.db.getAmountByStatus(run_id, 'PASS')
        fail_amount =  self.db.getAmountByStatus(run_id, 'FAIL')
        timeout_amount = self.db.getAmountByStatus(run_id, 'TIMEOUT')
        na_amount = self.db.getAmountByStatus(run_id, 'NA')
        running_amount = self.db.getAmountByStatus(run_id, 'START')
        run_info = {}
        run_info["run_id"] = run_id
        run_info["run_name"] = run_name
        run_info["run_description"] = run_description
        run_info["start_time"] = start_time
        run_info["end_time"] = end_time
        run_info["run_status"] = run_status
        run_info["run_machine"] = run_machine
        run_info["case_amount"] = case_amount
        run_info["mail_to"] = mail_to
        run_info["send_mail"] = send_mail
        run_info["pass_amount"] = pass_amount
        run_info["fail_amount"] = fail_amount
        run_info["timeout_amount"] = timeout_amount
        run_info["na_amount"] = na_amount
        run_info["running_amount"] = running_amount
        return run_info

    def genCaseReportByRunID(self, run_id, filename):
        file_object = open(filename, 'a+')
        file_object.write("Test Cases Info for RunID %s\n" % run_id)
        file_object.write("Case ID, QA Forum ID, Case Name, Case Description, Start Time, End Time, Status,log\n")
        run_cases = self.db.getCaseByRun(run_id)
        for case_id in run_cases:
            case_info = self.db.getCaseInfo(case_id)
            (run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, end, status, log) = case_info
            if status == "START":
                status = "Running"
            file_object.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (case_id, case_qa_id, case_name, case_description, start, end, status,log)) 
        file_object.write("\n\n")
        file_object.close()

    # Return all the cases info in list by run_id, the element in list is a map
    def getCaseInfoByRunID(self, run_id):
        cases_info = []
        run_cases = self.db.getCaseByRun(run_id)
        for case_id in run_cases:
            case_info_db = self.db.getCaseInfo(case_id)
            (run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, end, status, log) = case_info_db
            if status == "START":
                status = "Running"
            case_info = {}
            case_info["case_id"] = case_id
            case_info["run_id"] = run_id
            case_info["module_qa_id"] = module_qa_id
            case_info["module_name"] = module_name
            case_info["case_qa_id"] = case_qa_id
            case_info["case_name"] = case_name
            case_info["case_description"] = case_description
            case_info["start_time"] = start
            case_info["end_time"] = end
            case_info["case_status"] = status
            case_info["log"] = log
            cases_info.append(case_info)
        return cases_info

    # Return the case info in map by case_id
    def getCaseInfoByCaseID(self, case_id):
        case_info_db = self.db.getCaseInfo(case_id)
        (run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, end, status, log) = case_info_db
        if status == "START":
            status = "Running"
        case_info = {}
        case_info["case_id"] = case_id
        case_info["run_id"] = run_id
        case_info["module_name"] = module_name
        case_info["case_name"] = case_name
        case_info["case_description"] = case_description
        case_info["start_time"] = start
        case_info["end_time"] = end
        case_info["case_status"] = status
        case_info["log"] = log
        return case_info

    def genStepReportByCaseID(self, case_id, filename):
        file_object = open(filename, 'a+')
        case_info = self.db.getCaseInfo(case_id)
        (run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, end, status, log) = case_info
        if status == "START":
            status = "Running"
        file_object.write("Steps for CaseID:%s Case Name:%s Status: %s\n" % (case_id, case_name, status))
        file_object.write("Step,Description\n")
        steps_info = self.db.getCaseStep(case_id)
        if steps_info == []:
            pass
        i = 1
        for step in steps_info:
            file_object.write("%d,%s\n" % (i, step))
            i = i + 1
        file_object.close()

    # Return the steps info in list by case_id
    def getStepInfoByCaseID(self, case_id):
        steps_info = []
        steps_info_db = self.db.getCaseStep(case_id)
        if steps_info_db == []:
            return []
        for step in steps_info_db:
            steps_info.append(step)
        return steps_info
    

class CWBXTFXMLReport: 
    def __init__(self, project, build, run_id,mailTo=""):
        self.mailTo = mailTo
        print "mailTo: %s"%self.mailTo
        self.projectCode = project
        self.buildNum = build
        self.run_id = run_id
        self.suite_name = "default"        
        self.case_name = ''
        self.result = ''                                                      
        self.startTime = ''       
        self.endtime = ''
        self.case_id = ''
        self.nowTime = time.strftime("%Y%m%d",time.localtime())

    def setupDB(self,host, user, passwd, database):
        self.db = CWBXTFDBI()
        self.db.setupDB(host, user, passwd, database)
        run_info = self.db.getRunInfo(self.run_id)
        (run_name, run_description, start, end, status, run_machine, case_amount, mail_to, send_mail) = run_info

        passed = self.db.getAmountByStatus(self.run_id, "PASS")
        failed = self.db.getAmountByStatus(self.run_id, "FAIL")
        total = case_amount
        ratio = (passed * 100) / total
        
        self.total = str(total)
        self.passed = str(passed)
        self.failed = str(failed)
        self.ratio = str(ratio)
        self.modStart = str(start)
        self.modEnd = str(end)
        self.suite = ''
    
    def genXMLReport(self):
        print "Create XML Report"
        impl = getDOMImplementation()
        self.doc = impl.createDocument(None, "report", None)
        self.root = self.doc.documentElement
        self.createReport(self.doc, self.root)
        
        cases = self.db.getCaseByRun(self.run_id)
        for case in cases:
            case_info = self.db.getCaseInfo(case)
            (run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, end, status, log) = case_info
            self.case_id = str(case)
            self.case_name = str(case_name)
            self.startTime = str(start)
            self.endTime = str(end)
            if str(status) == "PASS":
                status = "pass"
            self.result = str(status)
            self.log = str(log)
            self.createCase(self.doc)
            
        #print self.doc.toprettyxml(encoding='utf-8')        
        
        return True
    
    def createElement(self, doc, name, value):
        e = doc.createElement(name)
        e.appendChild(doc.createTextNode(value))
        return e
    
    def createCDATAElement(self, doc, name, value):
        e = doc.createElement(name)
        e.appendChild(doc.createCDATASection(value))
        return e
    
    def createReport(self, doc, parent):

        self.suite = doc.createElement('suite')
        self.suite.setAttribute('name',self.suite_name)#add suitename  
        self.suite.appendChild(self.createElement(doc, 'startTime', self.modStart))
        self.suite.appendChild(self.createElement(doc, 'endTime', self.modEnd))
            
        testcase = doc.createElement('testCases')
        testcase.appendChild(self.createElement(doc, 'total', self.total)) #add total
        testcase.appendChild(self.createElement(doc, 'passed', self.passed))
        testcase.appendChild(self.createElement(doc, 'failed', self.failed))
        testcase.appendChild(self.createElement(doc, 'passRatio', self.ratio))
     
        parent.appendChild(self.createElement(doc, 'projectCode', self.projectCode))#add project
        parent.appendChild(self.createElement(doc, 'buildNumber', self.buildNum))#add build
        parent.appendChild(self.createElement(doc, "mailTo", self.mailTo))
        parent.appendChild(testcase)
        parent.appendChild(self.suite) 
                       
    def createCase(self, doc):
        runtime = doc.createElement('runtime')
        runtime.appendChild(self.createElement(doc, 'begin', self.startTime))
        runtime.appendChild(self.createElement(doc, 'end', self.endTime))
        
        message = doc.createElement('messages')
        message.appendChild(self.createElement(doc, 'failure', 'N/A'))#failue message
        message.appendChild(self.createElement(doc, 'success', 'N/A'))#success message
        
        result = doc.createElement('result')
        result.appendChild(self.createElement(doc, 'status', self.result))
        result.appendChild(runtime)
        result.appendChild(self.createElement(doc, 'expected', 'N/A'))
        result.appendChild(message)
            
        case = doc.createElement('case')
        case.setAttribute('name', self.case_name)
        case.setAttribute('id', self.case_id) 
        case.appendChild(self.createElement(doc, 'input', 'N/A'))      
        case.appendChild(result)
        
        self.suite.appendChild(case)
              
        if self.log: 
            text = str(self.log)       
            case.appendChild(self.createCDATAElement(doc, 'reportData', text))
    
    def saveAs(self, filename):
        self.genXMLReport()
        f = open(filename, 'w')
        f.write(self.doc.toprettyxml(encoding='utf-8'))
        f.close()
        
    
    def uploadToTAScheduler(self,suiteName):
        self.suite_name = suiteName                    
        self.genXMLReport()
        reportData = self.doc.toprettyxml(encoding='utf-8')
        try:
            params = urllib.urlencode({'reportData': reportData})
            f = urllib2.urlopen("http://ta.webex.com.cn/tasche/reports/insertPythonReport.action", params)
        except:
            t, e  = sys.exc_info()[:2]
            print "Upload => %s: %s" % (t.__name__, e)
        else:
            #print "Upload => %s" % f.read()
            f.close()


# if __name__ == "__main__":
#     report = CWBXTFXMLReport("waip2.0", "qa_test", 463)
#     report.setupDB("10.224.65.45", "root", "wist1234", "wist")
#     report.saveAs("test001.xml")
    

# if __name__ == "__main__":
#     report = CWBXTFDBReport()
#     report.setupDB("10.224.70.88", "root", "wist1234", "wist")

#     report.genRunReportByRunID(261, "report.csv")
#     report.genCaseReportByRunID(261, "case.csv")
#     report.genStepReportByCaseID(173, "step.csv")
    
#     res = report.getRunInfoByRunID(261)
#     print res
    
#     res = report.getCaseInfoByRunID(261)
#     print res

#     res = report.getStepInfoByCaseID(488)
#     print res
   

