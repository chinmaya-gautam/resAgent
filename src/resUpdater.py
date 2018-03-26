__author__ = 'huajin2'

import sys
import os
import time
import shutil
import subprocess


if __name__ == "__main__":
    try:
        if len(sys.argv) == 4:
            kill = subprocess.Popen("taskkill /F /PID %s" % sys.argv[3],shell=True)
            print "wait resAgent to be killed ...."
            kill.wait()
            dirUpdateTo = sys.argv[1]
            dirUpdateFrom = sys.argv[2]
            if os.path.isdir(dirUpdateTo):
                shutil.rmtree(dirUpdateTo,ignore_errors=True)
                time.sleep(5)
                print "delete old version success"
            if os.path.isdir(dirUpdateFrom):
                shutil.copytree(dirUpdateFrom,dirUpdateTo)
                time.sleep(5)
                print "Copy new version success, will restart new resAgent"
                newPath = os.path.join(dirUpdateTo, "resAgent", "src", "resAgent.py")
                time.sleep(1)
                subprocess.Popen("resAgent.py", shell=True)
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