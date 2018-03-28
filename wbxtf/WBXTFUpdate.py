#!/usr/bin/python
"""
This case is design for WBXTF Update 

@author: $Author: ShaunZ $
@version: $Revision: 1.4 $
@license: Copyright Cisco-Webex Corp
"""
import time

import WBXTF
import WBXTFActionPool

RUN_TIMEOUT=120 * 1000

class WBXTFWin32Update(WBXTF.WBXTFSectionLog):
    def __init__(self):
        self.m_targetMachines = ['']
        self.m_sourceMachine = ''
        self.m_sourceDir = 'C:/WBXTF/Backup/wbxtf-install'
        self.m_targetDir = 'C:/WBXTF/Backup/wbxtf-install'
        self.m_targetFilename = 'WBXTF-Setup.exe'
        self.m_packName = 'WBXTF'
                            
    def setTarget(self, machines, targetDir = None):
        self.m_targetMachines = machines
        if targetDir != None:
            self.m_targetDir = targetDir
    
    def setSource(self, sourceMachine, sourceDir = None):
        self.m_sourceMachine = sourceMachine
        if sourceDir != None:
            self.m_sourceDir = sourceDir
            
    def setInstallPackageFileName(self, filename):
        self.m_targetFilename = filename
    
    def removeInstallPackage(self):
        group = WBXTF.WBXTFObjectGroup()
        ress = []
        for machine in self.m_targetMachines:
            staf = WBXTF.WBXTFSTAF()
            request = 'DELETE ENTRY "%s" RECURSE CONFIRM' % (self.m_targetDir)            
            result = staf.submit(machine, "FS", request)
            ress.append(result)
        return ress
    
    def deployInstallPackage(self):
        self.traceHead("Deploy %s" % (self.m_packName))
        machines = {}
        index = 1
        machines = self.m_targetMachines
        count = len(machines)
        success = 0
        for machine in machines:
            self.trace("[%d/%d]Start to install %s" %(index, count, machine))
            staf = WBXTF.WBXTFSTAF()
            request = 'COPY DIRECTORY "%s" TODIRECTORY "%s" TOMACHINE "%s" RECURSE'\
                 % (self.m_sourceDir, self.m_targetDir, machine)
            result = staf.submit(self.m_sourceMachine, "fs", request)
            sText = "[%d/%d]End deploying on %s" %(index, count, machine)
            try:
                if result != None and result["rc"] == 0:
                    sText += ": OK"
                    success += 1
                else:                                        
                    sText += ": Failed :"
                    if result != None and result["rc"] == 0:
                        sText += str(result["rc"])
                        sText += ":"
                        sText += result["result"] 
            except Exception, e:
                 sText = "[%d/%d]End deploying on %s" %(index, count, machine)
                 sText += ": Failed"    
            self.trace(sText)
            index += 1 
        self.traceSep()
        self.trace("Total:%d, Success:%d, Fail:%d" %
                           (len(machines),
                            success,
                            len(machines) - success)) 
        self.traceTail("Deploy %s" % (self.m_packName))
        
    def __startOnMachine(self, machine):
        path = self.m_targetDir
        path += "/"
        path += self.m_targetFilename     
        objProcess = WBXTF.WBXTFObject("staf://%s/process" % (machine))
        sExtend = 'WAIT %s WORKDIR "%s"' % (RUN_TIMEOUT, self.m_targetDir)
        res = objProcess.Run(path, "/S", sExtend)
#        res = WBXTF.WBXTFRunWait(machine, path, "/S", 120)  
        return res 
        
    def install(self):
        self.traceHead("Update %s" % (self.m_packName))
        machines = {}
        index = 1
        machines = self.m_targetMachines
        count = len(machines)
        success = 0
        runMachines = []
        failMachines = []
        pool = WBXTFActionPool.WBXTFActionPool()
        ids = []        
        for machine in machines:
            id = pool.putAction(None, self.__startOnMachine, machine)
            ids.append([id, machine])
        for id in ids:
            res = pool.waitResult(id[0])                    
            if res['result']['rc'] != 22:
                self.trace("[%s] Fail to update, %s" % (id[1], res['result']['result']))
                failMachines.append(machine)
            else:
                self.trace("[%s] Start to update" % (id[1]))
                runMachines.append(id[1])                                
        # Wait until timeout
        passMachines = []
        self.m_timeout = 120
        last = time.time()
        now = last
        while now - last <= self.m_timeout and len(runMachines) > 0:
            now = time.time()
            for machine in runMachines[:]:
                obj = WBXTF.WBXTFObject("staf://%s/" % (machine))
                res = obj.WBXTFGetTags()
                if res['rc'] == 0:
                    passMachines.append(machine)
                    runMachines.remove(machine)
                    self.trace("[%s] Updated" % (machine))
            time.sleep(1)
        for machine in runMachines:
            failMachines.append(machine)
            self.trace("[%s] Fail to update" % (machine))            
        self.trace("Total:%d, Success:%d, Fail:%d" %
                           (len(machines),
                            len(passMachines),
                            len(failMachines)))        
        self.traceTail("Update %s" % (self.m_packName))                             
        if len(failMachines) > 0:
            return False
        else:
            return True
    
    def queryVersion(self):
        self.traceHead("Query %s Version" % (self.m_packName))
        machines = {}
        index = 1
        machines = self.m_targetMachines
        count = len(machines)
        success = 0
        runMachines = []
        failMachines = []
        mapVersion = {}
        for machine in machines:
            obj = WBXTF.WBXTFObject("staf://%s/wbxtf.util" % (machine))
            res = obj.GetVersion()
            if res['rc'] == 0:
                self.trace("[%s] %s" % (machine, res['result']))
                mapVersion[machine] = res['result']
            else:
                self.trace("[%s] Fail:%s:%s" % (machine, res['rc'], res['result']))                
        self.traceTail("Query %s Version" % (self.m_packName))
        return mapVersion    

if __name__ == "__main__":
    update = WBXTFWin32Update()
    update.install()
    update.queryVersion()

