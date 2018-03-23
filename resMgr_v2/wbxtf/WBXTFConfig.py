import sys
import threading
import os
import types

class WBXTFConfig:
    m_lock = threading.RLock()
    
    def __init__(self):
        self.m_config = {}
        
    def copy(self):
        self.m_lock.acquire()
        config = WBXTFConfig()
        config.m_config = self.m_config.copy()
        self.m_lock.release()
        
    def get(self, key, default = None):
        self.m_lock.acquire()
        value = default
        if self.m_config.has_key(key):
            value = self.m_config[key]
        self.m_lock.release()            
        return value
    
    def set(self, key, value):
        self.m_lock.acquire()
        self.m_config[key] = value
        if type(key) == types.StringType:
            setattr(self, key, value)
        self.m_lock.release()    
        
    def setDefault(self, key, default):
        self.m_lock.acquire()
        if not self.m_config.has_key(key):            
            self.m_config[key] = default
            if type(key) == types.StringType:
                setattr(self, key, default)
        self.m_lock.release()        
    
    def readConfigFile(self, file):
        self.m_lock.acquire()
        var = {}
        if os.path.isfile(file):
            execfile(file, var)
            for k,v in var.items():
                self.m_config[k] = v
                if type(k) == types.StringType:
                    setattr(self, k, v)
        self.m_lock.release()
        return True

def ReadConfigFile(sFile, globals = globals()):
    print "ReadConfigFile:%s" % sFile
    var = {}
    try:
        execfile(sFile, var)
        for k,v in var.items():
            globals[k] = v
        return var
    except Exception, e:
        print e
        return None

def ReadConfgFile(sFile, globals = globals()):
    return ReadConfigFile(sFile, globals)

def ReadDefaultConfigFile(globals = globals()):
    sFile = sys.argv[0]
    sConfigFile = sFile[0:-3]
    sConfigFile = sConfigFile + "_data.py"
    print sConfigFile
    return ReadConfgFile(sConfigFile, globals)

g_config = {}  

'''
    Add this interface to correct "readConfgFile" to "readConfigFile"
'''
def  readConfigFile(sFile, globals = globals()):
    #return ReadConfigFile(sFile, globals)
    return ReadConfigFile(sFile, globals)

def  readConfgFile(sFile, globals = globals()):
	return ReadConfigFile(sFile, globals)

def readDefaultConfigFile(globals = globals()):
	return ReadDefaultConfigFile(globals)
   
def config(name, value):
	global g_config
	g_config[name] = value
	
def getConfig(name, default = None):
	global g_config
	if g_config.has_key(name):
	   return g_config[name]
	else:
		return default

def setEurekaPETADB(host = "localhost", user = "root", passwd = ""):
	global g_config	
	g_config['eureka.peta.db.host'] = host
	g_config['eureka.peta.db.user'] = user
	g_config['eureka.peta.db.password'] = passwd
	g_config['eureka.peta.db.isEureka'] = True
	
def setTaskID(runID, taskID):
	global g_config	
	g_config['task.id.run'] = runID
	g_config['task.id.task'] = taskID

	
def getEurekaPETADB():
	info = {}
	info['isEureka'] = getConfig('eureka.peta.db.isEureka', False)
	info['password'] = getConfig('eureka.peta.db.password', '')
	info['user'] = getConfig('eureka.peta.db.user', '')
	info['host'] = getConfig('eureka.peta.db.host', '')
	return info

def getTaskID():
	info = {}
	info['runid'] = getConfig('task.id.run', 0)
	info['taskid'] = getConfig('task.id.task', 0)
	return info		
	
def getBasePath(subpath = None):
    basepath = os.path.abspath(sys.argv[0])   
    basepath = os.path.dirname(basepath)     
    if subpath != None:
        basepath += "\\"
        basepath += subpath
    return basepath
