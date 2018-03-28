import time

import WBXTF


class WBXTFSysInfo:
    def __init__(self,machine=""):
        self.m_machine = machine
        
    def __getSysInfoObj(self):
        return WBXTF.WBXTFGetSysInfoObj(self.m_machine)
        
    def setMachine(self,machine):
        self.m_machine = machine
        
    def getMachine(self):
        return self.m_machine
    
    def start(self):
        sysinfo = self.__getSysInfoObj()
        res = sysinfo.monitor.control.Start()
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]start return:%s" % res)
        
    def stop(self):
        sysinfo = self.__getSysInfoObj()
        res = sysinfo.monitor.control.Stop()
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]stop return:%s" % res)
            
    def isRunning(self):
        sysinfo = self.__getSysInfoObj()
        res = sysinfo.monitor.control.IsRunning()
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]isRunning return:%s" % res)
        return bool(res["result"])
        
    def setMonitProcName(self, procName):
        sysinfo = self.__getSysInfoObj()
                                      
        res = sysinfo.monitor.control.SetMonitProcName(procName)
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]setMonitorProcName return:%s" % res)
        
    def getMonitProcName(self):
        sysinfo = self.__getSysInfoObj()
        res = sysinfo.monitor.control.GetMonitProcName()
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]getMonitorProcName return:%s" % res)
        return res["result"]
        
    def setSampleInterval(self, second):
        sysinfo = self.__getSysInfoObj()
        res = sysinfo.monitor.control.SetSampleInterval(second)
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]setSampleInterval return:%s" % res)
        
    def getSampleInterval(self):
        sysinfo = self.__getSysInfoObj()
        res = sysinfo.monitor.control.GetSampleInterval()
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]getSampleInterval return:%s" % res)
        return res["result"]
        
    def setCSVFilePath(self, csvPath):
        sysinfo = self.__getSysInfoObj()
        res = sysinfo.monitor.control.SetCSVFilePath(csvPath)
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]setCSVFilePath return:%s" % res)
        
    def getCSVFilePath(self):
        sysinfo = self.__getSysInfoObj()
        res = sysinfo.monitor.control.GetCSVFilePath()
        if(res["rc"]!=0):
            WBXTF.WBXTFWarning("[SysInfo]getCSVFilePath return:%s" % res)
        return res["result"]
    
if __name__ == '__main__':
    
    info = WBXTFSysInfo("local")
    
    if info.isRunning():
        info.stop()

    info.setMonitProcName("taskmgr")
    print 'get monitor process name: ', info.getMonitProcName()
    
    info.setSampleInterval(1)   # 1 second
    print 'get sampleInterval: ', info.getSampleInterval()
    
    print 'default csv file: ', info.getCSVFilePath()
    info.setCSVFilePath("d:\\dev\\perf_sysinfo_demo.csv")
    print 'change csv file: ', info.getCSVFilePath()
    
    info.start()
    
    print 'is running: ', info.isRunning()
    
    start_time = time.time();
    
    while time.time() - start_time <= 10:
        pass
    
    info.stop()
    
