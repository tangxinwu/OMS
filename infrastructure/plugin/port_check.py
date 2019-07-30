#! /bin/env python

import paramiko

cmd = """chown -R nginx:nginx /html/*"""

host_info = {
    "hostname": "192.168.1.207",
    "username": "root",
    "password": "111111",
}


class ExecuteShellCmd:
    def __init__(self):
        self._sshconnect = ""
        self._initconnect()

    def _initconnect(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=host_info.get("hostname"),
                    username=host_info.get("username"),
                    password=host_info.get("password"))
        self._sshconnect = ssh

    def run_cmd(self, cmd):
        if not self._sshconnect:
            self._initconnect()
        self._sshconnect.exec_command(cmd)


if __name__ == "__main__":
    p = ExecuteShellCmd()
    p.run_cmd(cmd)

