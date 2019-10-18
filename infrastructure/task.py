#! coding=utf8
from OMS import celery_app
from infrastructure.plugin import ssh_plugin, vcenter_connect
from infrastructure.models import Application, GoTask, GoTaskStatus,Server
from infrastructure.plugin.process_check import GoTaskCheck
import subprocess
import os
import datetime
import paramiko

# 版本更新 task
@celery_app.task
def version_update_task(application_id):
    selected_application = Application.objects.get(id=int(application_id.split("_")[0]))
    application_time_flag = application_id.split("_")[1]
    application_tags = application_id.split("_")[2]
    print("打印time flag", application_time_flag)
    # 运行本地拉取脚本
    # pull_cmd = "/usr/bin/sh {} {} {} {} {}".format(selected_application.ApplicationUpdateScriptPath,
    #                                          selected_application.ApplicationName,
    #                                           (lambda x: x if x else "master")(selected_application.ApplicationBranch),
    #                                           application_time_flag, application_tags)
    pull_cmd = "{} {} {} {} {}".format(selected_application.ApplicationUpdateScriptPath,
                                             selected_application.ApplicationName,
                                              (lambda x: x if x else "master")(selected_application.ApplicationBranch),
                                              application_time_flag, application_tags)
    print(pull_cmd)
    p = subprocess.Popen(pull_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout = p.stdout.read().decode("utf8")
    stderror = p.stderr.read().decode("utf8")
    # 传送脚本到remote服务器 ####
    host = {"hostname": selected_application.ApplicationServer.wan_ip, "username": "root",
            "password": selected_application.ApplicationServer.password, "port": 22}

    transport = ssh_plugin.SFTPConnect(host)

    transport.send_file(selected_application.ApplicationUpdateScriptPathAfter,
                        os.path.join("/tmp", os.path.basename(selected_application.ApplicationUpdateScriptPathAfter)))
    # 传送tar文件到remote服务器
    # transport.send_file("/root/workspace/{}/{}_{}.tar".format(selected_application.ApplicationName,
    #                                                        selected_application.ApplicationName,
    #                                                           application_time_flag),
    #                     "/tmp/{}_{}.tar".format(selected_application.ApplicationName, application_time_flag))
    transport.send_file("/tmp/workspace/{}/{}_{}.tar".format(selected_application.ApplicationName,
                                                              selected_application.ApplicationName,
                                                              application_time_flag),
                        "/tmp/{}_{}.tar".format(selected_application.ApplicationName, application_time_flag))
    transport.close()

    # 远程运行脚本 ##
    ssh = ssh_plugin.SSHConnect(host)
    cmd = "sh {} {} {}".format(
        os.path.join("/tmp", os.path.basename(selected_application.ApplicationUpdateScriptPathAfter)),
        selected_application.ApplicationPath,
        application_time_flag)
    print(cmd)
    result = ssh.run_command(cmd)
    return (lambda x, y: x if x else y)(stdout, stderror) + result


# 定时备份虚拟机task
@celery_app.task
def backup_vm(vm_ip):
    """
    按定期备份虚拟机为快照
    传入参数为虚拟机的ip地址
    :return:
    """

    select_vcenter = vcenter_connect.CreateSnapshot(SSL=False)
    select_vcenter.build_arg_parser()
    select_vcenter.add_argument(host=vm_ip,
                                name=str(vm_ip),
                                description="快照由后台自动创建于{}".format(str(datetime.datetime.now())),
                                memory=True,
                                quiesce=False)
    select_vcenter.handler()


# 检测gotask状态的task
@celery_app.task
def check_go_task_status():
    for Task in GoTask.objects.all():
        TaskServerIp = Task.TaskInServer.wan_ip
        TaskPath = Task.PathOfGoTask
        host = {
            "hostname": TaskServerIp,
            "username": "root",
            "password": Server.objects.get(wan_ip=TaskServerIp).password,
            "port": "22"
        }
        try:
            p = GoTaskCheck(host, TaskPath)
            TaskStatus = p.check_process_status()
        except paramiko.ssh_exception.SSHException:
            TaskStatus = "unreachable"
        except paramiko.ssh_exception.NoValidConnectionsError:
            TaskStatus = "unreachable"
        check_status_first = GoTaskStatus.objects.filter(GoTaskIP=TaskServerIp)
        if not check_status_first:
            GoTaskStatus.objects.create(GoTaskIP=TaskServerIp, GoTaskStatus=TaskStatus)
        else:
            if check_status_first[0].GoTaskStatus == TaskStatus:
                pass
            else:
                check_status_first.update(GoTaskStatus=TaskStatus)


@celery_app.task
def test_task():
    path = r"/tmp/test.log"
    import datetime
    with open(path, "a+") as f:
        f.write(str(datetime.datetime.now()) + "\n")


@celery_app.task
def backup_db(host, db_user, db_password, backup_db_name):
    """

    :param DB_PARAMS:传入的db参数格式如下
                    {
                        "host": "xxxx",
                        "db_user": "root",
                        "db_password": "123456",
                        "backup_db_name": []
                    }
    :return:
    """
    connect_host = {
            "hostname": host,
            "username": "root",
            "password": Server.objects.get(wan_ip=host).password,
            "port": 22
    }
    print("链接参数显示：", connect_host)
    ssh = ssh_plugin.SSHConnect(connect_host)
    sftp = ssh_plugin.SFTPConnect(connect_host)
    result_list = []
    for db_name in backup_db_name:
        result = ssh.run_command("""/usr/local/mysql5.6/bin/mysqldump -u{} -p{} {} > /tmp/{}""".format(db_user,
                                                            db_password,
                                                            db_name,
                                                            db_name))
        result_list.append(result)
    print(result_list)
    ssh.close()



