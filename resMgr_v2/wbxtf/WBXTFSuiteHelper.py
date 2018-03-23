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
            
    def getCaseInfos(self):
        caseInfos = []
        caseNodes = self.getCaseNodes()
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

    def getCaseNodes(self):
        caseNodes = []
        suiteNode = self.getSuiteNode()
        childs = suiteNode.childNodes
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
