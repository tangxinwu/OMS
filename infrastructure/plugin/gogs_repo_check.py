"""
查询gogs仓库内容的库
使用接口
http://127.0.0.1:8001/version_tags_check/?query_type=NoneTags&project_name=app

使用 \w{8}-\w{4}-\w{4}-\w{4}-\w{12} 正则分辨project_name传入的是否是task——id
"""
import pymysql
import sys

argvs = sys.argv

parms_list = ["database", "query_type", "project_name"]


class VersionUpdateConnectDB:
    def __init__(self, parms_list, argvs):
        self._parms_list = parms_list
        self._argvs = argvs
        self.__params_check()
        self.__phase_params()
        self._conn = ""
        self.data = ""
        self.__init_db()

    def __params_check(self):
        """
        参数检测
        :return:
        """
        for parm in parms_list:
            if "--" + parm not in self._argvs:
                print("参数错误！")
                sys.exit(0)

    def __phase_params(self):
        """
        参数解析
        :return:
        """
        for parm in parms_list:
            self.__setattr__(parm, self._argvs[(self._argvs.index("--" + parm) + 1)])

    def __init_db(self):
        """
        链接数据库然后查询
        :return:
        """
        self._conn = pymysql.connect(host="192.168.1.246", user="devops", password="devops", database=self.database)
        cur = self._conn.cursor()
        if self.query_type == "all_tags":
            sql = """select tag_name from `release` where repo_id  in (select id from repository where name='{}');""".format(self.project_name)
            cur.execute(sql)
            data = "||".join([i[0] for i in cur.fetchall()])
        else:
            sql = """select note from `release` where repo_id=(select id from repository where name='{}') and tag_name='{}';""".format(
                self.project_name, self.query_type)
            cur.execute(sql)
            # 查找结果为空的话 返回空值
            try:
                data = cur.fetchall()[0][0]
            except IndexError:
                data = ""
        self.data = data

    def __close_db(self):
        if self._conn:
            self._conn.close()


if __name__ == "__main__":
    p = VersionUpdateConnectDB(parms_list, sys.argv)
    print(vars(p))
    print(p.data)
