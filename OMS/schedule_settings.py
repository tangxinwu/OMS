from celery.schedules import crontab
from celery.schedules import timedelta

from infrastructure.plugin import ssh_plugin

# 定时任务 在此编辑
CELERYBEAT_SCHEDULE = {
    # "每天定时备份的虚拟机192.168.1.232": {
    #     "task": "infrastructure.task.backup_vm",
    #     "schedule": crontab(minute=0, hour=0),
    #     "args": ("192.168.1.232",)
    # },
    # "每天定时备份的虚拟机192.168.1.241": {
    #     "task": "infrastructure.task.backup_vm",
    #     "schedule": crontab(minute=15, hour=0),
    #     "args": ("192.168.1.241",)
    # },
    # "每天定时备份的虚拟机192.168.1.246": {
    #     "task": "infrastructure.task.backup_vm",
    #     "schedule": crontab(minute=30, hour=0),
    #     "args": ("192.168.1.246",)
    # },
    # "测试定时函数": {
    #     "task": "infrastructure.task.test_task",
    #     "schedule": timedelta(seconds=5),
    #     "args": ()
    # },
    "测试数据库备份": {
        "task": "infrastructure.task.backup_db",
        "schedule": crontab(),
        "kwargs": ({
                    "host": "192.168.1.232",
                    "db_user": "root",
                    "db_password": "123456",
                    "backup_db_name": ["xhdj_dev"]
                    }),

    }


}


# 使用 自带的crontab 的定时任务
