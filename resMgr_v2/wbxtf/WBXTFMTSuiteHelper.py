"""

                                                                         
@author: Fei Liang
@date: $Date: 2010/01/16 
@version: $Revision: 1.3 $
@license: Copyright Cisco-Webex Corp.
@see:
@summary: 
"""
import xml.dom.minidom
import time
import sys
import codecs

class CWBXTFSuiteHelper:

    def __init__(self):
        self.__m_suiteRun = None
        self.__m_filePath = ""
        
    def readSuiteRun(self):
        bSuccess = False
        try:
            self.__m_suiteRun = xml.dom.minidom.parse(self.__m_filePath)
            if(self.__m_suiteRun!=None):
                bSuccess = True
        except Exception,e:
            print e
        return bSuccess

    def getDBNode(self):
        dbNode = None
        if(self.__m_suiteRun != None):
            suiteRun = self.__m_suiteRun.documentElement
            childs = suiteRun.childNodes
            for child in childs:
                if child.nodeName == "db":
                    dbNode = child
                    break
        return dbNode
    
    def getDBInfo(self):
        dbInfo = {}
        dbNode = self.getDBNode()
        if(dbNode==None):
            return dbInfo
        attrs = dbNode.attributes
        keys = attrs.keys()
        for key in keys:
            attr = attrs[key]
            value = attr.nodeValue
            dbInfo[key] = value
        return dbInfo
    
    def getRunParamInfo(self):
        runParamInfo = {}
        runParamNode = self.getRunParamNode()
        if(runParamNode==None):
            return runParamInfo
        attrs = runParamNode.attributes
        keys = attrs.keys()
        for key in keys:
            attr = attrs[key]
            value = attr.nodeValue
            runParamInfo[key] = value
            if(key == "config"):
                runParamInfo[key] = value.replace("\\","\\\\")
        return runParamInfo
    
    def getRunParamNode(self):
        runParamNode = None
        if(self.__m_suiteRun != None):
            suiteRun = self.__m_suiteRun.documentElement
            childs = suiteRun.childNodes
            for child in childs:
                if child.nodeName == "runParam":
                    runParamNode = child
                    break
        return runParamNode
    
    def getSuiteRun(self):
        pass

    def getSuiteNode(self):
        suiteNode = None
        if(self.__m_suiteRun != None):
            suiteRun = self.__m_suiteRun.documentElement
            childs = suiteRun.childNodes
            for child in childs:
                if child.nodeName == "suite":
                    suiteNode = child
                    break
        return suiteNode
           
    def getSuiteInfo(self):
        suiteInfo = {}
        suiteNode = self.getSuiteNode()
        if(suiteNode==None):
            return suiteInfo
        attrs = suiteNode.attributes
        keys = attrs.keys()
        for key in keys:
            attr = attrs[key]
            value = attr.nodeValue
            suiteInfo[key] = value
            if(key == "base_path"):
                suiteInfo[key] = value.replace("\\","\\\\")
        return suiteInfo

    def getSuitesNode(self,runParam = None):
        suiteNode = []
        if(self.__m_suiteRun != None):
            suiteRun = self.__m_suiteRun.documentElement
            childs = suiteRun.childNodes
            for child in childs:
                if child.nodeName == "suite":
                    if runParam and runParam.has_key("run_sutes") and (child.attributes["name"].nodeValue not in runParam["run_sutes"]):
                        continue
                    suiteNode.append(child)
        return suiteNode
        
    def getSuitesInfo(self, runParam = None):
        suitesInfo = []
        suiteNodes = self.getSuitesNode(runParam)
        for suiteNode in suiteNodes:
            suiteInfo = {}
            attrs = suiteNode.attributes
            keys = attrs.keys()
            for key in keys:
                attr = attrs[key]
                value = attr.nodeValue
                suiteInfo[key] = value
                if(key == "base_path"):
                    suiteInfo[key] = value.replace("\\","\\\\")
            suiteCases = self.getCaseInfos(suiteNode, runParam)
            suiteInfo["case"] = suiteCases
            suitesInfo.append(suiteInfo)
            
        return suitesInfo
            
    def getCaseInfos(self, suiteNode = None, runParam=None):
        caseInfos = []
        caseNodes = self.getCaseNodes(suiteNode, runParam)
        for caseNode in caseNodes:
            caseInfo = {}
            attrs = caseNode.attributes
            keys = attrs.keys()
            for key in keys:
                attr = attrs[key]
                value = attr.nodeValue
                caseInfo[key] = value
                if(key == "path"):
                    caseInfo[key] = value.replace("\\","\\\\")
            caseInfos.append(caseInfo)
            
        return caseInfos

    def getCaseNodes(self, suiteNode = None, runParam=None):
        caseNodes = []
        if suiteNode == None:
            suiteNode = self.getSuiteNode()
        childs = suiteNode.childNodes
        if runParam \
                and runParam.has_key("quick_test_env") \
                and runParam["quick_test_env"] == "True" :
            for child in childs:
                if(child.nodeName == "quick_test_case"):
                    caseNodes.append(child)
                    break
            if len(caseNodes) == 0:
                for child in childs:
                    if(child.nodeName == "case"):
                        caseNodes.append(child)
                        break
        else:
            for child in childs:
                if(child.nodeName == "case"):
                    caseNodes.append(child)
            
        return caseNodes
    
    def setFilePath(self,path):
        self.__m_filePath = path
        
    def getFilePath(self):
        return self.__m_filePath

""" 
path = "D:/work/cvs/server/PETA2.0/lib/com/org/tools/wapi/suite.xml"
obj = CWBXTFSuiteHelper()
obj.setFilePath(path)
obj.readSuiteRun()
print obj.getSuiteInfo()
print obj.getCaseInfos()
print obj.getDBInfo()
print obj.getRunParamInfo()  
"""
