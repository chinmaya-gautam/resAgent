import sys
import os

basePath = os.path.abspath(__file__ + "/../../")
libsPath = os.path.abspath(basePath + "/libs")
grpcIncludes = os.path.abspath(basePath + "/grpc_includes")
sys.path.insert(0, basePath)
sys.path.insert(1,libsPath)
sys.path.insert(2, grpcIncludes)


import time
import shutil
import subprocess
import urllib2
import zipfile
import requests
import datetime

from WBXTFLogex import *
from resAgentConfig import *

class ResAgentAutoUpdater:

    def __init__(self, resAgentPid = None, resMgrPid = None):
        """
        :type resMgr: wbxtfResMgr
        """
        self._currentVersion = RES_AGENT_VERSION
        self._updateURL = RES_AGENT_UPDATE_URL
        self._tempFolder = RES_AGENT_TEMP_FOLDER
        self._updateCheckInterval = RES_AGENT_UPDATE_CHECK_INTERVAL

        self._updateInfo = None
        self.resAgentPid = resAgentPid
        self.resMgrPid = resMgrPid
        self.start()

    def download_updateFiles(self, remote_path, target_folder):
        file_name = os.path.basename(remote_path)
        local_path = os.path.join(target_folder, file_name)

        # remove all files if target folder already exists,
        # then re-create the folder again.
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder, ignore_errors=True)
        os.makedirs(target_folder)

        if self._download_file(remote_path, local_path):
            # unzip if the file is an archive
            if zipfile.is_zipfile(local_path):
                return self._unzip_and_delete(local_path)
            else:
                # directly return True if it is not zip file
                return True
        else:
            return False

    def _download_file(self, remote_path, local_path, chunk_size=1024):
        """Download a tool from path. By default, the file should be a zip,
        but not a directory.
        """
        WBXTFLogInfo("toolPackage:(%s)  is downloading .... " % remote_path)
        stream = requests.get(remote_path, stream=True)
        original_size = int(stream.headers['Content-Length'])
        with open(local_path, 'wb') as f:
            for chunk in stream.iter_content(chunk_size=chunk_size):
                if chunk:   # filter out keep-alive new chunks
                    f.write(chunk)

        downloaded_size = os.path.getsize(local_path)
        WBXTFLogInfo('download:%s to local:%s finished Original: %d, downloaded: %d' %
                     (remote_path,local_path,original_size, downloaded_size))

        # check if the file is downloaded completely.
        return original_size == downloaded_size

    def _unzip_and_delete(self, file_path, target_folder=None):
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return False

        target_folder = target_folder if target_folder is not None else os.path.dirname(file_path)

        with zipfile.ZipFile(file_path) as zip_file:
            zip_file.extractall(path=target_folder)

        # remove the zip file after extraction.
        os.remove(file_path)

        return True


    def checkForUpdates(self):

        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(
            url=self._updateURL,
        )
        request.get_method = lambda: "GET"
        strResponse = opener.open(request).read()
        dictResponse = eval(strResponse)
        WBXTFLogDebug("updateCheck response=\n%s" % strResponse)

        if isinstance(dictResponse, dict) and dictResponse.has_key("version") and dictResponse.has_key("path"):
            if self._currentVersion != dictResponse["version"]:
                self._updateInfo = dictResponse
                return True

        return False

    def updateResAgent(self):

        ret = self.download_updateFiles(self._updateInfo["path"], self._tempFolder)
        if ret == True:
            dirUpdateTo = os.path.abspath(os.path.dirname(__file__) + "/../")
            dirUpdateFrom = self._tempFolder
            resUpdater = self._tempFolder + r"\resUpdater.py"

            # Copy the resUpdater to the temp folder
            shutil.copy("resUpdater.py", resUpdater)
            # Copy the Copy util to temp folder
            shutil.copy("CopyUtil.py", self._tempFolder + r'\CopyUtil.py')

            WBXTFLogInfo("Will do self upgrade. dirUpdateTo:%s , dirUpdateFrom: %s" %
                         (dirUpdateTo, dirUpdateFrom))

            subprocess.Popen(["python", resUpdater, dirUpdateTo, dirUpdateFrom, str(os.getpid()), str(self.resAgentPid), str(self.resMgrPid)])
        else:
            WBXTFLogWarning("Download new version of resAgent failed.")

    def start(self):

        while True:
            try:
                # Check for update
                isUpdateAvailable = self.checkForUpdates()
                if isUpdateAvailable:
                    self.updateResAgent()

                time.sleep(self._updateCheckInterval)
            except KeyboardInterrupt:
                WBXTFLogInfo("Received a keyboard interrupt, will exit ...")
                sys.exit(0)
            except Exception as e:
                WBXTFLogError("Exception running auto updater: %s" % (str(e)))


class AutoUpdater:

    def __init__(self):
        pass


if __name__ == "__main__":
    WBXTFLogSetLogLevel(WBXTF_DEBUG)
    timeStamp = datetime.datetime.fromtimestamp(time.time()).strftime("%y%m%d%H%M%S")
    logFilePath = os.path.join(os.path.split(os.path.realpath(__file__))[0], "../log/ResAgentAutoUpdater_log_%s.txt" % timeStamp)
    WBXTFLogSetLogFilePath(logFilePath)

    if len(sys.argv) == 3:
        resAgentAutoUpdater = ResAgentAutoUpdater(sys.argv[1], sys.argv[2])
    else:
        resAgentAutoUpdater = ResAgentAutoUpdater()
    resAgentAutoUpdater.start()