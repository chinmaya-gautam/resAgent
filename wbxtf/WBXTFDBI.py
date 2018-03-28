
"""
Database module for WIST
Author: Haoran
"""

import MySQLdb

class CWBXTFDBI():
    
    def __init__(self,host="", user="", passwd="", database=""):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._database = database  
        
    def setupDB(self, host, user, passwd, database):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._database = database        
    
    # Add new test run to database.
    # Special parameters:
    #   status: 'START','FINISH'
    #   start_time: "YYYY-MM-DD HH:MM:SS"
    #   send_mail: 'YES', 'NO'
    # Return the auto increased run_id
    def addRun(self, run_name, run_description, start_time,  status, run_machine, case_amount, mail_to, send_mail):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "insert into %s.run_info (run_name, run_description, start, status, run_machine, case_amount, mail_to, send_mail) values ('%s', '%s', '%s', '%s',  '%s', '%s', '%s', '%s');" % (self._database, run_name, run_description, start_time, status, run_machine, case_amount, mail_to, send_mail)
            cur.execute(sql)
            conn.commit()
            sql = " select @@identity;"
            cur.execute(sql)
            run_id = cur.fetchone()        
            cur.close()
            conn.close()
            return run_id[0]
        except Exception, e:
            print "addRun encounter exception: %s" % e 
            return 0
    
    # Add new test case to database.
    # Special parameters:
    #   status: 'START','PASS','FAIL','TIMOUT','NA'
    #   start_time: "YYYY-MM-DD HH:MM:SS"
    # Return the auto increased case_id
    def addCase(self, run_id, start_time,  status = "START", module_qa_id = 0 , module_name = "", case_qa_id = 0, case_name = "", case_description = "", log = ""):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "insert into %s.case_info (run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, status, log) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (self._database, run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start_time, status, log)
            #print sql
            cur.execute(sql)
            conn.commit()
            sql = " select @@identity;"
            cur.execute(sql)
            case_id = cur.fetchone()        
            cur.close()
            conn.close()
            return case_id[0]
        except Exception, e:
            print "addCase encounter exception: %s " % e
            return 0
            

    # Add step with case_id
    # Return the step_id
    def addStep(self, case_id, step_description):
        try:
            step_description = step_description.replace("\\","\\\\").replace("'","\\'")
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "insert into %s.step_info (step_description) values('%s');" % (self._database, step_description)
            cur.execute(sql)
            conn.commit()
            sql = "select @@identity;"
            cur.execute(sql)
            step_id = cur.fetchone()
            sql = "insert into %s.case_step ( case_id, step_id) values ('%s', '%s');" % (self._database,  case_id, step_id[0])
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return step_id[0]
        except Exception, e:
            print "addStep encounter exception: %s" % e
            return 0
    
    # Add steps with case_id
    # Return the step_id array  
    def addSteps(self, case_id, step_description_array):
        try:
            step_id_array = []
            for step in step_description_array:
                step_id = self.addStep(case_id, step)
                step_id_array.append(step_id)
            return step_id_array
        except Exception, e:
            print "addSteps encounter exception: %s" % e
            return []

    #Update run status: 'START','FINISH'
    def updateRunStatus(self, run_id, status):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "update %s.run_info set status = '%s' where run_id = '%s' ;" % (self._database, status, run_id)
            success = cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return success
        except Exception, e:
            print "updateRunStatus encounter exception: %s" % e
            return 0

    # Update case status: 'START','PASS','FAIL','TIMOUT','NA'
    def updateCaseStatus(self, case_id, status):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "update %s.case_info set status = '%s' where case_id = '%s' ;" % (self._database, status, case_id)
            #print sql
            success = cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return success
        except Exception, e:
            print "updateCaseStatus encounter exception: %s" % e 
            return 0
    
    # Update case log
    def updateCaseLog(self, case_id,log):
        try:
            log = log.replace("\\","\\\\").replace("'","\\'")
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "update %s.case_info set log = '%s' where case_id = '%s' ;" % (self._database, log, case_id)
            success = cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return success
        except Exception, e:
            print "updateCaseLog encounter exception: %s" % e
            return 0
        

    # Update run end time: "YYYY-MM-DD HH:MM:SS"
    def updateRunEndTime(self, run_id, end_time):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "update %s.run_info set end = '%s' where run_id = '%s' ;" % (self._database, end_time, run_id)
            success = cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return success
        except Exception, e:
            print "updateRunEndTime encounter exception: %s" % e 
            return 0

    # Update case end time: "YYYY-MM-DD HH:MM:SS"
    def updateCaseEndTime(self, case_id, end_time):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "update %s.case_info set end = '%s' where case_id = '%s' ;" % (self._database, end_time, case_id)
            success = cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return success
        except Exception, e:
            print "updateCaseEndTime encounter exception: %s" % e
            return 0

    # Update case qa_id: "YYYY-MM-DD HH:MM:SS"
    def updateCaseQaID(self, case_id, module_qa_id, case_qa_id):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "update %s.case_info set module_qa_id = '%s', case_qa_id = '%s' where case_id = '%s' ;" % (self._database, module_qa_id , case_qa_id, case_id)
            success = cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return success
        except Exception, e:
            print "updateCaseEndTime encounter exception: %s" % e
            return 0

    # Update case qa_id: "YYYY-MM-DD HH:MM:SS"
    def updateCaseModuleCaseName(self, case_id, module_name, case_name):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "update %s.case_info set module_name = '%s', case_name = '%s' where case_id = '%s' ;" % (self._database, module_name , case_name, case_id)
            success = cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
            return success
        except Exception, e:
            print "updateCaseModuleCaseName encounter exception: %s" % e
            return 0
        
    # Get run info
    # Return (run_name, run_description, start, end, status, run_machine, mail_to, send_mail)
    def getRunInfo(self, run_id):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "select run_name, run_description, start, end, status, run_machine, case_amount, mail_to, send_mail from  %s.run_info where run_id = '%s' ;" % (self._database, run_id)
            cur.execute(sql)
            run_info = cur.fetchone()
            cur.close()
            conn.close()
            return run_info
        except Exception, e:
            print "getRunInfo encounter exception: %s" % e 
            return ""


    # Get case info 
    # Return (run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, end, status, log)
    def getCaseInfo(self, case_id):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "select run_id, module_qa_id, module_name, case_qa_id, case_name, case_description, start, end, status, log from %s.case_info where case_id = '%s' ;" % (self._database, case_id)
            cur.execute(sql)
            case_info = cur.fetchone()
            cur.close()
            conn.close()
            return case_info
        except Exception, e:
            print "getCaseInfo encounter exception: %s" % e
            return ""

    # Get case id array by run id
    def getCaseByRun(self, run_id):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "select case_id from %s.case_info where run_id = '%s' order by case_id;" % (self._database, run_id)
            cur.execute(sql)
            case_id_array = []
            while True:
                case_id = cur.fetchone()
                if not case_id:
                    break
                case_id_array.append(case_id[0])
            cur.close()
            conn.close()
            return case_id_array
        except Exception, e:
            print "getCaseByRun encounter exception: %s" % e
            return [] 
    
    # Get step description array by case id
    def getCaseStep(self, case_id):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            sql = "select step_id from %s.case_step where case_id = '%s' order by step_id ;" % (self._database, case_id)
            cur.execute(sql)
            step_id_array = []
            while True:
                step_id = cur.fetchone()
                if not step_id:
                    break
                step_id_array.append(step_id[0])
            step_info_array = []
            for id in step_id_array:
                sql = "select step_description from %s.step_info where step_id = '%s' ;" % (self._database, id)
                cur.execute(sql)
                step_info = cur.fetchone()
                step_info_array.append(step_info[0])
            cur.close()
            conn.close()
            return step_info_array
        except Exception, e:
            print "getCaseStep encounter exception: %s" % e
            return [] 

    def getAmountByStatus(self, run_id, status = None):
        try:
            conn = MySQLdb.connect(host=self._host, port=3306, user=self._user, passwd=self._passwd, db=self._database)
            cur = conn.cursor()
            if status == None:
                sql = "select status, count(*) from %s.case_info where run_id = '%s' group by status ;" % (self._database, run_id)
                cur.execute(sql)
                amount = cur.fetchall()
                result = amount
            else:
                sql = "select count(*) from %s.case_info where run_id = '%s' and status = '%s';" % (self._database, run_id, status)
                cur.execute(sql)
                amount = cur.fetchone()
                result = amount[0]
            cur.close()
            conn.close()
            return result
        except Exception, e:
            print "getCaseAmountByStatus encounter exception: %s" % e
            return 0

if __name__ == '__main__':
    import time
    m_dbInfo = {"host":"10.224.54.181",\
                           "user":"root",\
                           "passwd":"ART",\
                           "database":"wist_r"}
    run_id = 3019
    db_obj = CWBXTFDBI(m_dbInfo["host"], m_dbInfo["user"], 
                       m_dbInfo["passwd"], m_dbInfo["database"])
    print time.time()
    print db_obj.getAmountByStatus(run_id)
    res = db_obj.getAmountByStatus(run_id, 'PASS')
    pass_amount = db_obj.getAmountByStatus(run_id, 'PASS')
    fail_amount =  db_obj.getAmountByStatus(run_id, 'FAIL')
    timeout_amount = db_obj.getAmountByStatus(run_id, 'TIMEOUT')
    na_amount = db_obj.getAmountByStatus(run_id, 'NA')
    running_amount = db_obj.getAmountByStatus(run_id, 'START')
    
    
    
    print time.time()
    print res
   
   