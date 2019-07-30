#! coding=utf8
import paramiko


class HostFormatError(Exception):
    def __str__(self):
        return "传入的host格式错误"


class SSHConnect:
    """
    远程链接库
    """
    def __init__(self, host):
        self.connect = ""
        self.host = host
        self._connectInit()

    def __setattr__(self, key, value):
        if key == "host":
            if type(value) == dict:
                if "hostname" in value and "username" in value and "password" in value and "port" in value:
                    super().__setattr__(key, value)
                else:
                    raise HostFormatError
            else:
                raise HostFormatError
        else:
            super().__setattr__(key, value)

    def _connectInit(self):
        """
        连初始化
        :return:
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=self.host.get("hostname"), username=self.host.get("username"),
                    password=self.host.get("password"), port=self.host.get("port"))
        self.connect = ssh

    def run_command(self, cmd):
        """远程运行命令"""
        if self.connect:
            stdin, stdout, stderror = self.connect.exec_command(cmd)
            stdout_result = stdout.read().decode("utf8")
            stderr_result = stderror.read().decode("utf8")
        return (lambda x, y: x if x else y)(stdout_result,stderr_result)

    def close(self):
        """
        关闭ssh链接
        :return:
        """
        self.connect.close()


class SFTPConnect(SSHConnect):
    """
    使用SFTP连接目标服务器，默认端口使用22
    这是一个传送文件的雷
    """
    def __init__(self, host):
        """
        使用父类的构造方法
        :param host:
        """
        super().__init__(host)

    def __setattr__(self, key, value):
        """
        继承父类的检测参数方法
        :param key:
        :param value:
        :return:
        """
        super().__setattr__(key, value)

    def _connectInit(self):
        """
        初始化SFTP连接
        :return:
        """
        sftp = paramiko.Transport((self.host.get("hostname"), self.host.get("port")))
        sftp.connect(username=self.host.get("username"), password=self.host.get("password"))
        sftp_client = paramiko.SFTPClient.from_transport(sftp)
        self.connect = sftp_client

    def run_command(self, cmd):
        print("SFTP 里面已经放弃run command 方法，请使用send_file方法发送文件")

    def send_file(self, local_file, remote_file):
        """
        传送文件
        :param local_file: 本地文件
        :param remote_file: 远程服务器文件
        :return:
        """
        if not self.connect:
            self._connectInit()
        self.connect.put(local_file, remote_file)

    def get_file(self, remote_file, local_file):
        """
        获取文件
        :param remote_file: 远程服务器文件
        :param local_file:  保存到本地的地址
        :return:
        """
        if not self.connect:
            self._connectInit()
        self.connect.get(remote_file, local_file)


if __name__ == "__main__":
    host = {
        "hostname": "192.168.149.130",
        "username": "root",
        "password": "111111",
        "port": 22
    }
    p = SFTPConnect(host)
    try:
        p.send_file(r"C:\Users\tang\Desktop\new 1.txt", r"/tmp/new.txt")
    except:
        print("传送失败 请检查原因！")
    p.close()
