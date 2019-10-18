"""OMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from infrastructure import views as iv

urlpatterns = [
    path('admin/', admin.site.urls),                           # 后台admin界面
    path('ip_interface/', iv.ip_interface),                    # ip显示界面
    path('login/', iv.login),                                  # 登录界面
    path("version_update/", iv.version_update),                # 版本升级界面
    path("logs_gather/", iv.logs_gather),                      # 日志显示界面
    path("logout/", iv.logout),                                # 登出界面
    path("shortcut/", iv.shortcut),                            # 快捷入口的界面
    path("test1/<test_params>/", iv.test1),                                   # 测试的接口
    path("docker_local_registry/", iv.docker_local_registry),  # 查找docker本地仓库的界面
    path("h5_update/", iv.h5_update),                          # 用于h5 升级的界面
    path("check_log/", iv.check_log),                          # 用于获取最近升级日志的接口
    path("go-task/", iv.go_task),                              # 用于检测go-task状态的接口
    path("self_invoke/", iv.self_invoke),                      # 自助申请更新流程
    path("self_invoke_result/", iv.self_invoke_result),        # 自助申请审批界面
    path("ssh_failed_page/", iv.ssh_failed_page),              # web链接SSH失败的失败界面
    path("aliyun_check/", iv.aliyun_check),                    # 检测阿里云服务器
    path("version_tags_check/", iv.version_tags_check)         # 检测某项目的tags （get方法传参数）
]
