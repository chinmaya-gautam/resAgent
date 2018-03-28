import types

import WBXTF

CONFIG_DEPLOY_THREAD_NUM = 5

class WBXTFDeployConfig:    
    def __init__(self):
        self.m_sSourceMachine = ''
        self.m_sMachines = []
        self.m_sSourcePath = ''
        self.m_sPackName = ''
        self.m_sDestPath = ''
        self.m_sPackVersion = ''
        self.m_enableDebug = False
        
    def copy(self):
        config = WBXTFDeployConfig()
        config.m_sSourceMachine = self.m_sSourceMachine        
        config.m_sSourcePath = self.m_sSourcePath
        config.m_sPackName = self.m_sPackName
        config.m_sDestPath = self.m_sDestPath
        config.m_sPackVersion = self.m_sPackVersion
        config.m_enableDebug = self.m_enableDebug   
        config.m_sMachines = self.m_sMachines[:]
        return config    
        
        
    def setSourceMachine(self, machine):
        self.m_sSourceMachine = machine
    
    def getSourceMachine(self):
        return self.m_sSourceMachine
        
    def setTargetMachines(self, machines):
        self.m_sMachines = machines
    
    def getTargetMachines(self):
        return self.m_sMachines
    
    def setSourcePath(self, path):
        self.m_sSourcePath = path
        
    def getSourcePath(self):
        return self.m_sSourcePath
        
    def setDestPath(self, path):
        self.m_sDestPath = path
    
    def getDestPath(self):
        return self.m_sDestPath        
    
    def setPackName(self, path):
        self.m_sPackName = path
        
    def getPackName(self):
        return self.m_sPackName
    
    def setPackVerion(self, version):
        self.m_sPackVersion = version
        
    def getPackVerion(self):
        return self.m_sPackVersion
    
    def enableDebugTrace(self, enabled):
        self.m_enableDebug = enabled
    
    def isEnabledDebugTrace(self):
        return self.m_enableDebug     
        
class WBXTFDeploy:
    def __init__(self, config = WBXTFDeployConfig()):
        self.__m_config = config        
        
    def __trace(self, text):
        if self.getConfig().isEnabledDebugTrace():
            WBXTF.WBXTFOutput(text, WBXTF.typeDebug)
                
    def setConfig(self, config):
        self.__m_config = config
        
    def getConfig(self):
        return self.__m_config
    
    def __formatFailResult(self, rc, desc):
        result = {}
        result['rc'] = rc 
        result['success'] = 0
        result['description'] = desc
        result['result'] = {}
        return result
    
    def deploy(self):
        self.__trace("Enter deploy")
        sourceMachine = self.getConfig().getSourceMachine()
        targetMachines = self.getConfig().getTargetMachines()
        sourcePath = self.getConfig().getSourcePath()
        destPath = self.getConfig().getDestPath()
        packName = self.getConfig().getPackName()  
        packVersion = self.getConfig().getPackVerion()       
                
        if type(targetMachines) != types.ListType:
            error = 'the destMachines is not a list'
            self.__trace("Leave deploy:%s" % (error))            
            return self.__formatFailResult(WBXTF.E_ERROR, error)        

        # Check the parameter
        if sourceMachine == "":
            error = 'not set source machine'
            self.__trace("Leave deploy:%s" % (error))
            return self.__formatFailResult(WBXTF.E_ERROR, error)     
      
        if len(targetMachines) == 0:
            error = 'the destMachines is empty'
            self.__trace("Leave deploy:%s" % (error))
            return self.__formatFailResult(WBXTF.E_ERROR, error)  
        
        if len(sourcePath) == 0:
            error = 'not set sourcePath'
            self.__trace("Leave deploy:%s" % (error))
            return self.__formatFailResult(WBXTF.E_ERROR, error)     
                
        # Deploy
        self.__trace("Start to deploy")
        group = WBXTF.WBXTFObjectGroup()
        group.setMaxRequestThreads(CONFIG_DEPLOY_THREAD_NUM)
        for machine in targetMachines:            
            deployObj = WBXTF.WBXTFObject("staf://%s/pack" % (machine))
            group.add(deployObj, False)
                        
        ress = group.execute("Install(%s, %s, %s, %s)" % \
                             (packName,\
                              sourceMachine,\
                              sourcePath,\
                              destPath))        
        result = {}
        num = 0  
        if ress == None:
            ress = [] 
            
        groupSetVersion = WBXTF.WBXTFObjectGroup()

        for res in ress:
            try:
                if res['result']['rc'] != 0:
                    result[res['object'].sMachine] = res['result']
                else:
                     result[res['object'].sMachine] = res['result']['result']
                     if res['result']['rc'] == 0:
                         num += 1
                         groupSetVersion.add(res['object'])
                         self.__trace("Success deploying in %s" % (res['object'].sMachine))
            except Exception, e:
                if res.has_key('object'):
                    result[res['object'].sMachine] = {'rc': WBXTF.E_ERROR, 'result': ''}
                
        totalResult = {}
        totalResult['result'] = result
        totalResult['success'] = num
        if num == 0:
            totalResult['rc'] = WBXTF.E_ERROR
        elif num == len(targetMachines):
            totalResult['rc'] = 0
        else:
            totalResult['rc'] = WBXTF.S_FALSE   
            
        self.__trace("deployed tools in %d machines" % (num))        
            
        # Set the version information
        if packVersion != None and len(packVersion) > 0:
            self.__trace("Start to set the version:%s" % (packVersion))
            res = groupSetVersion.execute('%s.AddProp("sys.version", %s)' % (packName, WBXTF.WBXTFVar(packVersion)))
            self.__trace("End to set the version:%s" % (packVersion))  
                         
        self.__trace("Leave deploy")   
                     
        return totalResult
        
    def queryPackVersion(self):
        self.__trace("Enter queryPackVersion")        
        targetMachines = self.getConfig().getTargetMachines()        
        packName = self.getConfig().getPackName()  
        
        if type(targetMachines) != types.ListType:
            error = 'the destMachines is not a list'
            self.__trace("Leave queryPackVersion:%s" % (error))            
            return self.__formatFailResult(WBXTF.E_ERROR, error)   
      
        if len(targetMachines) == 0:
            error = 'the destMachines is empty'
            self.__trace("Leave queryPackVersion:%s" % (error))    
            return self.__formatFailResult(WBXTF.E_ERROR, error)  
        
                # Check the parameter
        if packName == "":
            error = 'not set pack name'
            self.__trace("Leave queryPackVersion:%s" % (error))    
            return self.__formatFailResult(WBXTF.E_ERROR, error)
        
        
        group = WBXTF.WBXTFObjectGroup()        
        for machine in targetMachines:            
            deployObj = WBXTF.WBXTFObject("staf://%s/pack" % (machine))
            group.add(deployObj, False)   
                        
        ress = group.execute('%s.GetProp(sys.version)' %(packName))
        num = 0
        result = {}
        for res in ress:
            try:
                if res['result']['rc'] != 0:
                    result[res['object'].sMachine] = res['result']
                else:
                     result[res['object'].sMachine] = res['result']                    
                     num += 1
                     group.add(res['object'])
                     self.__trace("queryPackVersion: machine %s:%s" % (res['object'].sMachine, res['result']))
            except Exception, e:
                if res.has_key('object'):
                    result[res['object'].sMachine] = {'rc': WBXTF.E_ERROR, 'result': ''}
         
        totalResult = {}
        totalResult['result'] = result
        totalResult['success'] = num
        if num == 0:
            totalResult['rc'] = WBXTF.E_ERROR
        elif num == len(targetMachines):
            totalResult['rc'] = 0
        else:
            totalResult['rc'] = WBXTF.S_FALSE
        self.__trace("Leave queryPackVersion")    
        return  totalResult
    
    def removePack(self):
        self.__trace("Enter removePack") 
              
        targetMachines = self.getConfig().getTargetMachines()   
        packName = self.getConfig().getPackName()

        if type(targetMachines) != types.ListType:
            error = 'the destMachines is not a list'
            self.__trace("Leave removePack:%s" % (error))            
            return self.__formatFailResult(WBXTF.E_ERROR, error)   
      
        if len(targetMachines) == 0:
            error = 'the destMachines is empty'
            self.__trace("Leave removePack:%s" % (error))    
            return self.__formatFailResult(WBXTF.E_ERROR, error)         

        if packName == "":
            error = 'not set pack name'
            self.__trace("Leave removePack:%s" % (error))    
            return self.__formatFailResult(WBXTF.E_ERROR, error)
        
        group = WBXTF.WBXTFObjectGroup()        
        for machine in targetMachines:            
            deployObj = WBXTF.WBXTFObject("staf://%s/pack" % (machine))
            group.add(deployObj, False)   
                        
        ress = group.execute('UnInstall(%s)' %(packName))
        num = 0
        result = {}
        for res in ress:
            try:
                if res['result']['rc'] != 0:
                    result[res['object'].sMachine] = res['result']
                elif res['result']['result']['rc'] == 0:
                     result[res['object'].sMachine] = res['result']                    
                     num += 1
                     group.add(res['object'])
                     self.__trace("removePack: machine %s:%s" % (res['object'].sMachine, res['result']))
                else:
                    result[res['object'].sMachine] = res['result']['result']
            except Exception, e:
                if res.has_key('object'):
                    result[res['object'].sMachine] = {'rc': WBXTF.E_ERROR, 'result': ''}
         
        totalResult = {}
        totalResult['result'] = result
        totalResult['success'] = num
        if num == 0:
            totalResult['rc'] = WBXTF.E_ERROR
        elif num == len(targetMachines):
            totalResult['rc'] = 0
        else:
            totalResult['rc'] = WBXTF.S_FALSE
        self.__trace("Leave removePack")    
        return  totalResult        
    
    def updatePack(self):  
        self.__trace("Enter updatePack")             
        targetMachines = self.getConfig().getTargetMachines()[:]
        machineNum = len(targetMachines)      
        packName = self.getConfig().getPackName()
        packVersion = self.getConfig().getPackVerion()   
        
        ingoreResult = {}         
        self.__trace("Enter updatePack::queryPackVersion") 
        res = self.queryPackVersion()
        self.__trace("Leave updatePack::queryPackVersion") 
        resultTotal = {}
        resultTotal['rc'] = 0
        result = {}    
        num = 0    
        if res['rc'] == 0:
            for (machine, result) in res['result'].items():                
                if result['rc'] == 0 and self.__compVersion(packVersion, result['result']) <= 0:
                   targetMachines.remove(machine)
                   ingoreResult[machine] = {'rc':0}  
                   num += 1                    
                   self.__trace("updatePack: machine %s not need to update:%s" % (machine, result['result'])) 
        if len(targetMachines) > 0:
            self.__trace("updatePack: deploy %d machines" % (len(targetMachines))) 
            config = self.getConfig().copy()
            config.setTargetMachines(targetMachines)
            deploy = WBXTFDeploy(config)
            res = deploy.deploy()
            
            # Merge the result
            for (machine, result) in ingoreResult.items():
                res['result'][machine] = result
                res['success'] += 1
            self.__trace("Leave updatePack")
            return res
        else:
            resultTotal['success'] = num
            resultTotal['result'] = ingoreResult
            self.__trace("Leave updatePack")
            return resultTotal 
                    
                
    def __compVersion(self, ver1, ver2):
        listVer1 = ver1.split('.')
        listVer2 = ver2.split('.') 
        num1 = len(listVer1)
        num2 = len(listVer2)
        for index in range(num1):
            if index >= num2:
                return 1
            n1 = int(listVer1[index])
            n2 = int(listVer2[index])
            if n1 < n2:
                return -1
            elif n1 > n2:
                return 1
        if num1 == num2:
            return 0
        else:
            return -1                 

def WBXTFDeployPack(packName, sourceMachine, destMachines, sourcePath, destPath = None, packVersion = None):
        config = WBXTFDeployConfig()
#        config.enableDebugTrace(True)
        config.setPackName(packName)
        config.setSourceMachine(sourceMachine)
        config.setTargetMachines(destMachines)
        config.setSourcePath(sourcePath)
        config.setDestPath(destPath)
        config.setPackVerion(packVersion)
        
        deploy = WBXTFDeploy(config)
        res = deploy.deploy()
        return res
    
def WBXTFUpdatePack(packName, sourceMachine, destMachines, sourcePath, destPath = None, packVersion = None):
        config = WBXTFDeployConfig()
#        config.enableDebugTrace(True)
        config.setPackName(packName)
        config.setSourceMachine(sourceMachine)
        config.setTargetMachines(destMachines)
        config.setSourcePath(sourcePath)
        config.setDestPath(destPath)
        config.setPackVerion(packVersion)
        
        deploy = WBXTFDeploy(config)
        res = deploy.updatePack()
        return res     
     
    
def WBXTFQueryPackVersion(packName, destMachines):
        config = WBXTFDeployConfig()
        config.setPackName(packName)
        config.setTargetMachines(destMachines)
        
        deploy = WBXTFDeploy(config)
        res = deploy.queryPackVersion()                        
        return res    
    
def WBXTFRemovePack(packName, destMachines):
        config = WBXTFDeployConfig()
        config.setPackName(packName)
        config.setTargetMachines(destMachines)
        
        deploy = WBXTFDeploy(config)
        res = deploy.removePack()                        
        return res     
        
"""       
       
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
"""
def WBXTFQueryPack(destMachines, packName):
    pass

if __name__ == "__main__":
    machines = []
    for index in range(10):
        machines.append("SHAUN%s" % (index))
    machines.append("10.224.70.150")    
    
    res = WBXTFRemovePack("Test", machines)
    WBXTF.WBXTFCheck("WBXTFRemovePack", res["success"] == 2)
#    print res    
    
    res = WBXTFDeployPack("Test", "10.224.70.71", machines, "C:/WBXTF/Demo/WBXTFDemo1", "D:/Target/", "1.0")
    WBXTF.WBXTFCheck("WBXTFDeployPack", res["success"] == 11)
#    print res
    
    res = WBXTFDeployPack("Test", "10.224.70.71", ["10.224.70.150"], "C:/WBXTF/Demo/WBXTFDemo1", "D:/Target/", "1.1")
    WBXTF.WBXTFCheck("WBXTFDeployPack", res["success"] == 1)
#    print res
    
    res = WBXTFQueryPackVersion("Test", machines)
    WBXTF.WBXTFCheck("WBXTFQueryPackVersion", res["success"] == 11)
#    print res
        
    res = WBXTFUpdatePack("Test", "10.224.70.71", ['SHAUN1', '10.224.70.150'], "C:/WBXTF/Demo/WBXTFDemo1", "D:/Target/", "1.1")
    WBXTF.WBXTFCheck("WBXTFUpdatePack", res["success"] == 2)
#    print res
    
