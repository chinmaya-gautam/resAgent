#!/usr/bin/python
import WBXTF


class BaseEnv(WBXTF.ITestEnv): 
    def config(self, name, value):
        pass
    def getConfigList(self):
        pass
    def getConfig(self, name):
        pass  


class TestStrategy:
    def __init__(self, machine, num):
        pass
    
    def SetEnv(self, env):
        pass
    
    def Run(self):
        print "Run"
        pass
    


class BaseASKEnv(BaseEnv):
    def config(self, strategy):
        pass
    
    def deploy(self, machine):
        strategy.SetEnv(self)
        strategy.Run()
            
    def runHost(self, strategy):
        pass
    
    def runAttendee(self, strategy):
        pass
    
    def runClient(self, strategy):
        pass
    
    def getGroup(self, strategy):
        pass
    
    def sendToHost(self):
        pass
        
    def sendToAttendee(self):
        pass
    
    def sendToAll(self):
        pass
    
    ##################################################
    def doRunHost(self, machine, num):
        pass
    def doRunAttendee(self, machine, num):
        pass
    

class BaseStrategy:
    pass



case = BaseASKEnv()
case.deploy(TestStrategy("local", 100))