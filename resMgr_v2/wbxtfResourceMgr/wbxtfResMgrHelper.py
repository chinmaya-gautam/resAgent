
import WBXTF
import WBXTFTool
from wbxtf.WBXTFLogex import *
from wbxtf.WBXTFActionPool import *
import socket

class wbxtfResMgrRuner():
    '''
    imputParam = {
        "toolPath":"",
        "machineList":[],
    }
    '''
    def __init__(self,inputParam):
        self.__inputParam = inputParam
        pass

    def StartTools(self,machineList = None,timeout = 60):
        toolMachineList = self.__inputParam["machineList"]
        if machineList != None:
            toolMachineList = machineList
        toolPath = self.__inputParam["toolPath"]

        WBXTFLogInfo("Run wbxtf resource manager agent ,toolPath = %s ,machines = %s" % (toolPath,toolMachineList))
        toolMgr = WBXTFTool.WBXTFToolMgr()
        toolMgr.setToolType(WBXTFTool.WBXTFToolType_Python)
        toolMgr.setToolPath(toolPath)

        return  toolMgr.runToolsOnMachinesByTotal(toolMachineList,len(toolMachineList),0,timeout,True)

# def getWBXTFResMgrObj(machine):
#     toolNode = WBXTF.WBXTFGetToolObj(machine)
#     res = toolNode.WBXTFGetSubObjs()
#     if res.has_key("rc") and res["rc"] == 0 :
#         if res["result"]!= None:
#             for item in res["result"]:
#                 if item["name"] == "wbxtfResourceMgr":
#                     toolObj = WBXTF.WBXTFGetToolBySubID(machine,item["subid"])
#                     return toolObj
#
#     WBXTFLogWarning("wbxtfResourceMgr is not running on machine%s" % machine)
#     return None

def getWBXTFResMgrObj(machine):
    oResMgr = WBXTF.WBXTFObject("wbxtf://%s/tool.wbxtfResourceMgr" % machine)
    oRes = oResMgr.WBXTFGetTags()
    if oRes["rc"] == 0 :
        return oResMgr
    WBXTFLogWarning("wbxtfResourceMgr is not running on machine%s" % machine)
    return None

def actionGetResMgrVersionFunc(machine):
    oResMgr = getWBXTFResMgrObj(machine)
    if not oResMgr == None:
        version = oResMgr.getVersion()
        WBXTFLogInfo("machine:%s   RegMgr version:%s" % (machine,version))
        if version["rc"] == 0:
            return True
    return False

def actionRunWBXUIAFunc(machine):
    oResMgr = getWBXTFResMgrObj(machine)
    if not oResMgr == None:
        ret = oResMgr.runwbxUIAs("2.0","test",r"wbxtf://192.168.5.118/tool.$19",1)
        WBXTFLogInfo("machine:%s   RegMgr ret:%s" % (machine,ret))
        if ret["rc"] == 0:
            return True
    return False

def actionGetToolsInfoFromResMgr(machine):
    oResMgr = getWBXTFResMgrObj(machine)
    if not oResMgr == None:
        ret = oResMgr.reportManagedToolsInfo()
        WBXTFLogInfo("machine:%s   RegMgr managed tools info:%s" % (machine,ret))
        if ret["rc"] == 0:
            return True
    return False

if __name__ == '__main__':
    param_dest_machineList =[]
    machineIndexFrom = 191
    machineIndexTo = 200
    for x in range(machineIndexFrom, machineIndexTo + 1):
        strMachineName = "win7-npc%03d" % x
        param_dest_machineList.append(strMachineName)

    ##########################################################################
    #restart resource manager
    ##########################################################################
    # for machine in param_dest_machineList:
    #     oResMgr = getWBXTFResMgrObj(machine)
    #     if not oResMgr == None:
    #         oResMgr.exit()
    #
    # param = {
    #     "toolPath":r"C:\wbxtfResouceManageAgent\wbxtfResourceMgr\wbxtfResMgr.py",
    #     "machineList":param_dest_machineList
    # }
    # oRun = wbxtfResMgrRuner(param)
    # oRun.StartTools()

    ##########################################################################
    # update a exist version for a tool
    ##########################################################################
    # toolname = "tool_thinclient"
    # version = "2.1"
    # for machine in param_dest_machineList:
    #     oResMgr = WBXTF.WBXTFObject("wbxtf://%s/tool.wbxtfResourceMgr" % machine)
    #     res = oResMgr.addRemoteTool(toolname,version)
    #     print res
    # pass

    ##########################################################################
    # check version of ResMgr on machines
    ##########################################################################
    # actionPool = WBXTFActionPool(min(50,len(param_dest_machineList)))
    # for machine in param_dest_machineList:
    #     actionPool.putAction(None,actionGetResMgrVersionFunc,machine)
    # actionPool.waitComplete()

    ##########################################################################
    # Run WBXUIAFunc on machines
    ##########################################################################
    # actionPool = WBXTFActionPool(min(50,len(param_dest_machineList)))
    # for machine in param_dest_machineList:
    #     actionPool.putAction(None,actionRunWBXUIAFunc,machine)
    # actionPool.waitComplete()


    ##########################################################################
    # Get Tools Info From ResMgr
    ##########################################################################
    actionPool = WBXTFActionPool(min(50,len(param_dest_machineList)))
    for machine in param_dest_machineList:
        actionPool.putAction(None,actionGetToolsInfoFromResMgr,machine)
    actionPool.waitComplete()