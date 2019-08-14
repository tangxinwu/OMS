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
    path('port_check/', iv.port_check),                        # 端口检测界面
    path("version_update/", iv.version_update),                # 版本升级界面
    path("logs_gather/", iv.logs_gather),                      # 日志显示界面
    path("logout/", iv.logout),                                # 登出界面
    path("shortcut/", iv.shortcut),                            # 快捷入口的界面
    path("apk/", iv.apk),                                      # 打包 apk的界面
    path("test1", iv.test1),                                   # 测试的接口
    path("docker_local_registry/", iv.docker_local_registry),  # 查找docker本地仓库的界面
    path("h5_update/", iv.h5_update),                          # 用于h5 升级的界面
    path("check_log/", iv.check_log),                          # 用于获取最近升级日志的接口
    path("go-task/", iv.go_task),                              # 用于检测go-task状态的接口
    path("config_transfor/", iv.config_transfor),              # 用于转换配置文件
    path("wiki_public/", iv.wiki_public),                      # 关联wiki文档和用户之间的关注关系
    path("self_invoke/", iv.self_invoke),                      # 自助申请更新流程
    path("self_invoke_result/", iv.self_invoke_result),        # 自助申请审批界面
]
