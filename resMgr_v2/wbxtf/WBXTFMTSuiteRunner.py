import WBXTF
import WBXTFDBI 
import sys,threading
import time
from WBXTFMTSuiteHelper import CWBXTFSuiteHelper
from WBXTFDBReport import *
from WBXTF import WBXTFObject

DEFAULT_RUNTIME = 1*60
RUNPARAM_KEY_CASECFG = "cfgPath"
RUNPARAM_KEY_DBINFO = "DBInfo"
RUNPARAM_KEY_RUNINFO = "runInfo"

RUNSTATUS_START = "START"
RUNSTATUS_FINISH = "FINISH"
RUNSTATUS_FAIL = "FAIL"
RUNSTATUS_TIMEOUT = "TIMOUT"

def getLocalTime():
    """
    return the now time format:"%Y-%m-%d %H:%M:%S".
    """
    nowTime = time.gmtime()
    strNowTime = time.strftime('%Y-%m-%d %H:%M:%S', nowTime)
    return strNowTime

def WBXTFRunWaitReturn(sMachine, sPath, sParam = "", nTimeout = 60, returnStd = False):
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
    objProcess = WBXTFObject("staf://%s/process" % (sMachine))
    if returnStd:
        res = objProcess.Execute('Run(%s,%s, "WAIT %s STDERRTOSTDOUT RETURNSTDOUT ")' % (sPath, sParam, nTimeout * 1000))
    else:
        res = objProcess.Execute('Run(%s,%s, "WAIT %s")' % (sPath, sParam, nTimeout * 1000))
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

class CWBXTFCaseRunner():
    def __init__(self,casePath,caseCfg,DBInfo,runInfo,runMachine="local", maxTime = DEFAULT_RUNTIME):
        self.__m_casePath = casePath
        self.__m_caseCfg = caseCfg
        self.__m_DBInfo = DBInfo
        self.__m_runInfo = runInfo
        self.__m_runMachine = runMachine
        self.__m_maxTime = maxTime

    def runCase(self):
        paramStr = self.getRunCaseParamStr()
        cmd = "python %s "%(self.__m_casePath)
        cmd = cmd + paramStr
        print cmd
        res = WBXTFRunWaitReturn(self.__m_runMachine,cmd,"",self.__m_maxTime, returnStd = True)
        return res["rc"]

    def getRunCaseParamStr(self):
        paramStr = ""
        paramStr = paramStr + "/%s:%s "%(RUNPARAM_KEY_CASECFG,self.__m_caseCfg)
        paramStr += "/%s:"%RUNPARAM_KEY_DBINFO +"["
        paramStr = paramStr + "%s,%s,%s,%s"%(self.__m_DBInfo["host"],\
                                             self.__m_DBInfo["user"],\
                                             self.__m_DBInfo["passwd"],\
                                             self.__m_DBInfo["database"])
       
        paramStr += "] "
        paramStr += "/runInfo:" + "[" + "%s,%s"%(self.__m_runInfo["runID"],self.__m_runInfo["caseID"])+ "]"
        return paramStr
    
class CWBXTFSuiteRunner():
    def __init__(self,argv):
        self.__m_suiteFilePath = "D:/workspace/PETA2.0/wapi2.0/FeedServer/TestCases/TestModules/M5088_WAPI2.0_Feed_Server/suite.xml"
        self.__m_db = WBXTFDBI.CWBXTFDBI()
        self.__m_runInfo = {}
        self.__m_runParam = {}
        self.__m_caseInfo = {}
        self.__m_argv = argv
        self.__m_suiteInfo = {}
        self.__m_dbInfo = {"host":"10.224.54.181",\
                           "user":"root",\
                           "passwd":"ART",\
                           "database":"wist"}
        self.__m_suiteHelper = CWBXTFSuiteHelper()
        self.parseArgv(argv)
        self.__m_db.setupDB(self.__m_dbInfo["host"],\
                              self.__m_dbInfo["user"],\
                              self.__m_dbInfo["passwd"],\
                              self.__m_dbInfo["database"])
    
    def getSuiteInfo(self):
        return self.__m_suiteInfo

    def getRunParam(self):
        return self.__m_runParam
    
    def parseArgv(self,argv):
        if(argv != None):
            self.__m_suiteFilePath = argv
        self.__m_suiteHelper.setFilePath(self.__m_suiteFilePath)
        self.__m_suiteHelper.readSuiteRun()
        #caseInfo = self.__m_suiteHelper.getCaseInfos()
        dbInfo = self.__m_suiteHelper.getDBInfo()
        runParam = self.__m_suiteHelper.getRunParamInfo()
        suitesInfo = self.__m_suiteHelper.getSuitesInfo(runParam)
        self.__m_suiteInfo["suite"] = suitesInfo
        #self.__m_suiteInfo["case"] = caseInfo
        if(dbInfo!={}):
            self.__m_dbInfo = dbInfo
            self.__m_db.setupDB(self.__m_dbInfo["host"],\
                              self.__m_dbInfo["user"],\
                              self.__m_dbInfo["passwd"],\
                              self.__m_dbInfo["database"])
        self.__m_runParam = runParam
    
    def runSuite(self):
        """
        step 1: create an run, getRunId
        step 2: create Case with runID
        step 3: run case
        step 4: update case
        step 5: go to step2
        step 6: update run
        step 7: build report
        """
        runID = self.createRun()
        if(int(runID)>0):
            self.report(runID)

    
    def report(self,runID):
        report = CWBXTFDBReport()
        report.setupDB(self.__m_dbInfo["host"],self.__m_dbInfo["user"],\
                                 self.__m_dbInfo["passwd"],self.__m_dbInfo["database"])
        runInfo = report.getRunInfoByRunID(runID)
        strReport = ""
        print ""
        strReport += ""
        strReport += "\n"
        print "#######################Run result#################################"
        print "**********************General Info:*********************"
        strReport += "#######################Run result#################################"
        strReport +="\n"
        strReport += "**********************General Info:*********************"
        strReport +="\n"
   
        pass_amount= int(runInfo["pass_amount"])
        fail_amount = int(runInfo["fail_amount"])
        case_amount = int(runInfo["case_amount"])
        except_amount = int(runInfo["na_amount"]) +int(runInfo["running_amount"])
        print "\tstart_time:\t%s"%runInfo["start_time"]
        strReport += "\tstart_time:\t%s"%runInfo["start_time"]
        strReport += "\n" 
        print "\tend_time:\t%s"%runInfo["end_time"]
        strReport += "\tend_time:\t%s"%runInfo["end_time"]
        strReport += "\n"
        print "\trun_name:\t%s"%runInfo["run_name"]
        strReport += "\trun_name:\t\t%s"%runInfo["run_name"]
        strReport += "\n"
        print "\trun_id:\t\t%s"%runInfo["run_id"]
        strReport += "\trun_id:\t\t\t%s"%runInfo["run_id"]
        strReport += "\n"
        if(pass_amount == case_amount):
            print "\ttotal:\t%d, All pass."%case_amount
            strReport += "\ttotal:\t%d, All pass."%case_amount
            strReport += "\n"
        else:
            print "\ttotal:\t%d"%(case_amount)
            strReport += "\ttotal:\t%d"%(case_amount)
            strReport += "\n"
            if(case_amount>0):
                pass_rate = float(pass_amount)/float(case_amount)
                fail_rate = float(fail_amount)/float(case_amount)
                except_rate = float(except_amount)/float(case_amount)
                print "\tpass:\t%d(%1.2f)"%(pass_amount,pass_rate)
                strReport += "\tpass:\t%d(%1.2f)"%(pass_amount,pass_rate)
                strReport += "\n"
                print "\tfail:\t%d(%1.2f)"%(fail_amount,fail_rate)
                strReport += "\tfail:\t%d(%1.2f)"%(fail_amount,fail_rate)
                strReport += "\n"
                print "\texcept:\t%d(%1.2f)"%(except_amount,except_rate)
                strReport += "\texcept:\t%d(%1.2f)"%(except_amount,except_rate)
                strReport += "\n"
        print ""
        print "**********************Case Detail Info:*********************"
        strReport += ""
        strReport += "\n"
        strReport += "**********************Case Detail Info:*********************"
        strReport += "\n"
        #for key in runInfo.keys():
        #    print "\t%s:\t%s"%(key,runInfo[key])
        caseInfos = report.getCaseInfoByRunID(runID)
        for caseInfo in caseInfos:
            strReport += "\n"
            if caseInfo["case_status"] != "PASS":
                msg = "module:%s, case:%s result: %s ===================="%(caseInfo["module_name"],caseInfo["case_name"],caseInfo["case_status"])
                print msg
                strReport += msg
                print ""
                print "\t\tcase log:"
                strReport += "\t\tcase log:"
                strReport += "\n"
                caseLog = caseInfo["log"]
                caseLog = caseLog.replace("\n","\n\t\t\t")
                print "\t\t\t%s"%caseLog
                strReport += "\t\t\t%s"%caseLog
                strReport += "\n"
                print "\t\tstep Info:"
                strReport += "\t\tstep Info:"
                strReport += "\n"
                stepInfos= report.getStepInfoByCaseID(int(caseInfo["case_id"]))
                for stepInfo in stepInfos:
                    print "\t\t\t%s"%stepInfo
                    strReport += "\t\t\t%s"%stepInfo
                    strReport += "\n"
                print ""
                strReport += "\n"
    
            else:
                msg = "module:%s, case:%s result: %s\n"%(caseInfo["module_name"],caseInfo["case_name"],caseInfo["case_status"])
                strReport += msg
                print msg
        try:
            filePath = "C:/tmp/%s" % runID
            if(os.path.exists(filePath)==False):
                os.mkdir(filePath)
            nowTime = time.gmtime()
            strNowTime = time.strftime('%Y%m%d%H%M%S', nowTime)
            fileName = filePath + "/report_%s_%s_%s.txt"%(runInfo["run_name"],runInfo["run_id"],strNowTime)
            file_object = open(fileName, 'w')
            file_object.write(strReport)
            file_object.close()
        except Exception,e:
            print "save run info in localfile exception:%s"%(e)
        
    
    def getDB(self):
        return self.__m_dbInfo

    def getRunID(self):
        nowTime = getLocalTime()
        self.checkParam()
        self.__m_runParam["case_amount"] = 0
        for suite in self.__m_suiteInfo["suite"]:
            print suite
            self.__m_runParam["case_amount"] += len(suite["case"])
        runID = self.__m_db.addRun(self.__m_runParam["run_name"],\
                                   self.__m_runParam["run_description"],\
                               nowTime, RUNSTATUS_START ,\
                               self.__m_runParam["run_machine"],\
                               self.__m_runParam["case_amount"],\
                               self.__m_runParam["mail_to"],\
                               self.__m_runParam["send_mail"])           
        runID = int(runID)
        if(int(runID) <1):
            WBXTF.WBXTFError("CreateRun success,name=%s,description=%s"%(self.__m_runParam["run_name"],\
                                                                         self.__m_runParam["run_description"]))
        else:
            WBXTF.WBXTFOutput("CreateRun success,runID = %d,name=%s,description=%s"%(runID,\
                                                                        self.__m_runParam["run_name"],\
                                                                         self.__m_runParam["run_description"]))
        print "................................................................"
        return runID
    
    def suiteCaseRun(self, runID,suite):
        caseIndex = 1
        for case in suite["case"]:
            if(caseIndex%10==0):
                time.sleep(20)
            #time.sleep(1)
            print "suite %s, case %d, total:%d"%(suite["name"],caseIndex,len(suite["case"]))
            start_time = getLocalTime()
            caseID = self.__m_db.addCase(runID,start_time)
            caseID = int(caseID)
            if(int(caseID)<1):
                WBXTF.WBXTFError("CreateCase:%s Failed,"%(case["path"]))
            else:
                WBXTF.WBXTFOutput("CreateCase success,caseID=%d,path=%s"%(caseID,case["path"]))
            runInfo = {}
            runInfo["runID"] = runID
            runInfo["caseID"] = caseID
            formatCasePath = suite["base_path"]
            if(formatCasePath!=""):
                if(formatCasePath[len(formatCasePath)-1]!="/" and formatCasePath[len(formatCasePath)-1]!="\\"):
                    formatCasePath += "/"
            formatCasePath += case["path"]
            caseRunner = CWBXTFCaseRunner(formatCasePath,suite["config"],\
                                     self.__m_dbInfo,runInfo,\
                                     self.__m_runParam["run_machine"],\
                                     int(self.__m_runParam["case_time"]))
            res = caseRunner.runCase()
            if(int(res)!=0):
                WBXTF.WBXTFOutput("LoadCase failed,caseID=%d,path=%s"%(caseID,case["path"]))
                #self.__m_db.updateCaseStatus(caseID,RUNSTATUS_FAIL)
                #bFail = True
            else:
                WBXTF.WBXTFOutput("LoadCase success,caseID=%d,path=%s"%(caseID,case["path"]))
            endTime = getLocalTime()
            self.__m_db.updateCaseEndTime(caseID,endTime)
            caseIndex +=1     
           
    def createRun(self):
        runID = self.getRunID()
        thread_list = []
        for suite in self.__m_suiteInfo["suite"]:
            t=threading.Thread(target=self.suiteCaseRun,kwargs={'runID':runID,'suite':suite})
            t.start()
            thread_list.append(t)
        
        for threaditem in thread_list:
            while threaditem.isAlive():
                time.sleep(1)

        self.__m_db.updateRunStatus(runID,RUNSTATUS_FINISH)
        endTime = getLocalTime()
        self.__m_db.updateRunEndTime(runID,endTime)
        print "......................................................................."
        WBXTF.WBXTFOutput("Run finished,runID = %d,name=%s,descript=%s"%(runID,self.__m_runParam["run_name"],\
                                                                         self.__m_runParam["run_description"]))
        print "====================================================================="
        return runID
    
    def checkParam(self):
        for suite in self.__m_suiteInfo["suite"]:
            if(not suite.has_key("name")):
                suite["name"] = ""
            if(not suite.has_key("description")):
                suite["description"] = ""
            if(not suite.has_key("base_path")):
                suite["base_path"] = ""
            if(len(suite["case"])<1):
                WBXTF.WBXTFError("No Case to be run!")
                return False
            
            for case in suite["case"]:
                if((not case.has_key("path")) or case["path"]==""):
                    WBXTF.WBXTFError("Case path is null")
        
        if(self.__m_runParam=={}):
            WBXTF.WBXTFError("runParam is null")
            return False
        if(not self.__m_runParam.has_key("run_name")):
            self.__m_runParam["run_name"] = "NoName"

        if(not self.__m_runParam.has_key("run_description")):
            self.__m_runParam["run_description"] = ""
        if(not self.__m_runParam.has_key("run_machine")):
            self.__m_runParam["run_machine"] = "local" 
        if(not self.__m_runParam.has_key("config")):
            self.__m_runParam["config"] = "" 
        if(not self.__m_runParam.has_key("case_time")):
            self.__m_runParam["case_time"] = "1800" 
        if(not self.__m_runParam.has_key("mail_to")):
            self.__m_runParam["mail_to"] = "" 
        if(not self.__m_runParam.has_key("send_mail")):
            self.__m_runParam["send_mail"] = "NO" 
       
################################
## Entry Point
################################
if __name__ == '__main__':
    argv = None;
    if len(sys.argv) > 1:
        argv = sys.argv[1];
    suiteRun = CWBXTFSuiteRunner(argv);
    suiteRun.runSuite();

