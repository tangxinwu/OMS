"""
检测应用状态插件
created by tangxinwu
"""
# 引入ssh连接插件
try:
    import ssh_plugin
except ImportError:
    from infrastructure.plugin import ssh_plugin

# 引入自定义open
try:
    from CustomOpen import CustomOpen
except ImportError:
    from infrastructure.plugin.CustomOpen import CustomOpen


from abc import abstractmethod, ABC
import os


class ProcessCheck(ABC):
    """
    根据进程名检测进程状态
    :param host ：检查的进程所在的主机
    :
    """
    def __init__(self, host):
        """
        :param host: 传入目标机器
        self._ssh : 保存paramiko 链接的实例
        self.result: 保存最终的字典
        self.default_cmd: 保存linux命令
        """
        self._ssh = ssh_plugin.SSHConnect(host)
        self.result = {}
        self.status_cmd = ""
        self.restart_cmd = ""
        self.stop_cmd = ""

    def _set_status_cmd(self, cmd):
        """
        可以设置检测status的cmd的命令
        :param cmd: 传入新的cmd
        :return:
        """
        self.status_cmd = cmd

    def _set_restart_cmd(self, cmd):
        """
        可以设置重启进程的cmd命令
        :return:
        """
        self.restart_cmd = cmd

    def _set_stop_cmd(self, cmd):
        """
        可以设置停止进程的cmd命令
        :param cmd:
        :return:
        """
        self.stop_cmd = cmd

    @abstractmethod
    def check_process_status(self):
        """
        检查进程状态
        :return: 返回运行状态Running or Exited
        """

    @abstractmethod
    def restart_process(self):
        """
        重启进程
        :return: 返回重启后的提示
        """

    @abstractmethod
    def read_from_config(self):
        """
        读取配置文件
        :return:
        """

    @abstractmethod
    def modify_config(self):
        """
        修改配置文件
        :return:
        """

    @abstractmethod
    def stop_process(self):
        """
        停止进程
        :return:
        """

    def close(self):
        """
        关闭ssh链接
        :return:
        """
        self._ssh.close()


class GoTaskCheck(ProcessCheck):
    """
    处理go-task的进程状态
    """
    def __init__(self, host, gotask_path):
        """
        使用父类的初始化方法
        :param host:
        :param gotask_path: 传入go task 路径
        """
        super().__init__(host)
        self.gotask_path = gotask_path
        self._set_status_cmd("""ps -ef | grep go-task | grep -v grep""")
        self._set_restart_cmd("""cd %s ;a=`ps -ef | grep go-task | grep -v grep | awk -F ' ' '{print $2}'`;
                                 if [[ $a == "" ]];then %s/go-task start -d;else kill -9 $a;fi &&
                                 %s/go-task start -d""" % (self.gotask_path, self.gotask_path, self.gotask_path))
        self._set_stop_cmd("""cd %s ;a=`ps -ef | grep go-task | grep -v grep | awk -F ' ' '{print $2}'`;
                                 if [[ $a == "" ]];then %s/go-task start -d;else kill -9 $a;fi""" % (self.gotask_path,
                                                                                                     self.gotask_path))

    def check_process_status(self):
        """
        检查
        :return:
        """
        result = self._ssh.run_command(self.status_cmd)
        return (lambda x: "Running" if x else "Exited")(result)

    def restart_process(self):
        """
        重启进程
        :return: 返回重启状态
        """
        result = self._ssh.run_command(self.restart_cmd)
        return (lambda x: x if x else "重启成功")(result)

    def read_from_config(self, config_name):
        """
        读取go task的配置文件
        :return:
        """
        config_path = os.path.join(self.gotask_path, "config/" + config_name)

        config_content = self._ssh.run_command("""cat {}""".format(config_path))
        return config_content

    def modify_config(self, config_content, config_name):
        """
        修改config文件
        bak_path ： 新加的备份地址
        :return:
        """
        config_path = os.path.join(self.gotask_path, "config/" + config_name)
        bak_path = os.path.join(self.gotask_path, "config/" + config_name + ".bak")
        config_content = config_content
        self._ssh.run_command("""\\cp -rf {} {}""".format(config_path, bak_path))
        self._ssh.run_command("""echo '{}' > {}""".format(config_content.replace("'", '"'), config_path))


    def stop_process(self):
        """
        停止go-task进程
        :return:
        """
        result = self._ssh.run_command(self.stop_cmd)
        return (lambda x: x if x else "停止成功")(result)


if __name__ == "__main__":
    host = {
            "hostname": "192.168.1.123",
            "username": "root",
            "password": "111111",
            "port": "22"
            }
    p = GoTaskCheck(host, "/html/go-task")
    print(p.check_process_status())
    content = p.read_from_config()
    print(content)
    p.close()
