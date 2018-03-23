##################################################################
##
## Library for WBXTF by STAF
##
#################################################################
import sys
from WBXTF import *


class WBXTFQTask:
   
   def __init__(self):
      self.params = {}
      self.__ParseArg()
      sRoot = self.ReadParam("target_node", "")
      if len(sRoot):         
         self.root = WBXTFObject(sRoot)
      else:
         self.root = WBXTFObject("staf://local")
    
   def ReadParam(self, param, default = None):
      sKey = param.upper()
      if self.params.has_key(sKey):
##         if type(default) == type(1):
##            return (int)(self.params[sKey])
##         elif type(default) == type(0.1):
##            return (float)(self.params[sKey])
##         else:
           return self.params[sKey]
      else:
         return default

   def Execute(self, command):
      return self.root.Execute(command)

   def DumpParam(self):
      print self.params
   
   def __ParseArg(self):
      for arg in sys.argv:
         val = arg.partition("=")
         if len(val[1]) == 0:
            continue
         sKey = val[0].strip()
         sValue = val[2]
         if len(sKey) == 0:
            continue
         self.params[sKey.upper()] = sValue
   
