"""
Django settings for OMS project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import djcelery
from kombu import Exchange, Queue


TIME_ZONE = 'Asia/Shanghai'

# celery django 设置
djcelery.setup_loader()

CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

BROKER_URL = "amqp://admin:admin@127.0.0.1:5672/"  # 代理人 负责分发任务去worker

CELERY_RESULT_BACKEND = 'django-db'  # 指定使用哪个数据库保存djcelery的数据


CELERY_TIMEZONE = TIME_ZONE

# 自定义队列名用来分开
# 如果自己定义了队列 每次都要自己设置定义的 队列对应的task 要不然消费者无法消费
CELERY_QUEUES = (
    Queue("update_version", Exchange("update_version"), routing_key="task_a"),
    Queue("check_gotask_status", Exchange("check_gotask_status"), routing_key="task_b"),
    Queue("backup_vm", Exchange("backup_vm"), routing_key="backup_vm"),
    Queue("backup_db", Exchange("backup_db"), routing_key="backup_db"),

)

CELERY_ROUTES = {
    "infrastructure.task.update_version": {"queue": "update_version", "routing_key": "task_a"},
    "infrastructure.task.check_gotask_status": {"queue": "check_gotask_status", "routing_key": "task_b"},
    # "infrastructure.task.backup_vm": {"queue": "backup_vm", "routing_key": "backup_vm"},
    "infrastructure.task.backup_db": {"queue": "backup_db", "routing_key": "backup_db"},
}


# celery django 设置结束

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(v*e9rzjhqqpw1idt1s1!n^x!lb4u5i(c3d*)0$ow9n&gj*-h1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["192.168.1.240", "django", "127.0.0.1", "192.168.1.191", "192.168.10.69"]

# 设置session 超时时间
# SESSION_SAVE_EVERY_REQUEST = True
# SESSION_COOKIE_AGE = 60*5

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'infrastructure',
    'djcelery',
    'django_celery_results',
    # 'django_celery_beat'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'infrastructure.middleware.CustomHttpRequest.HttpPost2HttpOtherMiddleware'
]

ROOT_URLCONF = 'OMS.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["infrastructure/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'OMS.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
                    "infrastructure/statics",
                    )





