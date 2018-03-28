#!/usr/bin/python

import imp
import os
import sys

import WBXTFBusiness

wbxtf_init_modules = sys.modules.keys()
  
class WBBusinessLoader:
    m_sPath = ""
    m_modules = {}
    def __init__(self):
        pass
    
    def SetPath(self, path):
        self.m_sPath = path
        os.sys.path.append(path)
        return True
    
    def Load(self):
        # Clear all        
        self.__clearModule()
        res = self.__LoadDir(self.m_sPath)
        WBXTFBusiness.setRoot(globals())
        return res
        
    def __clearModule(self):
        for m in [x for x in sys.modules.keys() if x not in wbxtf_init_modules]:        	
                del(sys.modules[m])   
    
    def __IsLoad(self, sModuleName):
    	return False
        if self.m_modules.has_key(sModuleName):
            return self.m_modules[sModuleName]
        else:
            return False
          
    def __LoadModule(self, sModuleName, sPath, sShortModuleName):
        try: 
            if self.__IsLoad(sModuleName):
                exec('reload(%s)' % (sModuleName))
                return True
                               
            res = imp.find_module(sShortModuleName, [sPath])            
            tmp = imp.load_module(sShortModuleName, res[0], res[1], res[2])
            WBXTFBusiness.supportModule(tmp)            
            if "." in sModuleName:
                exec("%s = tmp" % (sModuleName))
            else:
                exec("global %s;%s = tmp" % (sModuleName, sModuleName))           
     
            self.m_modules[sModuleName] = True          
            return True
        except ImportError, e:
            return False   
        except Exception, e:
#            print e.message
            return False
    
    def __LoadDir(self, sPath, sBase = ""):
        files = os.listdir(sPath)        
        paths = sFolder = os.path.split(sPath)
        sDirName = paths[len(paths) - 1]
        if sBase != "":
            if not ("__init__.py" in files):
                return False
            if not self.__LoadModule(sBase, paths[0], sDirName):
                return False                      
        else:
            pass      

        for sFile in files:         
            if sFile[0:1] == "_":
                continue            
            sLongFile = sPath + "/" + sFile
            if os.path.isdir(sLongFile):
                if sBase == "":
                    sNewBase = sFile
                else:
                    sNewBase = sBase + "." + sFile
                self.__LoadDir(sLongFile, sNewBase) 
                continue
            module_name, ext = os.path.splitext(sFile)
            if ext != ".py":
                continue
            sModuleName = ""
            if sBase == "":
                sModuleName = module_name
            else:
                sModuleName = sBase + "." + module_name           

            self.__LoadModule(sModuleName, sPath, module_name) 
            
        return True
    
global __gLoader
__gLoader = WBBusinessLoader()

#def SetPath(sPath):
#    return __gLoader.SetPath(sPath)  

def setPath(sPath):
    return __gLoader.SetPath(sPath) 

def load():
    return __gLoader.Load()  

def setTimeout(timeout):
    WBXTFBusiness.WB_INFINIT = timeout

def getTimeout():
    return WBXTFBusiness.WB_INFINIT

def exit():
    WBXTFBusiness.clearHiddenObject()
    WBXTFBusiness.cancelAsTool() 


WBXTFBusiness.hideObject(setPath)
WBXTFBusiness.hideObject(load)
WBXTFBusiness.hideObject(wbxtf_init_modules)



