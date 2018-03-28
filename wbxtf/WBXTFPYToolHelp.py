__author__ = 'huajin2'

import os
import socket
import threading
import time

import WBXTFBusiness
import WBXTFService


class wbxtfPyToolModuleInterfaceBase(object):
    def __init__(self):
        self._URL = ""

    def exit(self):
        pid = os.getpid()
        WBXTFService.WBXTFKillProcessByPID("local", pid)

    def getPID(self):
        pid = os.getpid()
        return pid

    def getToolURL(self):
        return self._URL

    def WBXTFSetToolURL(self,URL):
        self._URL = URL
        self._onSelfURLGet()

    def _onSelfURLGet(self):
        pass

class wbxtfPyToolModule(threading.Thread):
    def __init__(self,interfaceObj,interfaceName="",dependThreadName="MainThread"):
        threading.Thread.__init__(self)
        self._interfaceObj = interfaceObj
        self._interfaceName = interfaceName
        self._machineIp = socket.gethostbyname(socket.gethostname())
        #if this machine has 192.xx ip will use it as toolurl
        IPinfo = socket.gethostbyname_ex(socket.gethostname())
        for ip in IPinfo[2]:
            if ip.find("192")!= -1:
                self._machineIp = ip
                break
        self._dependThreadName = dependThreadName
        if self._interfaceName == "":
            self._interfaceName = "unnametool"
        self._interfaceName = self._interfaceName + "_pid" + str(os.getpid())
        pass

    def setupToolName(self,showName):
        self._interfaceName = showName

    def getToolName(self):
        return  self._interfaceName

    def unregisterTool(self):
        WBXTFBusiness.cancelAsTool()

    def run(self):
        WBXTFBusiness.setRoot(self._interfaceObj)
        oTool = WBXTFBusiness.registerAsTool(self._interfaceName, dependThreadName=self._dependThreadName)
        if oTool.IsRegister() == True:
            URL = "wbxtf://%s/tool.$%s" % (self._machineIp,str(oTool.m_handle))
            self._interfaceObj.WBXTFSetToolURL(URL)
        WBXTFBusiness.runningRegisterTool(oTool)

if __name__ == '__main__':
    otest = wbxtfPyToolModuleInterfaceBase()
    pytool = wbxtfPyToolModule(otest,"Test")
    pytool.start()

    for i in range(0,10):
        print "Run ... %s" % i
        time.sleep(1)
    pass