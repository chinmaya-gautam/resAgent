import socket
import threading
import time
import types

import WBXTF


##################################################################
##
## WBXTF CallBack
##
#################################################################

class WBXTFCallBackThread(threading.Thread):    
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.__parent = parent
        self.__exception = 0
        
    def run(self):
        if self.__exception != 0:
            return -1
        try:
            return self.__parent.OnRun()
        except Exception, e:
            self.__exception = 1
            self.__parent.Exit()
            wbxtf.WBXTFError("Exception in CallBack:%s" % str(e))
            return -1
        
    
class WBXTFCallBackFun1:
    """
    Generate a URI for a callback function, 
    and check / dispatch the callback to the callback function
    This class is used for WBXTFCallBack          
    @author: Shaun
    @date: 2008/07/15
    """             
    __lock = threading.RLock()
    def __init__(self, fun):
        """   
        @type fun: function
        @param fun: the callback function
        """          
        self.fun = fun
        self.sMachine = 'local'
        prot = WBXTF.WBXTFGetProt()
        if(prot=="staf"):
            res = WBXTF.g_wbxtfSTAF.submit("local", "var", "get system var STAF/Config/Machine")
            if(res["rc"] == 0):
                self.sMachine = res["result"]
        else:
            self.sMachine = socket.gethostbyname(socket.gethostname())
        
        self.queue = WBXTF.WBXTFObject("%s://local/queue" % prot)
        res = self.queue.Execute("CreateSubQueue")
        self.dwID = 0
        if(res['rc'] == 0):
            self.dwID = res['result']
        self.uri = "%s://%s/queue.[%s].Put" % (prot,self.sMachine, self.dwID)
        return
    
    def GetURI(self): 
        """
        Get the URI of the callback function.
        You can pass the URI to the remote object to set callback  
        @rtype:  string
        @return: URI, a location of callback function
        """                 
        return self.uri

    def __Dispatch(self, val):
        # Detect the function type
        typeFun = type(self.fun)
        nFun = 0
        if(typeFun == types.FunctionType):
            nFun = self.fun.func_code.co_argcount
        elif typeFun == types.MethodType:
            nFun = self.fun.im_func.func_code.co_argcount
            nFun = nFun - 1
                        
        nVal = 1
        bList = (type(val) == type([]))
        if bList:
            nVal = len(val)            
            
        sCommand = "self.fun("
        for nIdx in range(nFun):
            if nIdx > 0:
                sCommand += ","
            if nIdx < nVal:
                if bList:
                    sCommand += "val[%d]" % (nIdx)
                else:
                    sCommand += "val"
            else:
                sCommand += "None"
        sCommand += ")"
        eval(sCommand)               

    def Check(self):
        """
        Check whether there is a callback event
        You must repeat to call the function to drive callback 
        """          
        res = self.queue.Execute("[%s].Get" % (self.dwID))
        # print (self.dwID)
        #print  res
        count = 0
        if(res['rc'] == 0 and int(res['result']['count']) > 0):
            count = int(res['result']['count'])
        for index in range(count):
             ##__Dispatch
             self.__Dispatch(res["result"]["value"][index])

    def Test(self, val):
        """
        This is for Test
        """
        self.__Dispatch(val)

    def __del__(self):        
        try:          
            self.__lock.acquire()  
            self.queue.Execute("DestroySubQueue(%d)" % self.dwID)
            self.__lock.release()                 
        except Exception, e:            
            pass        

class WBXTFCallBack1:
    """
    Support CallBack          
    @author: Shaun
    @date: 2008/07/15
    """      
    def __init__(self, bAutoStart = True, interval = 0.2, bDaemonThread = True):
        """
        Init WBXTF CallBack
        @type bAutoStart: bool
        @param bAutoStart: Whether auto start callback
        @type interval: float
        @param interval: the interval between twice checking   
        """                 
        self.lock = threading.RLock()  
        self.funs = {}
        self.bExit = 1
        self.interval = interval
        self.bAutoStart = bAutoStart
        self.eventWait = threading.Event()
        self.__bDaemonThread = bDaemonThread
        self.__thread = None
        return
    
    def __del__(self):          
        try:            
            self.StopListen()
        except Exception,e :
            pass
             
    def __createThread(self):
        if self.__thread == None:
            self.__thread = WBXTFCallBackThread(self)
            self.__thread.setDaemon(self.__bDaemonThread)

    ## Register a function and get the uri    
    def RegisterFunction(self, fun):
        """
        Register a callback function
        @type fun: function
        @param fun: The callback function
        @rtype: string
        @return: the interval for every checking
        """          
        self.Lock()
        if self.funs.has_key(fun):
            var = self.funs[fun]["uri"]
            self.Unlock()
            return var
        else:
            val = {}
            val["obj"] = WBXTFCallBackFun1(fun)
            val["uri"] = val["obj"].GetURI()
            val["fun"] = fun
            self.funs[fun] = val
            self.Unlock()
            if self.bAutoStart and not self.IsListening():
                self.StartListen()
            return val["uri"]

    ## Get the uri of a function
    def GetFunctionURI(self, fun):
        """
        Register a callback function
        @type fun: function
        @param fun: The callback function  
        """            
        self.Lock()
        var = ""
        if self.funs.has_key(fun):
            var = self.funs[fun]["uri"]
        self.Unlock()
        return var

    ## Unregister a function from  the listener list     
    def UnregisterFunction(self, fun):
        """
        Unregister a callback function
        @type fun: function
        @param fun: The callback function
        """         
        self.Lock()
        if not self.funs.has_key(fun):
            self.Unlock()
            return
        self.funs.pop(fun)
        num = len(self.funs)
        self.Unlock()
        if self.bAutoStart and num == 0:
            self.StopListen()
        return

    ## Unregister all functions from  the listener list     
    def UnregisterAll(self):
        """
        Unregister all callback functions 
        """         
        self.Lock()
        self.funs.clear()
        self.Unlock()
        if self.bAutoStart:
            self.StopListen()
        return    

    ## Start to listen Call Back    
    def StartListen(self):
        """
        Start to listen the callbacks
        @rtype: None
        @return: None 
        """      
        self.Lock()
        if(not self.bExit):
            self.Unlock()
            return        
        self.__createThread()
        WBXTF.WBXTFOutput("WBXTFCallBack::StartListen");
        self.bExit = 0
        self.__thread.start()
        self.Unlock()
        return
    
    def IsListening(self):
        """
        Check if is listening
        @rtype: bool
        @return: result, True - Listening, False - Not Listening
        """        
        return self.bExit != 1

    ## Stop to listen Call Back    
    def StopListen(self):
        """
        Stop the listening
        @rtype: None
        @return: None         
        """
        self.Lock()
        if(self.bExit):
            self.Unlock()
            return    
        self.bExit = 1
        if threading.currentThread().getName() != self.__thread.getName():
            tmpThread = self.__thread
            self.__thread = None
            self.Unlock()
            tmpThread.join()
        else:
            WBXTF.WBXTFWarning("WBXTFCallBack::StopListen is called inside a callback function. Please avoid to do that.")
            self.__thread = None   
            self.Unlock()       
        return

    def Lock(self):
        """
        Using lock to prevent variable conflict.
        The function is design for variable conflict in callback functions.
        Only need call this function outside callback functions.        
        @see: UnLock 
        """
        return self.lock.acquire()
        
    def Unlock(self):
        """
        Call this function release a lock.        
        @see: Lock 
        """
        return self.lock.release()

    def __delete__(self):
        self.UnRegisterAll()
        self.StopListen()
        return    

    def Check(self, funs):
        """
            Manually check the callback functions
        """        
        for key,item in funs.items():
            item["obj"].Check()
            
    def Test(self, val):
        for key,item in self.funs.items():
            item["obj"].Test(val)
          
    def OnRun(self):
        while self.bExit == 0:
            self.Lock()
            funs = self.funs.copy() 
            self.Unlock()
            self.Check(funs)
            time.sleep(self.interval)            
        return    

    def Run(self, Timeout = None):
        """
        Hanging the call thread and wait it.
        When you call Exit() or the time exhausts, the function return.
                
        @type Timeout: float
        @type Timeout: The timeout value. The unit is second. 
        @see: Exit  
        """
        if Timeout == None:
            res = self.eventWait.wait()
            return res
        else:
            res = self.eventWait.wait(Timeout)
            return res

    def Exit(self):
        """
        Exit for Run()
                
        @see: Run
        """        
        return self.eventWait.set() 
    
class WBXTFCallBack2:
    """
    Support CallBack          
    @author: Shaun
    @date: 2010/01/07
    """  
    def __init__(self, bAutoStart = True, interval = 5, bDaemonThread = True):
        """
        Init WBXTF CallBack
        @type bAutoStart: bool
        @param bAutoStart: Whether auto start callback
        @type interval: unused
        @param interval: the interval between twice checking   
        """         
        self.__lock = threading.RLock() 
        self.__bDaemonThread = bDaemonThread  
                
        self.__funs = {}
        self.__mapFun = {}
        self.__bListen = 0
        self.__interval = 5 
        self.__bAutoStart = bAutoStart
        self.__eventWait = threading.Event()
        self.__nNextID = 0
        self.__eventSlotURL = ""
        self.__eventSlotID = 0
        self.__eventSlotName = ""
        self.__eventSlot = None
        self.__thread = None            
                
        self.__registerEventSlot()
        self.__eventSlotExitURL = self.RegisterFunction(self.__onExit)
        
    def __del__(self):     
        try:
            self.StopListen()
        except Exception,e :
            pass
                
    def __createThread(self):
        if self.__thread != None:
            return
        self.__thread = WBXTFCallBackThread(self)
        self.__thread.setDaemon(self.__bDaemonThread)  
         
        
    def __onExit(self):
        self.__bListen = False
        
    def __unRegisterEventSlot(self):       
        if self.__eventSlotID > 0:            
            obj = WBXTF.WBXTFObject(self.__eventSlotExitURL)
            obj.exit()
            self.__eventSlotID = 0
            
    def __isRegisterEventSlot(self):
        if self.__eventSlotID > 0:
            return True
        else:
            return False 
    
    def __registerEventSlot(self): 
        # Register Event Slot        
        self.__eventSlot = WBXTF.WBXTFObject("staf://local/eventslot")
        if len(self.__eventSlotName) > 0:
            res = self.__eventSlot.CreateSlot(self.__eventSlotName)
        else:
            res = self.__eventSlot.CreateSlot()        
        if res['rc'] != 0:
            WBXTF.WBXTFWarning("Fail to init the callback system (CreateSlot)")
            return
        self.__eventSlotName = str(res['result'])
        self.__eventSlotID = int(res['result'])  
        res = self.__eventSlot.GetAbsURL(self.__eventSlotID)
        if res['rc'] != 0:
            WBXTF.WBXTFWarning("Fail to init the callback system (GetAbsURL)")
            return                            
        self.__eventSlotURL = res['result']
        return

    ## Register a function and get the uri    
    def RegisterFunction(self, fun):
        """
        Register a callback function
        @type fun: function
        @param fun: The callback function
        @rtype: string
        @return: the interval for every checking
        """          
        self.Lock()
        if self.__funs.has_key(fun):
            var = self.__funs[fun]["uri"]
            self.Unlock()
            return var
        else:
            val = {}
            self.__nNextID += 1
            val["name"] = str(self.__nNextID) 
            val["fun"] = fun
            val["uri"] = self.__eventSlotURL + "." + val["name"]
            self.__funs[fun] = val            
            if self.__bAutoStart and not self.IsListening():
                self.StartListen()            
            self.__mapFun[val["name"]] = fun 
            self.Unlock()           
            return val["uri"]

    ## Get the uri of a function
    def GetFunctionURI(self, fun):
        """
        Register a callback function
        @type fun: function
        @param fun: The callback function  
        """            
        self.Lock()
        var = ""
        if self.__funs.has_key(fun):
            var = self.__funs[fun]["uri"]
        self.Unlock()
        return var

    ## Unregister a function from  the listener list     
    def UnregisterFunction(self, fun):
        """
        Unregister a callback function
        @type fun: function
        @param fun: The callback function
        """         
        self.Lock()
        if not self.__funs.has_key(fun):
            self.Unlock()
            return
        self.mapFun.pop(self.__funs[fun]['name'])
        self.__funs.pop(fun)
        num = len(self.__funs)
        self.Unlock()
        if self.__bAutoStart and num == 0:
            self.StopListen()
        return

    ## Unregister all functions from  the listener list     
    def UnregisterAll(self):
        """
        Unregister all callback functions 
        """         
        self.Lock()
        self.__funs.clear()
        self.__mapFun.clear()
        self.Unlock()
        if self.__bAutoStart:
            self.StopListen()
        self.__eventSlotExitURL = self.RegisterFunction(self.__onExit)
        return

    ## Start to listen Call Back    
    def StartListen(self):
        """
        Start to listen the callbacks
        @rtype: None
        @return: None 
        """           
        self.Lock()
        if(self.__bListen):
            self.Unlock()
            return
        if not self.__isRegisterEventSlot():
            self.__registerEventSlot()
        self.__createThread()
        WBXTF.WBXTFOutput("WBXTFCallBack::StartListen", WBXTF.typeDebug);
        self.__bListen = True
        self.__thread.start()
        self.Unlock()
        return
    
    def IsListening(self):
        """
        Check if is listening
        @rtype: bool
        @return: result, True - Listening, False - Not Listening
        """        
        return self.__bListen

    ## Stop to listen Call Back    
    def StopListen(self):
        """
        Stop the listening
        @rtype: None
        @return: None         
        """        
        self.Lock()
        if(not self.__bListen):
            self.Unlock()
            return
        self.__bListen = False
        self.__unRegisterEventSlot()  
        if threading.currentThread().getName() != self.__thread.getName():
            tmpThread = self.__thread
            self.__thread = None
            self.Unlock()
            tmpThread.join()
        else:
            WBXTF.WBXTFWarning("WBXTFCallBack::StopListen is called inside a callback function. Please avoid to do that.")
            self.__thread = None   
            self.Unlock()       
        return
        return

    def Lock(self):
        """
        Using lock to prevent variable conflict.
        The function is design for variable conflict in callback functions.
        Only need call this function outside callback functions.        
        @see: UnLock 
        """
        return self.__lock.acquire()
        
    def Unlock(self):
        """
        Call this function release a lock.        
        @see: Lock 
        """
        return self.__lock.release()

    def __delete__(self):
        self.StopListen()        
        return    

    def Check(self):
        """
            Manually check the callback functions
        """
        if self.__eventSlotID == 0:
            return False
        while self.__bListen:  
            res = self.__eventSlot.WaitEvent(self.__eventSlotID, 60000)
            if res['rc'] != 0 or (not self.__DispatchResult(res['result'])):
                time.sleep(self.__interval)
        return True
            
    def __DispatchResult(self, result):
        items = {}
        try:
            if result['hr'] != 0:
                 return False
            if int(result['count']) == 0:
                 return True
            items = result['value']
        except Exception, e:
            return False
        for item in items:
            self.__DispatchItem(item)
        return True
        
    
    def __DispatchItem(self, item):
        self.Lock()
        try:
            request = item['request']
            val = item['param']            
            if not self.__mapFun.has_key(request):
                self.Unlock()
                return False
            fun = self.__mapFun[request]
                    
            typeFun = type(fun)
            nFun = 0
            if(typeFun == types.FunctionType):
                nFun = fun.func_code.co_argcount
            elif typeFun == types.MethodType:
                nFun = fun.im_func.func_code.co_argcount
                nFun = nFun - 1                        
            nVal = 1
            bList = (type(val) == type([]))
            
            if bList and len(val) == 1:
                val = val[0]          
                bList = (type(val) == type([]))
                 
            if bList:
                nVal = len(val)              
                
            sCommand = "fun("
            for nIdx in range(nFun):
                if nIdx > 0:
                    sCommand += ","
                if nIdx < nVal:
                    if bList:
                        sCommand += "val[%d]" % (nIdx)
                    else:
                        sCommand += "val"
                else:
                    sCommand += "None"
            sCommand += ")"
            eval(sCommand) 
        except Exception, e:
            return False    
        self.Unlock()
        return True
          
    def OnRun(self):            
        self.Check()
        return    

    def Run(self, Timeout = None):
        """
        Hanging the call thread and wait it.
        When you call Exit() or the time exhausts, the function return.
                
        @type Timeout: float
        @type Timeout: The timeout value. The unit is second. 
        @see: Exit  
        """
        if Timeout == None:
            res = self.__eventWait.wait()
            return res
        else:
            res = self.__eventWait.wait(Timeout)
            return res

    def Exit(self):
        """
        Exit for Run()
                
        @see: Run
        """
        return self.__eventWait.set()
    
    
class WBXTFCallBack:
    """
    Support CallBack          
    @author: Shaun
    @date: 2010/01/07
    """  
    def __init__(self, bAutoStart = True, interval = 5, bDaemonThread = True):
        """
        Init WBXTF CallBack
        @type bAutoStart: bool
        @param bAutoStart: Whether auto start callback
        @type interval: unused
        @param interval: the interval between twice checking   
        """    
        self.__callBack = WBXTFCallBack1(bAutoStart, interval, bDaemonThread)
#        obj = WBXTF.WBXTFObject("staf://local/eventslot")
#        res = obj.WBXTFGetTags()
#        self.__callBack = None
#        if res['rc'] == 0:
#            WBXTF.WBXTFOutput("Using EventSlot Callback System", WBXTF.typeDebug)
#            self.__callBack = WBXTFCallBack2(bAutoStart, interval, bDaemonThread)
#        else:
#            WBXTF.WBXTFOutput("Using Queue Callback System", WBXTF.typeDebug)
#            self.__callBack = WBXTFCallBack1(bAutoStart, interval, bDaemonThread)

    ## Register a function and get the uri    
    def RegisterFunction(self, fun):
        """
        Register a callback function
        @type fun: function
        @param fun: The callback function
        @rtype: string
        @return: the interval for every checking
        """          
        return self.__callBack.RegisterFunction(fun)

    ## Get the uri of a function
    def GetFunctionURI(self, fun):
        """
        Register a callback function
        @type fun: function
        @param fun: The callback function  
        """            
        return self.__callBack.GetFunctionURI(fun)

    ## Unregister a function from  the listener list     
    def UnregisterFunction(self, fun):
        """
        Unregister a callback function
        @type fun: function
        @param fun: The callback function
        """         
        return self.__callBack.UnregisterFunction(fun)

    ## Unregister all functions from  the listener list     
    def UnregisterAll(self):
        """
        Unregister all callback functions 
        """         
        return self.__callBack.UnregisterAll()

    ## Start to listen Call Back    
    def StartListen(self):
        """
        Start to listen the callbacks
        @rtype: None
        @return: None 
        """           
        return self.__callBack.StartListen()
   
    def IsListening(self):
        """
        Check if is listening
        @rtype: bool
        @return: result, True - Listening, False - Not Listening
        """        
        return self.__callBack.IsListening()

    ## Stop to listen Call Back    
    def StopListen(self):
        """
        Stop the listening
        @rtype: None
        @return: None         
        """        
        return self.__callBack.StopListen()

    def Lock(self):
        """
        Using lock to prevent variable conflict.
        The function is design for variable conflict in callback functions.
        Only need call this function outside callback functions.        
        @see: UnLock 
        """
        return self.__callBack.Lock()
        
    def Unlock(self):
        """
        Call this function release a lock.        
        @see: Lock 
        """
        return self.__callBack.Unlock()

    def __delete__(self):
        self.__callBack = None
        return    

    def Check(self):
        """
            Manually check the callback functions
        """
        return self.__callBack.Check() 

    def Run(self, Timeout = None):
        """
        Hanging the call thread and wait it.
        When you call Exit() or the time exhausts, the function return.
                
        @type Timeout: float
        @type Timeout: The timeout value. The unit is second. 
        @see: Exit  
        """
        return self.__callBack.Run() 

    def Exit(self):
        """
        Exit for Run()
                
        @see: Run
        """
        return self.__callBack.Exit() 
    

def testCallBackFun():
    print "it is worked"
    pass

if __name__ == "__main__":
    callback = WBXTFCallBack()
    print "1." + callback.RegisterFunction(testCallBackFun)
    print "2." + callback.GetFunctionURI(testCallBackFun)
    # callback2 = WBXTFCallBack()
    # print "1." + callback2.RegisterFunction(testCallBackFun)
    # print "2." + callback2.GetFunctionURI(testCallBackFun)
    callback.StartListen()
    #callback2.StopListen()
    time.sleep(10)
    callback.StopListen()

    # callback.StartListen()
    # callback.StopListen()
    # callback.StopListen()
    # callback.StartListen()

    
    
  
