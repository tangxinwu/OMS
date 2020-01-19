"""
同步数据库插件
"""

from abc import ABC, abstractmethod
import os
import difflib
from infrastructure.models import *
from OMS import settings

try:
    import ssh_plugin
except ImportError:
    from infrastructure.plugin import ssh_plugin


class DataBaseTableError(Exception):
    """
    备份数据库表报错
    """

    def __str__(self):
        return "传入的数据库参数为list类型时，无法指定table"


class DataBaseNotNull(Exception):
    """
    数据库名字为空报错
    """

    def __str__(self):
        return "没有指定数据库"


class CreateDB:
    """
    创建一个DB的实例包括3个属性
    username， password， port
    """

    def __init__(self, DBname, host="localhost"):
        self.DBName = DBname
        self._username = ""
        self._password = ""
        self._port = 3306
        self._host = host

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
                       "_username", "_password", "_port", "_host", "host"):
            raise KeyError("设置的属性名必须是username,password,port,host")
        else:
            super().__setattr__(key, value)


class CreateHost:
    """
    创建一个host实例 使得他的__str__值为一个json，用于匹配ssh_plugin
    传入的
    """
    def __init__(self, hostname, server_ip):
        """
            :param hostname: 传入host的命名（自定义）
            :param server_ip: 传入host的ip方便在后台数据库里面查找对应的密码
        """
        self._hostname = hostname
        self._server_ip = server_ip
        self._data = {}

    def _precheck(self):
        """
        生成要返回的数据类型 把结果返回给self._data
        :return:
        """
        self._data.update({"hostname": self._server_ip})
        self._data.update({"username": "root"})
        self._data.update({"password": Server.objects.get(wan_ip=self._server_ip).password})
        self._data.update({"port": 22})

    def __call__(self, *args, **kwargs):
        self._precheck()
        return self._data


class SyncDB(ABC):
    """
    同步数据库抽象类
    """

    def __init__(self, src="", des=""):
        """
        初始化同步数据库方法
        :param src : 需要同步的数据库的用户名和密码
        :param des : 目标数据库地址

        """
        self._src = src
        self._des = des
        self._backup_cmd = ""
        self._restore_cmd = ""
        self._database_name = ""
        self._table_name = ""

    def set_sync_or_export_database_name(self, database_name):
        """
        设置要备份（同步或者导出）的库的名字
        :param database_name:
        :return:
        """
        self._database_name = database_name

    def set_sync_or_export_table_name(self, table_name):
        """
        设置要备份（同步或者导出）的表的名字
        :param table_name:
        :return:
        """
        # 在传入的数据库为列表 以及传入的表名为列表的时候会报错 不允许存在
        if type(self._database_name) == list and type(table_name) == list:
            raise DataBaseTableError
        else:
            self._table_name = table_name

    def _middle_process(self):
        """
        中间处理过程
        :return:
        """
        assert self._database_name != "", "请先运行set_sync_or_database_name加入要同步或者导出的数据库名"

    @abstractmethod
    def db_precheck(self, database="", table=""):
        """
        检查DB和库和表的方法，根据传入的参数的不同。
        :param database:
        :param table:
        :return:
        """

    @abstractmethod
    def export(self):
        """
        开始执行导出操作
        :return:
        """

    @abstractmethod
    def sync(self):
        """
        开始执行同步操作
        :return:
        """

    @abstractmethod
    def compare_files(self):
        """
            比较文件
        :return:
        """

    def __setattr__(self, key, value):
        if key.endswith("DB"):
            if not isinstance(value, CreateDB) or not value:
                raise IndexError("参数只能在lDB和dDB之间选择,参数类型为CreateDB实例！或者为空")
        super().__setattr__(key, value)


class SyncMysql(SyncDB):
    """
    同步mysql数据库
    """

    def __init__(self, src="", des=""):
        """
        父类的初始化方法

        :param lDB: 需要同步的数据库的用户名和密码
                lDB的写法是{“host”:"xx","username":"xxxs","password":"xx"}
        :param dDB: 目标数据库地址
                dDB的写法是{“host”:"xx","username":"xxxs","password":"xx"}
        """
        super().__init__(src=src, des=des)
        self.host_connections = []
        self.host_trasport_connections = []
        self.cache_export = os.path.join(settings.STATICFILES_DIRS[0], "cache/export")
        self.cache_import = os.path.join(settings.STATICFILES_DIRS[0], "cache/import")
        [self.host_connections.append(ssh_plugin.SSHConnect(CreateHost(host.host, host.host)())) for host in
         (self._src, self._des) if host]
        [self.host_trasport_connections.append(ssh_plugin.SFTPConnect(CreateHost(host.host, host.host)())) for host in
         (self._src, self._des) if host]

    def db_precheck(self, database="", table=""):
        """
        检查
        :return:
        """
        check_result = {}
        # 没有传入database和table参数返回所有数据库
        if not database and not table:
            for conn in self.host_connections:
                result = conn.run_command(
                    """/usr/local/mysql5.6/bin/mysql -uroot -p{} -e "show databases \G" | grep -v "*" """.format(
                        (lambda x, y: x.password if x.host == conn.host.get("hostname") else y.password)(self._src, self._des))
                )
                check_result[conn.host.get("hostname")] = [
                    db.replace("\n", "").replace(" ", "") for db in result.split("Database:") if db]
            return check_result
        # 传入了database但是没有传入 table明返回该数据库下 所有的表名
        if database and not table:
            for conn in self.host_connections:
                result = conn.run_command(
                    """/usr/local/mysql5.6/bin/mysql -uroot -p{} {} -e "show tables \G" | grep -v "*" """.format(
                        (lambda x, y: x.password if x.host == conn.host.get("hostname") else y.password)(self._src, self._des),
                        database
                    )
                )
                check_result[conn.host.get("hostname")] = [
                    db.replace("\n", "").replace(" ", "") for db in result.split("Tables_in_" + database +": ") if db]
            return check_result
        # 同时传入 开始备份数据库
        if database and table:
            pass

    def sync(self, sync_detail):
        """
        mysql 同步
        :return:
        """
        self.export()

        des_conn = self.host_connections[1]
        des_sftp = self.host_trasport_connections[1]
        des_sftp.send_file(os.path.join(self.cache_export, sync_detail.get("src_table") + ".sql"),
                           os.path.join("/tmp", sync_detail.get("src_table") + ".sql"))
        result = des_conn.run_command("""mysql -uroot -p{} {} < {}.sql""".format(self._des.password,
                                                                                 sync_detail.get("des_db"),
                                                                                os.path.join("/tmp", sync_detail.get("src_table"))))
        print(result)  # 调试结果

    def export(self, options=""):
        """
        执行导出
        :return:
        """
        self._middle_process()
        # 数据库导出结构和表导出结构的参数不一样
        # 没办法只能这么干 哎 蛋疼
        # 现在导出参数
        # plus_args 导出表结构时候插入的参数
        if options == "stru_only":
            plus_args = "--opt -d"
        else:
            plus_args = ""
        if self._table_name:
            # 导出单张表
            for conn in self.host_connections:
                conn.run_command("""mysqldump -uroot -p{} {} {} {}> /tmp/{}.sql""".format(self._src.password,
                                                                                          plus_args,
                                                                                  self._database_name,
                                                                                  self._table_name,
                                                                                      self._table_name))
        else:
            # 导出整个库
            for conn in self.host_connections:
                conn.run_command("""mysqldump -uroot -p{} {} {}> /tmp/{}.sql""".format(
                    self._src.password, plus_args, self._database_name, self._database_name))
        # 拉取sql文件
        for sftp in self.host_trasport_connections:
            print(sftp.host)
            sftp.get_file("/tmp/{}.sql".format((lambda x, y: y if y else x)(self._database_name, self._table_name)),
                          os.path.join(self.cache_export, "{}.sql".format((lambda x, y: y if y else x)(self._database_name, self._table_name))))
            break
        return "/static/cache/export/{}.sql".format((lambda x, y: y if y else x)(self._database_name, self._table_name))

    def compare_files(self, compare_detail, output=os.path.join(settings.TEMPLATES[0].get("DIRS")[0], "report.html")):
        """
        比较两个文件 生成html
        :param self:
        :param output: 输出对比文件的路径 一般放到static静态文件夹下，然后用/display_report/对应的views渲染他
        :return:
        """
        self._gen_compare_files(compare_detail)
        c = difflib.HtmlDiff()

        f1 = open("/tmp/f1.txt")

        f2 = open("/tmp/f2.txt")

        report = open(output, "w+")

        f1_text = f1.readlines()

        f2_text = f2.readlines()

        report.write(c.make_file(f1_text, f2_text, context=True))

        f1.close()
        f2.close()
        report.close()

    def _gen_compare_files(self, compare_detail):
        """
            生成需要比较的文件
        """
        host1 = {
            "hostname": compare_detail.get("src_server"),
            "username": "root",
            "password": Server.objects.get(wan_ip=compare_detail.get("src_server")).password,
            "port": 22}
        host2 = {
            "hostname": compare_detail.get("des_server"),
            "username": "root",
            "password": Server.objects.get(wan_ip=compare_detail.get("des_server")).password,
            "port": 22}
        conn_host1 = ssh_plugin.SSHConnect(host1)
        conn_host2 = ssh_plugin.SSHConnect(host2)
        # 同时传入src_table和des_table值
        if all([compare_detail.get("src_table"), compare_detail.get("des_table")]):
            make_f1 = conn_host1.run_command("""/usr/local/mysql5.6/bin/mysql -uroot -p{} {} -e "show create table {}" """.format(
                self._src.password, compare_detail.get("src_db"), compare_detail.get("src_table")
            ))
            make_f2 = conn_host2.run_command("""/usr/local/mysql5.6/bin/mysql -uroot -p{} {} -e "show create table {}" """.format(
                self._des.password, compare_detail.get("des_db"), compare_detail.get("des_table")
            ))
            with open("/tmp/f1.txt", "w+") as f1:
                f1.write(make_f1.replace("\\n", "\r"))

            with open("/tmp/f2.txt", "w+") as f2:
                f2.write(make_f2.replace("\\n", "\r"))

        # 没有传入src_table和des_table值

        if not compare_detail.get("src_table") and not compare_detail.get("des_table"):
            f1_tmp_text = ""
            f2_tmp_text = ""
            # 设置write_flag 使得每次写入的文件名 分别为f1和f2 然后放到后面去对比
            write_flag = 0
            for db_server, tables in self.db_precheck(database=compare_detail.get("src_db")).items():

                if write_flag == 0:
                    for table in tables:
                        make_f1 = conn_host1.run_command(
                            """/usr/local/mysql5.6/bin/mysql -uroot -p{} {} -e "show create table {}" """.format(
                                self._src.password, compare_detail.get("src_db"), table))
                        f1_tmp_text += make_f1
                    with open("/tmp/f1.txt", "w+") as f1:
                        f1.write(f1_tmp_text.replace("\\n", "\r").replace("Warning: Using a password on the command line interface can be insecure.", "\r"))
                    write_flag += 1
                else:
                    for table in tables:
                        make_f2 = conn_host2.run_command(
                            """/usr/local/mysql5.6/bin/mysql -uroot -p{} {} -e "show create table {}" """.format(
                                self._des.password, compare_detail.get("des_db"), table))
                        f2_tmp_text += make_f2
                    with open("/tmp/f2.txt", "w+") as f2:
                        f2.write(f2_tmp_text.replace("\\n", "\r").replace("Warning: Using a password on the command line interface can be insecure.", "\r"))


if __name__ == "__main__":
    p1 = CreateDB("测试用的数据库")
    setattr(p1, "username", "root")
    setattr(p1, "password", "123456")
    setattr(p1, "port", 3306)
    setattr(p1, "host", "192.168.10.196")
    # print(vars(p1))

    p2 = CreateDB("241的服务器")
    setattr(p2, "username", "root")
    setattr(p2, "password", "123456")
    setattr(p2, "port", 3306)
    setattr(p2, "host", "192.168.1.241")
    # print(vars(p2))

    ps = SyncMysql(p1, p2)
    print(vars(ps))
    ps.set_sync_database_name("asaaa")
    ps.set_sync_table_name("bbbb")
    # ps.run()
    ps.db_prcheck()
