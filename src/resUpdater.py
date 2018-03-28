__author__ = 'huajin2'

import sys
import os
import time
import shutil
import subprocess
from CopyUtil import *


if __name__ == "__main__":
    try:
        if len(sys.argv) == 6:
            resAgentAutoUpdaterPid = sys.argv[3]
            resAgentPid = sys.argv[4]
            resMgrPid = sys.argv[5]
            kill = subprocess.Popen("taskkill /F /PID %s" % resAgentAutoUpdaterPid,shell=True)
            print "wait resAgentAutoUpdater to be killed ...."
            kill.wait()

            kill = subprocess.Popen("taskkill /F /PID %s" % resMgrPid, shell=True)
            print "wait resMgr to be killed ...."
            kill.wait()

            kill = subprocess.Popen("taskkill /F /PID %s" % resAgentPid, shell=True)
            print "wait resAgent to be killed ...."
            kill.wait()

            dirUpdateTo = sys.argv[1]
            dirUpdateFrom = sys.argv[2]
            if os.path.isdir(dirUpdateTo):
                shutil.rmtree(dirUpdateTo,ignore_errors=True)
                time.sleep(5)
                print "delete old version success"
            if os.path.isdir(dirUpdateFrom):
                res = copyTree(dirUpdateFrom,dirUpdateTo)
                if not res[0]:
                    print res[1]

                try:
                    os.remove(os.path.join(dirUpdateTo, 'CopyUtil.py'))
                    os.remove(os.path.join(dirUpdateTo, 'CopyUtil.pyc'))
                    os.remove(os.path.join(dirUpdateTo, 'resUpdater.py'))
                    os.remove(os.path.join(dirUpdateTo, 'resUpdater.pyc'))
                except OSError:
                    pass
                except Exception as e:
                    print "[[ERROR]] %s" % str(e)

                print "Copy new version success, will restart new resAgent"
                newPath = os.path.join(dirUpdateTo,  "src", "resAgent.py")
                time.sleep(1)
                print "newPath:", newPath
                subprocess.Popen(newPath, shell=True)
                time.sleep(1)
                print "wbxtfResMgr started. selfUpdate will exit."
                time.sleep(1)
            else:
                print "copy from:%s dir is not exist" % dirUpdateFrom
                os.system("pause")
        else:
            print "input params error. input params=%s" % sys.argv
            os.system("pause")
    except Exception,e:
        print "Fatal error:%s" % e
        os.system("pause")