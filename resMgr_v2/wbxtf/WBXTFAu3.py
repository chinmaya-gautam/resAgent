import WBXTF


def WBXTFAu3Load(sMachine, sModulePath):
    sURL = 'staf://%s/au3' % (sMachine)    
    objAu3 = WBXTF.WBXTFObject(sURL)
    res = objAu3.Load(sModulePath)
    if res['rc'] != 0 or res['result'] == '':
        return None
    sNewURL = sURL
    sNewURL = sNewURL + "."
    sNewURL = sNewURL + res['result']
    return WBXTFAu3Object(sNewURL)    

def WBXTFAu3Attach(sMachine, sModuleName):
    sURL = 'staf://%s/au3.%s' % (sMachine, sModuleName)
    return WBXTFAu3Object(sURL, False) 


class WBXTFAu3Object(WBXTF.WBXTFObject):
    def __init__(self, sURL, bUnload = True):
        WBXTF.WBXTFObject.__init__(self, sURL)
        self.__m_bUnload = bUnload
        
    def __del__(self):
        if self.__m_bUnload:
            self.Unload()
        
    def Unload(self):
        self.WBXTF_Exit()
        self.__m_bUnload = False
    
##########################################    
# For Test
##########################################
#myAu3 = WBXTFAu3Load('local', 'ie.au3')
#myAu3._IECreate()
#myAu3._IEQuit("$result__IECreate")


#myAu3 = WBXTFAu3Attach('local', 'default')
#print myAu3.Add(10, 20)
#print myAu3.Add(10, 20)
#print myAu3.Add(10, 20)
#print myAu3.Add(10, 20)
#print myAu3.Add(10, 20)
#myAu3.Unload()


     
       

