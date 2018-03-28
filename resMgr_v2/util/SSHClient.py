import sys
import os
pylibPath = os.path.abspath(__file__ + "/../../")
thirdPartyPath = os.path.abspath(pylibPath + "/ThirdParty")
sys.path.append(thirdPartyPath)

import paramiko
import os
import time
import logging

class SSHClient(object):
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        logging.getLogger("paramiko").setLevel(logging.WARNING)
    
    def __exec_cmd(self, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, self.port, self.username, self.password)
        stdin, stdout, stderr = ssh.exec_command(command)
        ssh.close()

    def __exec_cmd_return(self, command, input_data):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, self.port, self.username, self.password)
        stdin, stdout, stderr = ssh.exec_command(command)
        ret = stdout.read()
        ssh.close()
        return ret
    
    def __exec_cmd_returnx(self, command, input_data):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, self.port, self.username, self.password)
        transport = ssh.get_transport()
        session = transport.open_session()
        session.set_combine_stderr(True)
        session.get_pty()
        session.exec_command(command)
        output = self._run_poll(session, input_data)
        transport.close()
        ssh.close()
        return output
    
    def exec_cmd(self, command, *input_data):
        self.__exec_cmd_return(command, input_data)
    
    def exec_cmd_return(self, command, *input_data):        
        return self.__exec_cmd_return(command, input_data)
    
    def _run_poll(self, session, input_data, timeout = 60):
        '''
        Poll until the command completes.

        @param session     The session.
        @param timeout     The timeout in seconds.
        @param input_data  The input data.
        @returns the output
        '''
        interval = 0.2
        maxcount = timeout / interval
        curcount = 0

        # Poll until completion or timeout
        # Note that we cannot directly use the stdout file descriptor
        # because it stalls at 64K bytes (65536).
        input_idx = 0
        timeout_flag = False

        output = ''
        bufsize = 65536
        
        session.setblocking(0)
        while True:
            if session.recv_ready():
                data = session.recv(bufsize)
                output += data

                if session.send_ready():
                    if input_idx < len(input_data):
                        data = input_data[input_idx]
                        input_idx += 1
                        session.send(data)

            if session.exit_status_ready():
                break

            curcount += 1
            if curcount > maxcount:                
                timeout_flag = True
                break
            time.sleep(interval)

        if session.recv_ready():
            data = session.recv(self.bufsize)
            output += data
       
        if timeout_flag:            
            output += '\nERROR: timeout after %d seconds\n' % (timeout)
            session.close()

        return output
    

    
    def is_exists(self, file_path, flag = 'Local'):
        if flag == 'Local':
            return os.path.exists(file_path)
        elif flag == 'Remote':
            cmd = 'ls %s'%file_path
            ress = self.exec_cmd_return(cmd)
            if len(ress) > 0:
                return True
            return False
    
    def make_dirs(self, dir_path, flag = 'Local'):
        '''
        @param remote_dir: absolute dir path
        '''
        if flag == 'Local':
            ress = os.makedirs(dir_path)
        elif flag == 'Remote':
            cmd = 'mkdir -p %s'%dir_path
            ress = self.exec_cmd_return(cmd)
        return ress
    
    def __check_file_path_and_mkdir(self, file_path, flag):
        '''
        @param file_path: absolte path
        '''
        file_path = os.path.abspath(file_path)

        if file_path.find('\\') != -1:
            sep = '\\'
        else:
            sep = '/'
        dir_path = file_path[:file_path.rfind(sep)]
        if self.is_exists(dir_path):
            return True
        self.make_dirs(dir_path, flag)
        
    
    def put_file_to_server(self, local_file, remote_file):
        '''
        @param local_file: absolute path, not a dir
        @param remote_file: absolute path, not a dir
        '''
        if not self.is_exists(local_file, "Local"):
            return False
        self.__check_file_path_and_mkdir(remote_file, "Remote")
        
        t = paramiko.Transport((self.hostname, self.port))
        t.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(local_file, remote_file)
        t.close()
        
        if not self.is_exists(remote_file, "Remote"):
            return False
        return True
    
    def get_file_from_server(self, remote_file, local_file):
        '''
        @param local_file: absolute path, not a dir
        @param remote_file: absolute path, not a dir
        '''
        if not self.is_exists(remote_file, "Remote"):
            return False
        self.__check_file_path_and_mkdir(local_file, "Local")
        
        t = paramiko.Transport((self.hostname, self.port))
        t.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(remote_file, local_file)
        t.close()
        
        if not self.is_exists(local_file, "Local"):
            return False
        return True

def main():
    hostname = "192.168.4.28"
    port = 22
    username = 'root'
    password = 'pass'
    
    ssh = SSHClient(hostname, port, username, password)
    
#    for i in range(1, 5):
#        print ssh.exec_cmd_return('top -b -n1')
#        print '\n'
    #print ssh.is_exists('/opt/webex/mmp/logs/readme.txt', 'Remote')
    
    #print ssh.exec_cmd_return('top -b -n1')
    
#    print ssh.exec_cmd_return('sar -n DEV 2 2')
    
#    print ssh.exec_cmd_return('/root/demo')
    
    #print ssh.exec_cmd_interactive('rm /opt/webex/mmp/logs/log.txt', 'y')
    
#    print bool(ssh.exec_cmd_return('ls /opt/webex/config/'))
#    
#    filter = 'wbxwcs'
#    cmd = "top -b -n1 -H -p $(ps -ef | grep %s | awk '$0 !~/grep/ {print $2}')"%filter
#    print ssh.exec_cmd_return(cmd)
    #
    filter = 'wbxwcs'
    cmd1 = "top -b -n1 -H -p $(ps -ef | grep %s | awk '$0 !~/grep/ {print $2}')"%filter
    cmd2 = " | grep %s | sed -n '1'p | awk '{print $(NF-3)}' "%filter
    cmd = cmd1 + cmd2

    cmd = "top -b -n1 -u wrt-mmp"
    for i in range(0,10):
        ret = ssh.exec_cmd_return(cmd)
        print ret
        print str(i) + "   ###################################################################"
#    
#    for i in range(1, 10):
#        print ssh.exec_cmd_return(cmd)
    
    #print ssh.exec_cmd_return('cd /', 'ls')
    
#    ssh.make_dirs('/demo1/demo3', 'Remote')
#    
#    ssh.exec_cmd('mkdir /demo1/demo2/')
#    
#    print ssh.exec_cmd_return("cd /opt/webex/mmp/bin/;ls")
#    
#    ssh.put_file_to_server(r'readme.txt', r'/opt/webex/mmp/logs/readme.txt')
#    
#    ssh.get_file_from_server(r'/opt/webex/mmp/bin/Monitor.log', r'd:/Monitor.log')

if __name__ == '__main__':
    main()