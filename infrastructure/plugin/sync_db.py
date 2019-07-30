"""
同步数据库插件
"""

from abc import ABC, abstractmethod

try:
    import ssh_plugin
except ImportError:
    from infrastructure.plugin import ssh_plugin
# finally:
#     from infrastructure.models import Server


class CreateDB:
    """
    创建一个DB的实例包括3个属性
    username， password， port
    """
    def __init__(self, DBname):
        self.DBName = DBname
        self._username = ""
        self._password = ""
        self._port = 3306

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def port(self):
        return self._port

    @username.setter
    def username(self, value):
        self._username = value

    @password.getter
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    @port.setter
    def port(self, value):
        self._port = value

    def __setattr__(self, key, value):
        if key not in ("username", "password", "port", "DBName",
                       "_username", "_password", "_port"):
            raise KeyError("设置的属性名必须是username,password,port")
        else:
            super().__setattr__(key, value)


class SyncDB(ABC):
    """
    同步数据库抽象类
    """
    def __init__(self, lDB, dDB):
        """
        初始化同步数据库方法
        :param lDB : 需要同步的数据库的用户名和密码
        :param dDB : 目标数据库地址
        所有传入的host(lDB, dDB)信息格式为：
        {
            "username" : "root",
            "password" : "123456",
            "port" : 3306
        }

        """
        self._cmd_dconnect = ssh_plugin.SSHConnect(daddr)
        self._sftp_dconnect = ssh_plugin.SFTPConnect(daddr)
        self._cmd_rconnect = ssh_plugin.SSHConnect(laddr)
        self._sftp_rconnect = ssh_plugin.SFTPConnect(laddr)
        self._sync_script = ""
        self._database_name = []

    @abstractmethod
    def _set_backup_script(self, cmd):
        """
        设置远程服务器备份脚本
        :param cmd:
        :return:
        """

    @abstractmethod
    def _set_restore_script(self, cmd):
        """
        设置本地服务器还原脚本
        :param cmd:
        :return:
        """

    def set_sync_database_name(self, database_name):
        """
        设置要备份（同步）的库的名字
        :param database_name:
        :return:
        """
        if type(database_name) == list:
            self._database_name += list
        else:
            self._database_name.append(database_name)

    @abstractmethod
    def _middle_process(self):
        assert self._database_name != "" "请先运行set_sync_database_name加入要备份的数据库名"

        """
        中间处理过程
        :return: 
        """

    def close(self):
        for i in vars(self):
            print(str(i))


class SyncMysql(SyncDB):
    """
    同步mysql数据库
    """
    def __init__(self, lDB, dDB):
        """
        父类的初始化方法

        :param lDB: 需要同步的数据库的用户名和密码
        :param dDB: 目标数据库地址
        """
        super().__init__(lDB, dDB)


if __name__ == "__main__":
    p1 = CreateDB("测试用的数据库")
    setattr(p1, "username", "root")
    setattr(p1, "password", "123456")
    setattr(p1, "port", 3306)
    print(getattr(p1, "password"))

    p2 = CreateDB("241的服务器")
    setattr(p2, "username", "root")
    setattr(p2, "password", "123456")
    setattr(p2, "port", 3306)
    print(getattr(p2, "password"))

    SyncMysql()