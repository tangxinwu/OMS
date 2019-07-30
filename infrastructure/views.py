#! coding=utf-8
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from infrastructure.models import *
from django.views.decorators.csrf import csrf_exempt
import subprocess
import paramiko
from infrastructure.plugin import ssh_plugin, CustomOpen, process_check, vcenter_connect
import os
import re
import json
from infrastructure.task import version_update_task,check_go_task_status
from django_celery_results.models import TaskResult
import pytz
import pymysql
import time

# Create your views here.


def need_login(func):
    """
    登陆装饰器
    :param func: 传入装饰函数
    :return:
    """
    def _wapper(request):
        if not request.session.get("login_info", ""):
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
    xshell_path = User.objects.get(login_name=logged_user).xshell_path
    lan_servers = Server.objects.filter(wan_ip__icontains="192.168")
    wan_servers = Server.objects.exclude(wan_ip__icontains="192.168")
    host = request.GET.get("host", "")
    if host:
        host_wan_ip = Server.objects.get(wan_ip=host).wan_ip
        host_password = Server.objects.get(wan_ip=host).password
        try:
            subprocess.Popen(r"""{}\Xshell /url ssh://{}:{}@{}""".format(xshell_path, "root", host_password, host_wan_ip), shell=False)
        except:
            return HttpResponse("链接失败")

    return render(request, "ip_interface.html", locals())


@csrf_exempt
def login(request):
    """
    登入模块
    :param request:
    :return:
    """
    if request.method == "POST":
        login_name = request.POST.get("login_name", "")
        login_password = request.POST.get("login_password", "")
        result = User.objects.filter(login_name=login_name, login_password=login_password)
        if result:
            request.session["login_info"] = {"name": login_name, "role": result[0].role_type.RoleType}
            return HttpResponse("succ")
        else:
            return HttpResponse("failed")
    return render(request, "login.html", locals())


def logout(request):
    """
    登出模块
    :param request:
    :return:
    """
    try:
        del request.session["login_name"]
    except KeyError:
        pass
    return render(request, "login.html")


@need_login
@csrf_exempt
def port_check(request):
    """
    检测端口
    :param request:
    1、检测开启的端口使用GET方法, 检测前端是否有使用GET方法传送的server_name属性，如果有检测传入的server_name对应的服务器开启的端口数
       如果没有接收到server_name属性， 返回这个页面
    2、使用POST方法，重启端口， 重启服务使用本地脚本，然后传送到目标服务器运行， 本地脚本的位置为/root/scripts/service_scrpits/

    :return:
    """
    all_server = Server.objects.all()
    shell_check_script = """
        netstat -lntp 
    
    """
    server_name = request.GET.get("server_name", "")
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    # 查询端口的时候
    if server_name:
        server = Server.objects.get(server_name=server_name)
        host = {"hostname": server.wan_ip, "username": "root", "password": server.password, "port": 22}
        try:
            ssh = ssh_plugin.SSHConnect(host)
        except paramiko.ssh_exception.NoValidConnectionsError:
            return HttpResponse("连接失败，请确定该服务器在线或配置正确！")
        result = ssh.run_command(shell_check_script)
        port_list = re.findall(":[0-9]+", result)
        last_result = set([i.replace(":", "") for i in port_list if int(i.replace(":", "")) > 1])
        ssh.close()
        return HttpResponse(",".join(last_result))
    # 重启端口的时候
    if request.POST:
        serviceScript_basedir = r"/root/scripts/service_script"
        server_name = request.POST.get("server_name", "")
        port = request.POST.get("port", "")
        action = request.POST.get("action", "")
        print(server_name)
        print(port)
        try:
            # 发生这个异常需要在RemoteServerService中增加这个服务器对应的端口信息
            server = RemoteServerService.objects.get(ServiceAtServer__server_name=server_name, ServicePort=port)
        except RemoteServerService.DoesNotExist:
            return HttpResponse("{} 没有使用这个端口{}的相关信息，请在后台中配置！".format(server_name, port))
        ServiceName = server.ServiceName
        host = {"hostname": server.ServiceAtServer.wan_ip, "username": "root", "password": server.ServiceAtServer.password, "port": 22}

        # 传送本地脚本到目标服务器
        transport = ssh_plugin.SFTPConnect(host)
        local_script = os.path.join(serviceScript_basedir, server_name + "_" + ServiceName)
        print(local_script)
        if not os.path.isfile(local_script):
            return HttpResponse("本地没有相关的服务重启脚本，请在OMS服务器上先配置！ 服务器存放脚本文件路径为{}".format(str(local_script)))
        remote_script = os.path.join("/tmp", server_name + "_" + ServiceName)
        transport.send_file(local_script, remote_script)
        # 远程执行脚本
        ssh = ssh_plugin.SSHConnect(host)
        result = ssh.run_command("sh {} {} && rm -rf {}".format(remote_script, action, remote_script))
        return HttpResponse(result)

    return render(request, "port_check.html", locals())


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
    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    print(logged_role)
    all_application = Application.objects.exclude(ApplicationName="web_app")  # 排除H5的升级
    all_application_title = set([i.ApplicationName for i in all_application])
    if request.POST:
        application_id = request.POST.get("application_id", "")
        result = version_update_task.apply_async((application_id,), queue="update_version", routing_key="task_a")
        # try:
        UpdateLogs.objects.create(UpdateName=Application.objects.get(id=application_id),
                                  UpdateTaskId=result, UpdateUser=logged_user)
        return HttpResponse("任务(id={})已经开始".format(result))
        # except:
        #     return HttpResponse("任务(id={})开始失败".format(result))
    return render(request, "version_update.html", locals())


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
def apk(request):
    """
    先拉取git到本地(local_workspace) 本地检查文件完整性和配置（主要是每个模块下的build.gradle和根工程下gradle.properties）

    :param request:
    :return:
    """
    logged_user = request.session.get("login_info", "").get("name", "")
    logged_role = request.session.get("login_info", "").get("role", "")
    # AndroidSDK, local_workspace, ProjectName, file_filter从后台配置中读取
    AndroidSDK = r"/home/tangxinwu/Desktop/AndroidSDK"
    local_workspace = r"/home/tangxinwu/Desktop/workspace"
    ProjectName = "Android"
    all_build_file_list = []
    file_filter = {"build.gradle", "gradle.properties"}
    for i in os.walk(local_workspace):
        if i[2]:
            for k in i[2]:
                if k in file_filter:
                    all_build_file_list.append(
                        os.path.join(i[0], k).replace(os.path.join(local_workspace, ProjectName), "").replace("/", "", 1))

    if request.POST:
        file_content = request.POST.get("file_content", "")
        action = request.POST.get("action", "")
        select_config = request.POST.get("select_config", "")
        config_path = os.path.join(os.path.join(local_workspace, ProjectName), select_config)
        # 修改配置文件
        if action == "modify":
            f = CustomOpen.CustomOpen(config_path, "w")
            file_content = file_content.replace("</br>", "\\n").replace("&nbsp;", "\r")
            f.write(file_content)
            f.close()
            return HttpResponse("修改成功")
        # 读取配置文件到前段显示
        if action == "show":
            f = CustomOpen.CustomOpen(config_path)
            # 返回html能识别的版本文件内容
            data = f.read().replace("\\n", "</br>").replace("\r", "&nbsp;")
            f.close()
            return HttpResponse(data)
        # build apk
        if action == "build":
            # 增加java环境变量
            old_env = os.environ["PATH"]
            new_env = old_env + ":" + "/usr/local/jdk1.8.0_191/bin:/usr/local/gradle-4.4/bin"
            os.environ["PATH"] = new_env
            os.environ["CLASSPATH"] = "/usr/local/jdk1.8.0_191/lib/dt.jar:/usr/local/jdk1.8.0_191/lib/tools.jar"
            os.environ["GRADLE_HOME"] = "/usr/local/gradle-4.4/"
            os.chdir(os.path.join(local_workspace, ProjectName))
            os.system("""echo 'sdk.dir={}' > {}""".format(AndroidSDK,
                                                          os.path.join(os.path.join(local_workspace, ProjectName), "local.properties")))
            build_cmd = """gradle clean build -x test --info > {}""".format(os.path.join(os.path.join(local_workspace, ProjectName), "build.log"))
            process = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            result = (lambda x, y: x if x else y)(process.stdout.read(), process.stderr.read())
            return HttpResponse(result)
        # 获取build日志
        if action == "log":
            return_lines = 20
            lines = request.POST.get("lines", "")
            log_path = os.path.join(os.path.join(local_workspace, ProjectName), "build.log")
            host = {"hostname": "localhost", "username": "tangxinwu", "password": "sakamotomaaya1", "port": 22}
            cmd = """sed -n {},{}p {}""".format((lambda x: x if x else 1)((int(lines)-1)*return_lines),
                                                int(lines)*return_lines, log_path)
            print(cmd)
            ssh = ssh_plugin.SSHConnect(host)
            result = ssh.run_command(cmd)
            return HttpResponse(json.dumps({"lines": lines, "result": result}, ensure_ascii=False))
    return render(request, "apk.html", locals())


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
        # 运行本地拉取脚本
        pull_cmd = "/usr/bin/sh {} {} {}".format(selected_application.ApplicationUpdateScriptPath,
                                                 selected_application.ApplicationName,
                                                 (lambda x: x if x else "")(selected_application.ApplicationBranch))

        p = subprocess.Popen(pull_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
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
        transport.send_file("/root/workspace/{}/{}.tar".format(selected_application.ApplicationName,
                                                               selected_application.ApplicationName),
                            "/tmp/{}.tar".format(selected_application.ApplicationName))
        transport.close()

        # 远程运行脚本 ##
        ssh = ssh_plugin.SSHConnect(host)
        cmd = "sh {} {} {}".format(os.path.join("/tmp", os.path.basename(selected_application.ApplicationUpdateScriptPathAfter)),
                                selected_application.ApplicationPath, sub_dir)
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
            return_lines = 5
            # checked_objects = TaskResult.objects.all().order_by("-date_done")
            checked_objects = UpdateLogs.objects.all().order_by("-UpdateTime")[:return_lines]
            for i in checked_objects:
                try:
                    update_logs_object = TaskResult.objects.get(task_id=i.UpdateTaskId)
                    last_data[i.UpdateTaskId] = [i.UpdateName, update_logs_object.status,
                                            str(update_logs_object.date_done.astimezone(pytz.timezone("Asia/Shanghai"))),
                                                 i.UpdateUser]
                except TaskResult.DoesNotExist:
                    # updateLog表里面有这个task id 但是TaskResult不存在的，显示PROCESSING
                    last_data[i.UpdateTaskId] = [i.UpdateName, "PROCESSING", "waiting", "waiting"]
            return HttpResponse(json.dumps(last_data, ensure_ascii=False))
        if action == "detail_check":
            task_id = request.POST.get("task_id", "")
            detail_objects = TaskResult.objects.get(task_id=task_id)
            detail = detail_objects.result
            return HttpResponse(json.dumps({"message": detail}, ensure_ascii=False))
    return HttpResponse("没有输入！")


@csrf_exempt
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
def config_transfor(request):
    """
    转化普通的配置文件为新版的配置文件
    :param request:
    :return:
    """

    data = request.POST.get("data", "")
    host = {
        "hostname": "192.168.1.241",
        "username": "root",
        "password": "111111",
        "port": "22"

    }
    if data:
        escaped_data = data.replace("$", "\$")
        ssh = ssh_plugin.SSHConnect(host)
        # 写入数组的临时文件目录
        test_file_path = r"/html/config_node/scripts/test.php"
        clean_cache_cmd = """rm -rf /html/config_node/scripts/ini/test.php"""
        write_cmd = """ cd /html/config_node/scripts/ && echo -e "<?php\\n" > {} && \
         echo "{}" >> {} && \
         /usr/local/php7.1.14/bin/php7.1 \
         /html/config_node/scripts/arrtotext.php {} ./ini/""".format(test_file_path, escaped_data, test_file_path, test_file_path)
        read_cmd = """cat /html/config_node/scripts/ini/test.php"""
        clean_cache_result = ssh.run_command(clean_cache_cmd)
        write_result = ssh.run_command(write_cmd)
        read_result = ssh.run_command(read_cmd)
        ssh.close()
        return HttpResponse(read_result)
    return render(request, "config_transfor.html", locals())


@csrf_exempt
def wiki_public(request):
    """
    把wiki的文档和用户关联起来，用于推送
    有重复代码 注意优化
    :param request:
    :return:
    """
    wiki_database = {
        "host": "192.168.1.234",
        "user": "wiki",
        "password": "123456",
        "database": "mm_wiki"

    }
    conn = pymysql.connect(host=wiki_database.get("host"),
                           user=wiki_database.get("user"),
                           password=wiki_database.get("password"),
                           database=wiki_database.get("database"))
    cur = conn.cursor()
    cur.execute("""SELECT document_id, name FROM mw_document;""")
    all_document_name = cur.fetchall()
    cur.execute("""SELECT user_id, username FROM mw_user;""")
    all_users = cur.fetchall()
    if request.POST:
        action = request.POST.get("action", "")
        document_data = request.POST.get("document_data", "")
        user_data = request.POST.get("user_data", "")
        if action == "follow_document":
            if user_data != "all":
                flag_cmd = """SELECT * FROM mw_follow where object_id={} and user_id={};""".format(eval(document_data)[0],
                                                                                                   eval(user_data)[0])
                cur.execute(flag_cmd)
                check_exsited = cur.fetchall()
                if check_exsited:
                    return HttpResponse("已经关注过了，无需关注！")
                else:
                    add_cmd = """INSERT INTO mw_follow (user_id, object_id, create_time) VALUES ({}, {}, {});""".format(eval(user_data)[0],
                                                                                                                         eval(document_data)[0],
                                                                                                                         int(time.time()))
                    print(add_cmd)
                    cur.execute(add_cmd)
                    cur.execute("commit;")
                    return HttpResponse("已经关注成功！")
            else:
                check_user_cmd = """SELECT user_id FROM mw_user;"""
                cur.execute(check_user_cmd)
                user_ids = cur.fetchall()
                for i in user_ids:
                    flag_cmd = """SELECT * FROM mw_follow where object_id={} and user_id={};""".format(
                        eval(document_data)[0],
                        i[0])
                    cur.execute(flag_cmd)
                    check_exsited = cur.fetchall()
                    if check_exsited:
                        print("已经关注过了，无需关注！")
                        continue
                    else:


                        add_cmd = """INSERT INTO mw_follow (user_id, object_id, create_time) VALUES ({}, {}, {});""".format(
                            i[0],
                            eval(document_data)[0],
                            int(time.time()))
                        print(add_cmd)
                        cur.execute(add_cmd)
                        cur.execute("commit;")
                return HttpResponse("已经批量关注成功！")

    return render(request, "wiki_public.html", locals())


@csrf_exempt
def test1(request):
    if request.method == "POST":
        id = request.POST.get("id", "")
        return HttpResponse("come on...Post data!.. data is {}".format(id))
    if request.method == "DELETE":
        id = request.DELETE.get("id", "")
        return HttpResponse("Which one do u want to delete? {}".format(id))
    return HttpResponse("Fail you lost everything....")
