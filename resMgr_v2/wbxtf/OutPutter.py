"""
Base class of test result outputter
@version: $Id: OutPutter.py,v 1.3 2008-09-11 09:17:28 martin.dai Exp $
@author: Martin
@contact: martin@hf.webex.com
@date: 2008/08/18
@todo: 
"""

import WBXTF

class IOutPutter:
    def __init__(self):
        self.m_TestCase = None
       
    def BindWithTestCase(self, testCase):
        self.m_TestCase = testCase
        
    def outLog(self, type, log, more = None):
        pass

    def outStatusAsPass(self, description = ""):
        pass

    def outStatusAsFail(self, description = ""):
        pass


class DefaultOutPutter(IOutPutter):
    def __init__(self):
        IOutPutter.__init__(self);        

    def outLog(self, type, log, more = None):
        scope = {}
        if self.m_TestCase:
            scope['cid'] = self.m_TestCase.m_CID
            scope['mid'] = self.m_TestCase.m_MID
        return WBXTF.WBXTFOutput(log, type, scope) 

    def outStatusAsPass(self, description = ""):
        if len(description):
            self.outLog(WBXTF.typeInfo, "%s" % (description))

    def outStatusAsFail(self, description = ""):
        if len(description):
            self.outLog(WBXTF.typeError, "%s" % (description))

        