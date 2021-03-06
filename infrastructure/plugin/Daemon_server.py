#! coding=utf-8
"""
处理定时快照的守护进程
"""

import time
import datetime
import threading
import schedule
import daemon
import requests

# 加载连接vcenter模块
try:
    from infrastructure.plugin.vcenter_connect import CreateSnapshot
except ImportError:
    from vcenter_connect import CreateSnapshot

# 加载发送邮件模块
try:
    from infrastructure.plugin.CustomEmail import SendMail
except ImportError:
    from CustomEmail import SendMail


class MakeSnapshotThreading:
    """
    把创建快照的方法 封装成一个可调用的类

    """
    def __init__(self, ip):
        self.ip = ip

    def _snapshot(self):
        """
        封装的创建快照的内置方法
        :return:
        """
        p = CreateSnapshot(SSL=False)
        p.build_arg_parser()
        p.add_argument(host=self.ip,
                       name=str(datetime.datetime.now()),
                       description="Created by Daemon server!",
                       memory=True,
                       quiesce=False)
        p.handler()

    def _transfor_to_threading(self):
        """
        创建快照转成线程模式启动
        :return:
        """

        threading.Thread(target=self._snapshot).start()

    def __call__(self, *args, **kwargs):
        """
        使得类的实例可以被调用
        :param args:
        :param kwargs:
        :return:
        """
        self._transfor_to_threading()


class MakeSnapshotMethod:
    """
    根据参数返回对应创建snapshot的方法
    schedule 方法使用样例
    schedule.every(10).minutes.do(job)
    schedule.every().hour.do(job)
    schedule.every().day.at("10:30").do(job)
    schedule.every(5).to(10).days.do(job)
    schedule.every().monday.do(job)
    schedule.every().wednesday.at("13:15").do(job)
    """
    def __init__(self, params):
        self._params = params
        self._interval = self._params.get("interval")
        self._week_day = self._params.get("week_day")
        self._timing_unit = self._params.get("timing_unit")
        self._snap_date = self._params.get("snap_date")

    def make_process(self):
        if self._interval:
            return getattr(getattr(getattr(schedule, "every")(self._interval), self._timing_unit), "do")
        else:
            if self._week_day and self._snap_date:
                return getattr(getattr(getattr(getattr(schedule, "every")(), self._week_day), "at")(self._snap_date), "do")
            if self._week_day and not self._snap_date:
                return getattr(getattr(getattr(schedule, "every")(), self._week_day), "do")
            if not self._week_day and self._snap_date:
                return getattr(getattr(getattr(getattr(schedule, "every")(), "day"), "at")(self._snap_date), "do")
        return "error"


def snapshot_timer():
    """
    定时任务函数,收集所有定时任务
    :var schedule_list:保存由类MakeThreading创建实例，用于定时任务(schedule)的调用,因为不能传参数
    :var task_list: 保存接受完参数的创建snapshot的类
    :var connection: 保存sqlite3 连接
    :var cur: 指针游标
    :var data: 数据库中查到的所有定时任务
    :return:
    """
    schedule_list = list()
    task_list = list()
    params = dict()
    data = (
        # ("192.168.1.239", "", "", "", "16:22"),
        ("192.168.1.241", "", "", "", "00:10"),
        ("192.168.1.246", "", "", "", "00:15"),

    )

    for task in data:
        params["ip"] = task[0]
        params["interval"] = task[1]
        params["week_day"] = task[2]
        params["timing_unit"] = task[3]
        params["snap_date"] = task[4]
        task_list.append(MakeSnapshotMethod(params))
        schedule_list.append(MakeSnapshotThreading(params["ip"]))
        # 为什么要重置下 不是可以替换属性的吗？ 这里不重置的话 params 的值不会被覆盖....
        params = dict()
    for threading_task in zip(task_list, schedule_list):
        threading_task[0].make_process()(threading_task[1])
        try:
            threading_task[0].make_process()(threading_task[1])
        except TypeError:
            print("{} maybe not configurte yet!".format(threading_task[1].ip))
            continue


def aliyun_expire_check_timer():
    """
    阿里云过期提醒
    :param alter_time ：修改这个参数的默认值可以设置时间报警的阀值
    :param expire_check_url: 修改确认过期查询的接口地址
    :return:
    """
    check_time = "00:00"

    def expire_check(alert_time=10, expire_check_url="http://127.0.0.1:10088/aliyun_check/"):
        aliyun_expire_data = eval(requests.get(expire_check_url).content.decode("utf8"))
        current_time = datetime.datetime.now()
        for hostname, expire_time in aliyun_expire_data.items():
            temp_date = datetime.datetime.strptime(expire_time.split("+")[0], "%Y-%m-%d %H:%M:%S") - current_time
            if abs(temp_date.days) <= alert_time:
                p = SendMail()
                p.send_mail("阿里云过期提醒", "主机{} 即将到期，到期时间为{}".format(hostname, expire_time))
    schedule.every().day.at(check_time).do(expire_check)

# def test_timer():
#     def test():
#         f = open("/tmp/test.log", "a+")
#         f.write(str(datetime.datetime.now()) + "\n")
#         f.close()
#     schedule.every(10).seconds.do(test)


def schedule_change_host_password_timer():
    """
    定期修改主机root密码
    :return:
    """
    change_time = "00:00"

    def change_password():
        pass

    schedule.every().day.at(change_time).do(change_password)


if __name__ == "__main__":
    all_locals = locals().copy()
    with daemon.DaemonContext():
        for task in all_locals:
            if task.endswith("_timer"):
                all_locals.get(task)()
        while True:
            schedule.run_pending()
            time.sleep(1)
    # 调试请打开这个注释 注释掉上面的上下文管理器
    # for task in all_locals:
    #     if task.endswith("_timer"):
    #         all_locals.get(task)()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

