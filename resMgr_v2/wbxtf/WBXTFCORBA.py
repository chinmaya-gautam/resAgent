import ctypes
import WBXTFUtil
import time
import threading
import sys
import WBXTFError

class WBXTFCORBA:
    __m_lock = threading.RLock()
    def __init__(self):
        self.dll = None
        self.m_handle = 0        
        
    def __del__(self):
        self.destroy()
              
    def create(self):
#        try:
            if self.dll != None:
                return True
            if sys.platform == "win32":
                self.dll = ctypes.cdll.LoadLibrary("WBXTFCORBAClient.dll")
            else:
                self.dll = ctypes.cdll.LoadLibrary("WBXTFCORBAClient.so")
            num = ctypes.c_uint()            
            self.dll.WBXTFCreateClient(0, ctypes.byref(num), 0)
            self.m_handle = num
            if self.m_handle == 0:
                self.dll = None
                return False
            else:
                return True
#        except Exception,e:            
#            return False
        
    def __createOnce(self):
        self.__m_lock.acquire()
        if self.dll == None:
            res = self.create()
            self.__m_lock.release()
            return res
        else:
            self.__m_lock.release()
            return True
            
    def destroy(self):
        if self.dll == None:
            return
        self.dll.WBXTFDestroyClient(self.m_handle)
    
    def execute(self, machine, command):
        self.__createOnce()
        if self.dll == None:
            return {'rc':WBXTFError.E_ERROR, 'result':None}        
        hrRes = ctypes.c_long()
        sResult = ctypes.c_char_p()
        hr = self.dll.WBXTFExecuteClient(self.m_handle,
                                    ctypes.c_char_p(machine),
                                    ctypes.c_char_p(command),
                                    0,                                    
                                    ctypes.byref(sResult),
                                    0)
        result = {}
        if hr != 0:
            result['rc'] = hr
            result['result'] = None
        else:
            result["rc"] = hrRes.value
            result["result"] = WBXTFUtil.WBXTFDefaultResultFormat2Var(sResult.value)            
        self.dll.WBXTFFreeResult(sResult)
        return result    
    

    
    
