#! coding=utf-8
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from infrastructure.models import *
from django.views.decorators.csrf import csrf_exempt
import subprocess
import paramiko
from infrastructure.plugin import ssh_plugin, CustomOpen, process_check, vcenter_connect, CustomEmail, gogs_repo_check, login_plugin, sync_db
import os
import re
import json
from infrastructure.task import version_update_task, check_go_task_status
from django_celery_results.models import TaskResult
from django.forms.models import model_to_dict
import pytz
import time
import uuid
import base64
import socket
import requests
from dwebsocket.decorators import accept_websocket

# Create your views here.


def need_login(func):
    """
    登录用装饰器
    :param func:
    :return:
    """
    def _wapper(request):
        auth_process = login_plugin.LoginSession(request)
        if not auth_process():
            auth_process.clean_cache()
            return HttpResponseRedirect("/login/")
        else:
            return func(request)
    return _wapper


@need_login
@csrf_exempt
def ip_interface(request):
    """
    变量名：
        login_name : session里面 读login_name 字段用来判断是否登陆

    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    if logged_role not in ("master",):
        return HttpResponseRedirect("/logout/")
    lan_servers = Server.objects.filter(wan_ip__icontains="192.168")
    wan_servers = Server.objects.exclude(wan_ip__icontains="192.168")
    host = request.GET.get("host", "")
    if host:
        host_wan_ip = Server.objects.get(wan_ip=host).wan_ip
        host_password = base64.b64encode(Server.objects.get(wan_ip=host).password.encode("utf8")).decode("utf8")
        try:
            s1 = socket.socket()
            s1.connect((host_wan_ip, 22))
            return HttpResponse("http://192.168.1.240:8888/?hostname={}&&username=root&&password={}".format(
                                        host_wan_ip, host_password))
        except:
            return HttpResponse("/ssh_failed_page/")

    return render(request, "ip_interface.html", locals())


@csrf_exempt
def login(request):
    if request.POST:
        auth_message = {}
        avalible_keys = ["login_name", "login_password"]
        for key in avalible_keys:
            auth_message[key] = request.POST.get(key, "")
        if all(auth_message.values()):
            auth_process = login_plugin.LoginSession(request, auth_message.get("login_name"), auth_message.get("login_password"))
            if not auth_process():
                auth_process.clean_cache()
                return HttpResponse("failed")
            else:
                return HttpResponse("succ")
        else:
            return HttpResponse("参数错误！")
    return render(request, "login.html", locals())


def logout(request):
    """
    登出接口， 清除session和redis
    :param request:
    :return:
    """
    logout_process = login_plugin.LoginSession(request)
    logout_process.clean_cache()
    return HttpResponse("已经成功登出！")


@csrf_exempt
@need_login
def version_update(request):
    """
    版本更新界面views
    默认使用tar包结构
    流程：本地服务器先从本地的gits 拉取需要的版本的代码（临时文件夹位置/root/temp_files），
         然后在本地打包（打包好的tar包的临时位置/root/workspace/工程名/工程名.tar）
         然后再传送到目标服务器的/tmp目录下 然后解压选取src文件夹覆盖（这个操作是写在shell脚本中）
    2019-01-15增加使用mq 异步同步机制 ， 使用django-celery
    version_update_task就是task任务的主程序
    2019-10-16 前端增加传入tags 可以根据仓库项目有的tags来拉取代码， 对应的拉取tags
    2020-03-02 前端增加传入options_content 可以决定是否更新config 默认option_no 不更新配置文件
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    all_application = Application.objects.exclude(ApplicationName="web_app")  # 排除H5的升级 H5升级的特殊性 另外开个版面
    all_application_title = set([i.ApplicationName for i in all_application])
    if request.POST:
        application_id = request.POST.get("application_id", "")
        application_tags = request.POST.get("application_tags", "NullTags")
        application_options = request.POST.get("application_options", "ConfigNo")
        result = version_update_task.apply_async((str(application_id) + "_" + str(int(time.time())) + "_" + application_tags + "_" + application_options,),
                                                 queue="update_version",
                                                 routing_key="task_a")
        # 尝试获取tags对应的更新说明
        UpdateDescription = requests.get("http://" + request.get_host() + "/version_tags_check/?query_type={}&project_name={}".format(application_tags, application_id)).content.decode("utf8")
        # try:
        UpdateLogs.objects.create(UpdateName=Application.objects.get(id=application_id),UpdateServer=Application.objects.get(id=application_id).ApplicationServer,
                                  UpdateTaskId=result, UpdateUser=logged_user, UpdateTags=application_tags,
                                  UpdateBranch=(lambda x: (lambda y: y if y else "master")(x) if not application_tags else "")(Application.objects.get(id=application_id).ApplicationBranch),
                                  UpdateDescription=UpdateDescription,
                                  UpdateUseConfig=(lambda x: "是" if x=="ConfigYes" else "否")(application_options))
        return HttpResponse("任务(id={})已经开始".format(result))
        # except:
        #     return HttpResponse("任务(id={})开始失败".format(result))
    return render(request, "version_update.html", locals())


@csrf_exempt
def version_tags_check(request):
    """
    查找当前project_name（项目名）对应的所有的tags
    当query_type为all_tags的时候返回所有该项目的tags用||分割开来
    当query_type为其他的时候 返回该tags对应的tags内容（升级内容）
    project_name ：
            可以传入数字 如果是数字 从Application 中返回ApplicationName
    :param request:
    :return:
    """
    query_type = request.GET.get("query_type", "")
    project_name = (lambda x: x if not re.findall("[0-9]+", x) else Application.objects.get(id=x).ApplicationName)(request.GET.get("project_name", ""))
    parms_list = ["database", "query_type", "project_name"]
    argvs = ["--database", "gogs", "--query_type", query_type, "--project_name", project_name]
    gogs_check_process = gogs_repo_check.VersionUpdateConnectDB(parms_list, argvs)
    return HttpResponse(gogs_check_process.data)


@csrf_exempt
@need_login
def logs_gather(request):
    """
    检查日志的views, 显示固定行数日志到本地显示
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    all_logs = ApplicationLogs.objects.all()
    if request.POST:
        logs_id = request.POST.get("logs_id", "")
        # lines 参数决定返回最后多少行的日志
        lines = request.POST.get("lines", "")
        # 模糊查找后返回给前段的列表 点击列表再返回的具体的日志名字
        logfile = request.POST.get("logfile", "")
        # 过滤的关键字
        filter_keywords = request.POST.get("filter_words", "")

        selected_logs = ApplicationLogs.objects.get(id=logs_id)
        host = {"hostname": selected_logs.ApplicationOnTheServer.wan_ip, "username": "root",
                "password": selected_logs.ApplicationOnTheServer.password, "port": 22}
        ssh = ssh_plugin.SSHConnect(host)
        check_log_files_cmd = """ls {} | grep {}""".format(selected_logs.PathOfLogs, selected_logs.LogsFileName)
        check_result = ssh.run_command(check_log_files_cmd)
        # 分段去除空白的项
        check_result_list = check_result.split("\n")[:-1]
        # 前段有返回logfile的
        # lambda 函数确定前端有没有返回过滤的关键字 如果有则拼接grep
        if logfile:
            check_cmd = """tail -n{} {} {}""".format(lines,
                                                     os.path.join(selected_logs.PathOfLogs, logfile),
                                                     (lambda x: "| grep " + x if x else "")(filter_keywords))
        else:
            ssh.close()
            return HttpResponse("<br>".join(check_result_list))

        # 替换成网页版的换行符
        log_result = ssh.run_command(check_cmd).replace("\n", "<br>")
        ssh.close()
        return HttpResponse(log_result)
    return render(request, "logs_gather.html", locals())


@csrf_exempt
@need_login
def shortcut(request):
    """
    快捷入口
    checked_vm_host_uuid:保存了需要操作的vm的uuid值，可以使用StartStopVM里面注释中
                         中的一段查找vm的uuid
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    checked_vm_host_uuid = {
        "192.168.1.243": "500f7d0b-deb9-2008-179c-2c1f43bc8803",
        "192.168.1.236": "500f360b-c8d0-d78b-cd5a-155b1ff946cd",
        "192.168.1.238": "500fdb76-f01f-17d7-3fc2-776a00395979"
    }
    if request.method == "POST":
        action = request.POST.get("action", "")
        host = request.POST.get("host", "")
        if host:
            process = vcenter_connect.StartStopVM(SSL=False)
            process.build_arg_parser()
            process.add_argument(host=host, uuid=checked_vm_host_uuid.get(host))
            result = process.handler(action=action)
            return HttpResponse(result)

    return render(request, "shortcut.html", locals())


@need_login
def docker_local_registry(request):
    """
    docker本地仓库列表
    使用curl 检查url check_registry_url 获取到所有的repositories
    使用curl 检查url http://local_registry_server:local_registry_port/v2/{获取的repository}/tags/list 获取到所有的tags
    每次刷新页面的时候 都要返回值 前段页面返回的是一个json 用遍历key value的方法显示
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    images_name = {}
    local_registry_server = "192.168.1.251"
    local_registry_port = "5000"
    check_registry_url = "http://{}:{}/v2/_catalog".format(local_registry_server, local_registry_port)

    host = {"hostname": local_registry_server, "username": "root",
            "password": Server.objects.get(wan_ip=local_registry_server).password, "port": 22}
    ssh = ssh_plugin.SSHConnect(host)
    repository_result = eval(ssh.run_command("""curl -s {}""".format(check_registry_url)))
    all_repository = repository_result.get("repositories")
    for rep in all_repository:
        tag = eval(ssh.run_command("curl -s http://{}:{}/v2/{}/tags/list".format(
                                                    local_registry_server, local_registry_port, rep))).get("tags")
        images_name[rep] = tag[0]
    ssh.close()
    return render(request, "docker_local_registry.html", locals())


@csrf_exempt
@need_login
def h5_update(request):
    """
    只处理h5的 更新
    只处理applicationName=web_app的后台应用
    除了post多传了一个sub_dir的参数外 其他的和version_update没有任何区别
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    all_application = Application.objects.filter(ApplicationName="web_app")
    if request.POST:
        application_id = request.POST.get("application_id", "")
        sub_dir = request.POST.get("sub_dir", "")
        selected_application = Application.objects.get(id=int(application_id))
        time_flag = str(int(time.time()))
        # 运行本地拉取脚本
        pull_cmd = "/usr/bin/sh {} {} {} {}".format(selected_application.ApplicationUpdateScriptPath,
                                                 selected_application.ApplicationName,
                                                 (lambda x: x if x else "master")(selected_application.ApplicationBranch),
                                                 time_flag)

        p = subprocess.Popen(pull_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout = p.stdout.read().decode("utf8")
        stderror = p.stderr.read().decode("utf8")
        # 传送脚本到remote服务器 ####
        host = {"hostname": selected_application.ApplicationServer.wan_ip, "username": "root",
                "password": selected_application.ApplicationServer.password, "port": 22}
        try:
            transport = ssh_plugin.SFTPConnect(host)
        except paramiko.ssh_exception.SSHException:
            return HttpResponse("连接服务器超时！请检查服务器ip是否正确!")

        transport.send_file(selected_application.ApplicationUpdateScriptPathAfter,
                            os.path.join("/tmp", os.path.basename(selected_application.ApplicationUpdateScriptPathAfter)))
        # 传送tar文件到remote服务器
        transport.send_file("/root/workspace/{}/{}_{}.tar".format(selected_application.ApplicationName,
                                                               selected_application.ApplicationName,
                                                                  time_flag),
                            "/tmp/{}_{}.tar".format(selected_application.ApplicationName, time_flag))
        transport.close()

        # 远程运行脚本 ##
        ssh = ssh_plugin.SSHConnect(host)
        cmd = "sh {} {} {} {}".format(os.path.join("/tmp", os.path.basename(selected_application.ApplicationUpdateScriptPathAfter)),
                                selected_application.ApplicationPath, sub_dir, time_flag)
        result = ssh.run_command(cmd)
        return HttpResponse((lambda x, y: x if x else y)(stdout, stderror) + result)
    return render(request, "h5_update.html", locals())


@csrf_exempt
@need_login
def check_log(request):
    """

    POST 参数check：检查最后5个更新日志记录，返回给前端
                   纯接口 没有返回页面
                   return: {任务的uuid:[任务的中文名字, 任务的状态, 任务的完成时间]}
    POST 参数detail_check：接受前段传入的task_id
                   return:任务返回的结果
    """

    if request.method == "POST":
        action = request.POST.get("action", "")
        if action == "check":
            last_data = {}
            return_lines = 10
            # checked_objects = TaskResult.objects.all().order_by("-date_done")
            checked_objects = UpdateLogs.objects.all().order_by("-UpdateTime")[:return_lines]
            for i in checked_objects:
                try:
                    update_logs_object = TaskResult.objects.get(task_id=i.UpdateTaskId)
                    last_data[i.UpdateTaskId] = [i.UpdateName, i.UpdateServer, i.UpdateTags, i.UpdateBranch, update_logs_object.status,
                                            str(update_logs_object.date_done.astimezone(pytz.timezone("Asia/Shanghai"))),
                                                 i.UpdateUser, i.UpdateUseConfig]
                except TaskResult.DoesNotExist:
                    # updateLog表里面有这个task id 但是TaskResult不存在的，显示PROCESSING
                    last_data[i.UpdateTaskId] = [i.UpdateName, "PROCESSING", "waiting", "waiting", "waiting", "waiting", "waiting", "waiting"]
            return HttpResponse(json.dumps(last_data, ensure_ascii=False))
        if action == "detail_check":
            task_id = request.POST.get("task_id", "")
            detail_objects = TaskResult.objects.get(task_id=task_id)
            detail = detail_objects.result
            return HttpResponse(json.dumps({"message": detail}, ensure_ascii=False))
    return HttpResponse("没有输入！")


@csrf_exempt
@need_login
def go_task(request):
    """
    操作go-task的后台view函数
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    all_gotask = GoTask.objects.all()
    if request.method == "POST":
        flag = request.POST.get("action", "")
        ip = request.POST.get("ip", "")
        path = request.POST.get("path", "")
        config_name = request.POST.get("config_name", "")
        if ip:
            # 链接客户机的参数
            host = {
                "hostname": ip,
                "username": "root",
                "password": Server.objects.get(wan_ip=ip).password,
                "port": 22
            }
            task = process_check.GoTaskCheck(host, path)
            # 检查config.json 内容
            if flag == "check":
                restart_result = task.restart_process()
                config_content = task.read_from_config(config_name)
                task.close()
                return HttpResponse(json.dumps({"host": host,
                                                "restart_result": restart_result,
                                                "config_content": config_content.replace("\\n", "</br>")},
                                                ensure_ascii=False))
            # 修改内容分支
            if flag == "modify":
                config_content = request.POST.get("config_content", "")
                task.modify_config(config_content, config_name)
                task.restart_process()
                task.close()
                return HttpResponse("修改成功！go-task已经重启！")

            # 重启服务分支
            if flag == "restart":
                result = task.restart_process()
                task.close()
                return HttpResponse(result)

            # 停止服务分支
            if flag == "stop":
                result = task.stop_process()
                task.close()
                return HttpResponse(result)
        else:
            # 检查所有服务器的状态时 不需要传入ip参数
            # 查看go所有gotask服务器的状态 在/go-task/页面刷新的时候启用
            if flag == "check_all_status":
                check_go_task_status.apply_async((), queue="check_gotask_status", routing_key="task_b")
                return HttpResponse("检查go-task服务器结束")

    return render(request, "go-task.html", locals())


@csrf_exempt
@need_login
def self_invoke(request):
    """
    自助申请流程

    :param logged_user 从session读取, 记录登录的人的登录名
    :param logged_role 从session读取, 记录登录的人的角色
    :param all_application 排除web_app以外的所有记录在数据库中的更新记录
    :param all_auditingUser 查找所有用户表中 role为auditing的 审批者
    流程:
        前端传入需要更新的应用id(表application), 动作action, auditing_id审批者id -> 检测传入的参数的正确性 ->
        发送邮件到对应的审批者下的邮箱
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    # 排除H5的升级 H5升级的特殊性 另外开个版面
    all_application = Application.objects.filter(ApplicationBranch=None,
                                                 ApplicationLevel__application_level="生产").exclude(
                                                 ApplicationName="web_app")
    all_auditingUser = User.objects.filter(role_type__RoleType="auditing")
    if request.POST:
        # action_list = ["web_check"]
        application_id = request.POST.get("application_id", "")
        action = request.POST.get("action", "")
        auditing_id = request.POST.get("auditing_id", "")
        # 检测传值
        if not all([application_id, action, auditing_id]):
            return HttpResponse("非法传值")
        try:
            Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return HttpResponse("没有找到对应的应用!")
        # 传入的token用于审批人查找审批单
        self_invoke_token = str(uuid.uuid1())
        # 发送邮件通知 sender 和reciver都有默认值
        try:
            email = CustomEmail.SendMail(reciver=User.objects.get(id=auditing_id).user_email)
            sent_result = email.send_mail("审批邮件", self_invoke_token)
        except CustomEmail.SendMailFail:
            return HttpResponse("发送申请邮件失败, 发送的目标邮箱为{}, 请确定邮箱是否正确".format(User.objects.get(id=auditing_id).user_email))
        # 写入数据库
        SelfInvoke.objects.create(InVokedApplicationId_id=application_id, InVokedUser=logged_user,
                                  InvokedToken=self_invoke_token, AuditingUser_id=auditing_id)

        return HttpResponse(sent_result)
    return render(request, "self_invoke.html", locals())


@csrf_exempt
def self_invoke_result(request):
    """
    申请自助流程结果处理
    从邮箱中拿取的uuid查找当前登录用户的审批下的 申请
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    if logged_role not in ("auditing", "master"):
        return HttpResponseRedirect("/logout/")
    all_invoke = SelfInvoke.objects.all()
    if request.POST:
        # 用于前端显示的字典
        is_deal_map = {
            0: "未处理",
            1: "已处理",
            2: "已拒绝"
        }
        search_token = request.POST.get("search_token", "").replace(" ", "").replace("\t", "")
        auditing_action = request.POST.get("auditing_action", "")
        application_id_token = request.POST.get("application_id_token", "")
        if search_token:
            try:
                token_search_result = SelfInvoke.objects.get(InvokedToken=search_token, AuditingUser__login_name=logged_user)
                print(request.session.get("login_info"))

            except SelfInvoke.DoesNotExist:
                # 没有找到审批内容时返回faild
                return HttpResponse("FAILD")
            search_token_dict_result = model_to_dict(token_search_result)
            search_token_dict_result["InVokedApplication"] = Application.objects.get(id=search_token_dict_result["InVokedApplicationId"]).ApplicationName
            search_token_dict_result["AuditingUserName"] = User.objects.get(id=search_token_dict_result["AuditingUser"]).login_name
            search_token_dict_result["deal_status"] = is_deal_map.get(search_token_dict_result.get("isdeal"))
            return HttpResponse(json.dumps(search_token_dict_result))
        if auditing_action == "deny":
            SelfInvoke.objects.filter(InvokedToken=application_id_token.split("||")[1]).update(isdeal=2)
            return HttpResponse("已经拒绝请求!")
        if auditing_action == "agreed":
            result = version_update_task.apply_async((str(application_id_token.split("||")[0]) + "_" + str(int(time.time())),),
                                                     queue="update_version",
                                                     routing_key="task_a")
            # try:
            UpdateLogs.objects.create(UpdateName=Application.objects.get(id=application_id_token.split("||")[0]),
                                      UpdateTaskId=result, UpdateUser=request.session.get("login_info", "").get("name", "") + "(自助)")
            SelfInvoke.objects.filter(InvokedToken=application_id_token.split("||")[1]).update(isdeal=1)
            return HttpResponse("已经成功处理申请请求!")
    return render(request, "self_invoke_result.html", locals())


@csrf_exempt
def ssh_failed_page(request):
    return render(request, "ssh_failed_page.html", locals())


@csrf_exempt
def aliyun_check(request):
    """
    配合定时任务 检测阿里云过期时间的接口
    :param request:
    :return:
    """
    all_aliyun_server = Server.objects.filter(aliyun_server_expire__isnull=False)
    temp_dict = dict()
    for aliyun_server in all_aliyun_server:
        temp_dict[aliyun_server.wan_ip] = str(aliyun_server.aliyun_server_expire.astimezone(pytz.timezone("Asia/Shanghai")))
    return HttpResponse(json.dumps(temp_dict, ensure_ascii=False))


@csrf_exempt
def show_3rd_custom_detail(request):
    """
    把数据库中第三方消费记录
    :param request:
    :return:
    """
    return HttpResponse("生成第三方消费记录数据接口")


@csrf_exempt
@need_login
def syncdb(request):
    """
    同步和检测数据库不同和同步
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    if logged_role not in ("auditing", "master"):
        return HttpResponseRedirect("/logout/")
    all_db_server = Server.objects.filter(is_db_server=True)
    if request.POST:
        action = request.POST.get("action", "")
        server_ip = request.POST.get("server_ip", "")
        database = request.POST.get("database", "")
        src_server = request.POST.get("src_server", "")
        src_db = request.POST.get("src_db", "")
        src_table = request.POST.get("src_table", "")
        des_server = request.POST.get("des_server", "")
        des_db = request.POST.get("des_db", "")
        des_table = request.POST.get("des_table", "")
        options = request.POST.get("options", "")
        if action == "db_check":
            p1 = sync_db.CreateDB(str(server_ip))
            setattr(p1, "username", "root")
            setattr(p1, "password", "123456")
            setattr(p1, "port", 3306)
            setattr(p1, "host", server_ip)
            # # p2 = sync_db.CreateDB("241的服务器")
            # # setattr(p2, "username", "root")
            # # setattr(p2, "password", "123456")
            # # setattr(p2, "port", 3306)
            # # setattr(p2, "host", "192.168.1.241")
            # # # print(vars(p2))
            #
            ps = sync_db.SyncMysql(p1)
            # ps.set_sync_database_name("asaaa")
            # ps.set_sync_table_name("bbbb")
            # # ps.run()
            result = ps.db_precheck()
            return HttpResponse(json.dumps(result))
        if action == "table_check":
            p1 = sync_db.CreateDB(str(server_ip))
            setattr(p1, "username", "root")
            setattr(p1, "password", "123456")
            setattr(p1, "port", 3306)
            setattr(p1, "host", server_ip)
            ps = sync_db.SyncMysql(p1)
            result = ps.db_precheck(database=database)
            return HttpResponse(json.dumps(result))
        if action == "compare":
            compare_detail = {
                "src_server": src_server,
                "src_db": src_db,
                "src_table": src_table,
                "des_server": des_server,
                "des_db": des_db,
                "des_table": des_table
            }
            src = sync_db.CreateDB(str(src_server))
            des = sync_db.CreateDB(str(des_server))
            setattr(src, "username", "root")
            setattr(src, "password", "123456")
            setattr(src, "port", 3306)
            setattr(src, "host", compare_detail.get("src_server"))
            setattr(des, "username", "root")
            setattr(des, "password", "123456")
            setattr(des, "port", 3306)
            setattr(des, "host", compare_detail.get("des_server"))
            ps = sync_db.SyncMysql(src, des)
            ps.compare_files(compare_detail)
            return HttpResponse("比较分支")
        if action == "export":
            # 导出分支只关注于左边的部分 右边部分 忽略
            src = sync_db.CreateDB(str(src_server))
            setattr(src, "username", "root")
            setattr(src, "password", "123456")
            setattr(src, "port", 3306)
            setattr(src, "host", src_server)
            ps = sync_db.SyncMysql(src)
            ps.set_sync_or_export_database_name(src_db)
            if src_table:
                ps.set_sync_or_export_table_name(src_table)
            print(options)
            download_url = ps.export(options=options)
            return HttpResponse(download_url)
        if action == "sync":
            sync_detail = {
                "src_server": src_server,
                "src_db": src_db,
                "src_table": src_table,
                "des_server": des_server,
                "des_db": des_db,
                "des_table": des_table
            }
            print(sync_detail)
            src = sync_db.CreateDB(str(src_server))
            des = sync_db.CreateDB(str(des_server))
            setattr(src, "username", "root")
            setattr(src, "password", "123456")
            setattr(src, "port", 3306)
            setattr(src, "host", sync_detail.get("src_server"))
            setattr(des, "username", "root")
            setattr(des, "password", "123456")
            setattr(des, "port", 3306)
            setattr(des, "host", sync_detail.get("des_server"))
            ps = sync_db.SyncMysql(src, des)
            ps.set_sync_or_export_database_name(src_db)
            ps.set_sync_or_export_table_name(src_table)
            ps.sync(sync_detail)
            return HttpResponse("同步分支")
    return render(request, "sync_db.html", locals())


def display_report(request):
    return render(request, "report.html", locals())


@accept_websocket
def cmd_check(request):
    request.session["login_info"] = {
        "name": "CMDOnly",
        "role": "master"
    }
    version_update(request)
    return HttpResponse("cmd专用")
