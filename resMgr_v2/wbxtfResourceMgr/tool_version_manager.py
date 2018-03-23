import json
import requests
import os
import socket
import shutil
import zipfile
try:
    import urlparse
except ImportError:
    # Renamed to urllib.parse in Python 3
    from urllib import parse as urlparse
from wbxtf.WBXTFLogex import WBXTFLogInfo, WBXTFLogWarning, WBXTFLogError
from util.network_utils import ping, CURRENT_PLATFORM
from wbxtfResourceMgr import wbxtfResMgrConfig


__author__ = 'Ares Ou (weou@cisco.com)'


TOOL_PATH = 'C:\\PF_Tools\\' if CURRENT_PLATFORM == 'windows' else '/opt/PF_Tools/'

PORTAL_BASE_URL = ""
# if ping('192.168.22.11'):
#     PORTAL_BASE_URL = 'http://192.168.22.11:7777'
# else:
#     PORTAL_BASE_URL = 'http://10.195.135.80:7777'

#JSON_FILE_NAME = 'tools.json'
JSON_FILE_NAME = os.path.dirname(wbxtfResMgrConfig.__file__)+ r"/tools.json"

# field names for tool JSON object
FIELD_LOCAL_VER = 'local_version'
FIELD_REMOTE_VER = 'remote_version'
FIELD_LOCAL_PATH = 'local_path'
FIELD_REMOTE_PATH = 'remote_path'
FIELDS = (FIELD_LOCAL_VER, FIELD_REMOTE_VER, FIELD_LOCAL_PATH, FIELD_REMOTE_PATH)

REMOTE_NAME = 'name'
REMOTE_VERSION = 'version'
REMOTE_PATH = 'path'
REMOTE_FIELDS = (REMOTE_NAME, REMOTE_VERSION, REMOTE_PATH)


class ToolVersionManager(object):
    """Tool manager for wbxtfResMgr.

    Load, update and save tool list on local machine and
    machine portal.

    Auto download necessary tools and update expired versions.

    Save tool list to JSON file.
    """
    def __init__(self, base_url=None):
        self._base_url = base_url if base_url else PORTAL_BASE_URL
        self._tools = None
        self._machine_ip = socket.gethostbyname(socket.gethostname())
        self.load()

    def _get_json(self, url):
        """Use GET method and parse JSON response from url."""
        response = requests.get(url)
        if response.status_code == 200:
            # HTTP OK
            return response.json()

        return None

    def _get_field(self, tool_name, version, field_name):
        try:
            return self._tools[tool_name][version].get(field_name, '')
        except KeyError:
            return None

    def _send_json(self, url, data, method='POST'):
        return getattr(requests, method.lower())(url, json=data)

    def _set_field(self, tool_name, version, field_name, value):
        self._tools[tool_name][version][field_name] = value

    def _assemble_default_tool_path(self, name, version):
        return os.path.join(os.path.join(TOOL_PATH, name), version)

    def _add_tool(self, name, version, path):
        """Add a tool to local list and save to file. Return True
        if succeed else return False.
        """
        if name not in self._tools:
            self._tools[name] = {version: {FIELD_LOCAL_PATH: path}}
        elif version not in self._tools[name]:
            self._tools[name][version] = {FIELD_LOCAL_PATH: path}
        else:
            self._set_field(name, version, FIELD_LOCAL_PATH, path)

        # save the tool list to file after added a tool
        self.save()

        return True

    def add_remote_tool(self, name, version, target_folder=None):
        """Add a tool from remote, try to download it and put it to
        default path.
        """
        target_folder = target_folder if target_folder else self._assemble_default_tool_path(name, str(version))
        if self.download_tool(name, version, target_folder):
            WBXTFLogInfo("Deploy tool%s version:%s to target_folder%s success" % (name, version, target_folder))
            return self._add_tool(name, version, target_folder)
        else:
            WBXTFLogError('Tool download for %s %s failed...' % (name, version))
            return False

    def add_local_tool(self, name, version, local_path):
        """Add a tool from local path, do not validate if file exists."""
        return self._add_tool(name, version, local_path)

    def remove_tool(self, tool_name, version):
        try:
            del self._tools[tool_name][version]
            if not self._tools[tool_name]:
                # remove the tool from dictionary if no version is installed
                del self._tools[tool_name]
            self.save()
        except KeyError:
            # tool not found or version not found
            return False
        else:
            return True

    def load(self):
        """Load all tools from local file. Try to read from web if local
        file is empty or doesn't exist.
        """
        try:
            with open(JSON_FILE_NAME, 'rb') as f:
                self._tools = json.load(f)
        except (IOError, ValueError):
            self._tools = {}
            # TODO: read from web if file does not exist
            self.save()

    def save(self):
        """Save tool list into local file and report to
        the web portal.
        """
        with open(JSON_FILE_NAME, 'wt') as f:
            f.write(json.dumps(self._tools))

    def _unzip_and_delete(self, file_path, target_folder=None):
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return False

        target_folder = target_folder if target_folder is not None else os.path.dirname(file_path)

        with zipfile.ZipFile(file_path) as zip_file:
            zip_file.extractall(path=target_folder)

        # remove the zip file after extraction.
        os.remove(file_path)

        return True

    def download_tool(self, name, version, target_folder):
        remote_path = self.get_remote_path(name, version)
        if not remote_path:
            return False
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

    def all_tools(self):
        """Return a dictionary object containing all tool
        names and versions.
        """
        return self._tools

    def report(self):
        """Report local tool list to the web portal."""
        url = urlparse.urljoin(self._base_url, '/api/v1/machines/%s' % self._machine_ip)
        data = {'tools': self.all_tools()}

        # try PUT first
        response = self._send_json(url, data, method='PUT')
        if response.status_code != 200:
            WBXTFLogWarning('Failed to update machine tool list, try POST now...')
            # machine does not exist, use POST instead of PUT
            response = self._send_json(url, data, method='POST')

        if response.status_code == 200:
            WBXTFLogInfo('Tool list of machine %s succesfully updated to remote host.' % self._machine_ip)
            return True

        WBXTFLogError('Failed to update machine tool list...')

        return False

    def get_tool_info_from_remote(self, tool_name, version):
        """Get the tool record from remote portal. Returns a parsed
        JSON object.
        """
        url = urlparse.urljoin(self._base_url, '/api/v1/apps/%s/%s' % (tool_name, version))
        return self._get_json(url)

    def get_remote_path(self, tool_name, version):
        """Get download path from web portal with the tool name."""
        response = self.get_tool_info_from_remote(tool_name, version)
        if response:
            return response[REMOTE_PATH]

        return None

    def get_local_path(self, tool_name, version):
        """Get local path of tool with name."""
        return self._get_field(tool_name, version, FIELD_LOCAL_PATH)

    def prepare_tools(self, tool_list, callback=None):
        succeed_count = 0
        WBXTFLogInfo("Preparing tools:%s" % tool_list)
        for tool in tool_list:
            if not self.get_local_path(tool[REMOTE_NAME], tool[REMOTE_VERSION]):
                if self.add_remote_tool(tool[REMOTE_NAME], tool[REMOTE_VERSION]):
                    WBXTFLogInfo("prepare tool:%s success" % tool)
                    succeed_count += 1
                else:
                    WBXTFLogError("prepare tool:%s failed" % tool)
            else:
                succeed_count += 1
        # # If all tools are prepared successfully
        return succeed_count == len(tool_list)



if __name__ == '__main__':
    manager = ToolVersionManager()
    print manager.all_tools()
    manager.remove_tool('wbxtfresmgr', 'test')
    print manager.all_tools()
    manager.remove_tool('wbxtfresmgr', 'test2')
    print manager.all_tools()

    # add a list of tools
    manager.prepare_tools([{REMOTE_NAME: 'wbxtfresmgr', REMOTE_VERSION: 'test'},
                           {REMOTE_NAME: 'wbxtfresmgr', REMOTE_VERSION: 'test2'}])

    print manager.all_tools()
    manager.report()
