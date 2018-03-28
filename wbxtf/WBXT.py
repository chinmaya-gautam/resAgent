###########################################
## This is for the old PeToolLib
#########################################
import PySTAF
import WBXTF


def WBXTSendEventAsyn(mainChannel, subChannel, event, machine = "local"):
    sRequest = "GENERATE TYPE %s SUBTYPE %s " % (mainChannel, subChannel)
    sValue = " property ".join(['%s="%s"' % (k, v) for k, v in event.items()])	
    if len(sValue) > 0:
        sRequest += " property "
        sRequest += sValue		
    res = WBXTF.g_wbxtfSTAF.submit(machine, 'event', sRequest)
    return res            
    
def WBXTEventGetResult(machine, eventID, timeOut = 60):
    res = WBXTF.g_wbxtfSTAF.submit(machine, 'sem', 'WAIT EVENT WBXT/EventResult/%s TIMEOUT %d' % (eventID, timeOut * 1000))
    if res["rc"] != 0:
        return res
    
    res = WBXTF.g_wbxtfSTAF.submit(machine, 'VAR', "GET SYSTEM VAR WBXT/EventResult/%s" % (eventID))
    if res["rc"] == 0:
        WBXTF.g_wbxtfSTAF.submit(machine, 'VAR', "DELETE SYSTEM VAR WBXT/EventResult/%s" % (eventID))
        WBXTF.g_wbxtfSTAF.submit(machine, 'SEM', "DELETE MUTEX WBXT/EventResult/%s" % (eventID))
        WBXTF.g_wbxtfSTAF.submit(machine, 'SEM', "DELETE EVENT WBXT/EventResult/%s" % (eventID))
    return res

def WBXTFSendEvent(mainChannel, subChannel, event, machine = "local", timeOut = 60):
    res = WBXTSendEventAsyn(mainChannel, subChannel, event, machine)
    if res["rc"] != 0:
        return res
    eventID = res["result"]
    res = WBXTEventGetResult(machine, eventID, timeOut)
    return res

def WBXTPostEvent(mainChannel, subChannel, event, machine = "local"):
    return WBXTSendEventAsyn(mainChannel, subChannel, event, machine)
    
def WBXTSendCommand(mainChannel, subChannel, command, machine = "local", timeOut = 60):
    return WBXTFSendEvent(mainChannel, subChannel, {'command':command}, machine, timeOut)

def WBXTSendCommandByHandle(handle, command, machine = "local", timeOut = 60):
    return WBXTFSendEvent('WBXT/handle', '%s' % (handle), command, machine, timeOut)

def WBXTEventTidy(machine):
    res = WBXTF.g_wbxtfSTAF.submit(machine, 'EVENT', "LIST REGISTRATIONS")
    if res["rc"] != 0:
        return
    listRegs = res["result"]
    listHandles = []
    if len(listRegs) == 0:
        return {'rc':0}
    res = WBXTF.g_wbxtfSTAF.submit(machine, 'HANDLE', "LIST")
    if res["rc"] != 0:
        return res
    if res["result"] == None or len(res["result"]) == 0:
        listHandles = []
    else:
        listHandles = res["result"]
        
    for item in listRegs:
        bFind = 0
        request = ''
        requestTmp = ''
        for handle in listHandles:
            if (item['notifyBy'] == 'Handle' and handle['handle'] == item['notifiee']) or (item['notifyBy'] == 'Name' and handle['name'] == item['notifiee']):
                bFind = 1
                break
        if bFind == 0:
            if item['notifyBy'] == 'Handle':
                requestTmp = 'HANDLE %s' % (item['notifiee'])
            else:
                requestTmp = 'NAME %s' % (item['notifiee'])
                
            if item['subtype'] == None:
                request = 'UNREGISTER TYPE %s FORCE %s' % (item['type'], requestTmp)
            else:
                request = 'UNREGISTER TYPE %s SUBTYPE %s FORCE %s' % (item['type'], item['subtype'], requestTmp)

            res = WBXTF.g_wbxtfSTAF.submit(machine, 'EVENT', request)        
    return {'rc':0}   
    

def WBXTEventInit(machine = 'local'):
    WBXTEventTidy(machine)

def WBXTFMarshall(var):
    return PySTAF.marshall(var)


#Params = {"test": "China", "2": "USA"}
#print PySTAF.marshall(Params)

#WBXTEventInit('local')       
#print WBXTFSendEvent("wbxt/testconsole", "all", {'command':'test'})
#print WBXTSendCommand("wbxt/testconsole", "all", "This is a test: %s" % WBXTFMarshall(Params))
