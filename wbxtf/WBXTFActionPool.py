import threading
import time
from WBXTFError import *
######################################################


WBXTF_ACTIONPOOL_STYLE_POST = 1
######################################################


######################################################
class WBXTFActionPoolThread(threading.Thread):
    def __init__(self, pool):
        threading.Thread.__init__(self)
        threading.Thread.setDaemon(self, True)        
        self.setDaemon(True)
        self.m_bFree = False
        self.m_lock = threading.RLock()
        self.m_parent = pool
        
    def run(self):
        while not self.m_parent.isCancel():             
            self.__setFree(False)               
            request = self.m_parent.getNextAction()            
            if request != None:                                                         
                res = request['fun'](*request['args'])               
                self.m_parent.putResult(request['id'], res)                                
            self.__setFree(True)            
            self.m_parent.waitEvent()                    
            
            
    def __setFree(self, bFree):
        self.m_lock.acquire()
        self.m_bFree = bFree
        self.m_lock.release()
                            
    def isBusy(self):
        self.m_lock.acquire()
        busy = not self.m_bFree
        self.m_lock.release()
        return busy

class WBXTFActionPool:          
    def __init__(self, max_thread_num = 30, bAutoStart = True):
#        if max_thread_num <= 0:
#            max_thread_num = WBXTFGetSysConfig(WBXTF_SYS_CONFIG_REQUEST_POOL_MAX,
#                                               WBXTF_SYS_CONFIG_REQUEST_POOL_DEFAULT)        
        self.m_actions = []
        self.m_results = {}
        self.m_id = 0
        self.m_lock = threading.RLock()
        self.m_lockThread = threading.RLock()
        self.m_maxThreadNum = max_thread_num
        self.m_semRequest = threading.Semaphore()
        self.m_eventResult = threading.Event()
        self.m_threads = []
        self.m_exitFlag = False   
        self.m_bAutoStart = bAutoStart     
        self.m_bRunning = False   
        self.m_lockControl = threading.RLock()
        self.__threadFinishedNotifyfunc = None

    def setthreadFinishedNotifyFunc(self,func):
        self.__threadFinishedNotifyfunc = func

    def waitComplete(self, timeout = None):
        last = time.time() 
        now = last
        bFinish = False
        while timeout == None or now - last <= timeout:
            bFinish = self.isFinish()
            if bFinish:
                break
            time.sleep(0.5)            
            now = time.time()
        return bFinish
    
    def isFinish(self):
        isFinish = True
        self.m_lock.acquire()
        if len(self.m_actions) == 0:
            for id,result in self.m_results.items():
                if result['finish'] == False:
                    isFinish = False
                    break
        else:
            isFinish = False
        self.m_lock.release() 
        return isFinish
    
    def start(self):
        self.m_lockControl.acquire()
        self.__setExitFlag(False)
        self.__setRunning(True)
        self.__checkThread()
        self.m_lockControl.release()
    
    def stop(self, timeout = None):
        # wait until complete
        self.m_lockControl.acquire()
        self.waitComplete()
        
        self.__setExitFlag(True)    
        self.__closeThreads(timeout) 
        self.__setRunning(False)
        self.m_lockControl.release()
                        
    def cancel(self, timeout = None):                
        self.m_lockControl.acquire()
        self.__setExitFlag(True)
                
        # clear the actions
        self.m_lock.acquire()
        self.m_actions = []
        self.m_lock.release()
        
        # close all threads        
        self.m_lockThread.acquire()   
        self.__closeThreads(timeout)
        self.m_lockThread.release()
        
        self.__setRunning(False)
        
        self.m_lockControl.release()
        
    def putAction(self, opt, fun, *args):
        if fun == None:
            return 0
        ## Put into the queue
        self.m_lock.acquire()
        id = self.__getNextID()

        # generate the action
        request = {}
        request["id"] = id
        request["fun"] = fun
        request["args"] = args
        request["option"] = opt
        self.m_actions.append(request)

        # generate the result
        result = {}
        result["id"] = id
        result["event"] = None
        result["finish"] = False
        result["result"] = None
        result["fun"] = fun
        result["args"] = args
        result["option"] = opt
        self.m_results[id] = result
        self.__postEvent()
        self.m_lock.release()
        if self.m_bAutoStart and not self.__isRunning():
            self.start()
        return id

    def postAction(self, opt, fun, *args):
        if opt == None:
            opt = {}
        opt['style'] = WBXTF_ACTIONPOOL_STYLE_POST
        return self.putAction(opt, fun, *args)

    def putResult(self, id, res):
        self.m_lock.acquire()   
        if not self.m_results.has_key(id):
            return False             
        result = self.m_results[id]
        result["result"] = res
        result["finish"] = True
        if result["event"] != None:
            result["event"].set()
        if result["option"] != None and result["option"].has_key("style")\
         and result["option"]["style"] & WBXTF_ACTIONPOOL_STYLE_POST:
            self.m_results.pop(id)

        if not self.__threadFinishedNotifyfunc == None:
            self.__threadFinishedNotifyfunc(self.m_results)
        # nTotalTask = len(self.m_results)
        # nFinshed = 0
        # for key in self.m_results:
        #     if self.m_results[key]["finish"]== True:
        #         nFinshed +=1
        # print "ActionPool total task:%d finshed:%d" %(nTotalTask,nFinshed)
        self.m_lock.release()          
        
    def getResult(self, id):
        self.m_lock.acquire()
        result = {}
        rc = 0
        if self.m_results.has_key(id):
            if self.m_results[id]["finish"]:
                resItem = self.m_results.pop(id)
                result['result'] = resItem["result"]
                result['function'] = resItem["fun"]
                result['args'] = resItem["args"]
                result['option'] = resItem["option"] 
                rc = 0
            else:
                self.m_results[id]["event"] = threading.Event()
                rc = E_ERROR
        else:
            rc = E_NOTFOUND
        self.m_lock.release()
        result['rc'] = rc
        return result
    
    def waitResult(self, id, timeout = None):
        result = self.getResult(id)
        if result['rc'] == 0: 
            return result
        if result['rc'] == E_NOTFOUND:
            return result      
        rc = 0
        result = None
        event = None
        self.m_lock.acquire()
        if self.m_results.has_key(id):
            event = self.m_results[id]["event"]
        self.m_lock.release()
        if event == None:
            rc = E_NOTFOUND
            return {'rc': rc, 'result': result}
        
        event.wait(timeout)
        return self.getResult(id)
    
    def setMaxThreadCount(self, num):
        self.max_thread_num = num
    
    def getNextAction(self):
        self.m_lock.acquire()        
        action = None
        if len(self.m_actions) > 0:
            action = self.m_actions.pop(0)            
        self.m_lock.release()
        return action    
    
    def waitEvent(self, timeout = None):
        self.m_semRequest.acquire()         
          
    def isCancel(self):
        self.m_lock.acquire()
        bExit = self.m_exitFlag
        self.m_lock.release()
        return bExit  
    
    def __checkThread(self):
        self.m_lockThread.acquire()
        if self.m_maxThreadNum > 0 and len(self.m_threads) >= self.m_maxThreadNum:
            self.m_lockThread.release()
            return  
        self.m_lock.acquire() 
        if self.m_bRunning == False:
            self.m_lock.release()
            self.m_lockThread.release()
            return
        nFree = 0
        for thread in self.m_threads:
            if not thread.isBusy():
                nFree = nFree + 1        
        # Create a new thread
        nQueueSize = len(self.m_actions)
        nNeedCreated = nQueueSize - nFree
        if self.m_maxThreadNum > 0:
            nCanCreated = self.m_maxThreadNum - len(self.m_threads)
            if nNeedCreated > nCanCreated:
                nNeedCreated = nCanCreated
        while nNeedCreated > 0:            
            thread = WBXTFActionPoolThread(self)
            thread.start()
            self.m_threads.append(thread) 
            nNeedCreated = nNeedCreated -1     
        self.m_lock.release()                      
        self.m_lockThread.release()
    
    def __postEvent(self):
        self.__checkThread()
        self.m_semRequest.release()        
    
    def __getNextID(self):
        self.m_id = self.m_id + 1
        return self.m_id
    
    def __setRunning(self, bRunning):
        self.m_lock.acquire()
        self.m_bRunning = bRunning
        self.m_lock.release()
        
    def __isRunning(self):
        self.m_lock.acquire()        
        bRunning = self.m_bRunning
        self.m_lock.release()        
        return bRunning    
    
    def __closeThreads(self, timeout):
        self.__setExitFlag(True)
        self.m_lockThread.acquire()
        for thread in self.m_threads:
            self.m_semRequest.release()
        for thread in self.m_threads:            
            thread.join(timeout)
        self.m_threads = []
        self.m_lockThread.release()
        
    def __setExitFlag(self, bExitFlag):
        self.m_lock.acquire()
        self.m_exitFlag = bExitFlag        
        self.m_lock.release()
          
#####################################################    
#def add(num1, num2):
#    return num1 + num2
#
#def echo(text):
#    return text
#    
#times = 10000
#pool = WBXTFActionPool(30, True)
#for index in range(times):
#    id1 = pool.putAction(None, add, 10, 20)
#    id2 = pool.putAction(None, echo, "Test")
#    id3 = pool.postAction(None, add, 10, 20)
#    
##    res = pool.waitResult(id1)
##    print res
##    res = pool.waitResult(id2)
##    print res
##    res = pool.waitResult(id3)
##    print res
#pool.start()
#pool.stop()
#
#id1 = pool.putAction(None, add, 10, 20)
#res = pool.waitResult(id1)
#print res     
#
#pool.stop() 