from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# set timezome
CELERY_TIMEZONE='Asia/Shanghai'
# 设置运行环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OMS.settings')
# 实例化一个Celery
app = Celery('OMS')
# 设置celery配置文件(此处为proj/settings.py)
app.config_from_object('django.conf:settings')
# 自动发现位于INSTALLED_APPS中app里面的task任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


