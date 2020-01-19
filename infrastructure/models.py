from django.db import models

# Create your models here.
# update 2019-03-05
# 更新权限控制


class RoleType(models.Model):
    """
    权限控制角色类型
    """
    RoleType = models.CharField("权限角色", max_length=50, default="develop")

    class Meta:
        ordering = ["RoleType"]
        verbose_name_plural = "权限角色"

    def __str__(self):
        return self.RoleType


class ApplicationLevel(models.Model):
    """
    应用的级别，（生产还是测试）
    """
    application_level = models.CharField("应用的级别（生产还是测试）", max_length=50, default="测试")

    class Meta:
        ordering = ["application_level"]
        verbose_name_plural = "应用级别"

    def __str__(self):
        return self.application_level


class ServerType(models.Model):
    """
        服务器的类型，本地虚拟机还是物理机还是阿里云服务器
    """
    ServerTypeName = models.CharField("服务器的类型名", max_length=50)

    class Meta:
        ordering = ["ServerTypeName"]
        verbose_name_plural = "服务器类型名"

    def __str__(self):
        return self.ServerTypeName


class Server(models.Model):
    """
    标识服务器的名字和功能
    """
    server_name = models.CharField("服务器名字", max_length=50)
    server_type = models.ForeignKey(ServerType, "服务器的类型", default=1)
    wan_ip = models.GenericIPAddressField("外网ip")
    lan_ip = models.GenericIPAddressField("内网ip")
    applications = models.CharField("应用", max_length=500, blank=True,null=True)
    descriptions = models.CharField("描述", max_length=500, blank=True, null=True)
    password = models.CharField("登陆密码", max_length=50, blank=True, null=True)
    aliyun_server_expire = models.DateTimeField("阿里云服务器过期时间（如果为空就不是阿里云服务器）", blank=True, null=True)
    is_db_server = models.BooleanField("是否为数据库服务器", default=False)

    class Meta:
        ordering = ["server_name"]
        verbose_name_plural = "所有服务器"

    def __str__(self):
        return self.server_name


class User(models.Model):
    """
    注册的用户
    """
    login_name = models.CharField("登陆的名字", max_length=50)
    xshell_path = models.CharField("xshell路径", max_length=200, blank=True, null=True)
    login_password = models.CharField("登陆的密码", max_length=100)
    role_type = models.ForeignKey(RoleType, verbose_name="角色类型", default=1, on_delete=models.CASCADE)
    user_email = models.EmailField("电子邮件", max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["login_name"]
        verbose_name_plural = "所有注册能登陆的用户"

    def __str__(self):
        return self.login_name


class Application(models.Model):
    """
    应用分布
    """
    ApplicationName = models.CharField("应用名字(只允许英文)", max_length=100)
    ApplicationServer = models.ForeignKey(Server, on_delete=models.CASCADE)
    ApplicationPath = models.CharField("应用在服务器上的路径", max_length=200)
    ApplicationUpdateScriptPath = models.CharField("运行devops服务器上的拉取仓库的脚本位置", max_length=200)
    ApplicationUpdateScriptPathAfter = models.CharField("复制到远程服务器运行脚本的位置", max_length=200, blank=True,
                                                        null=True)
    ApplicationBranch = models.CharField("拉取的仓库的分支", default="", blank=True, null=True, max_length=50)
    ApplicationLevel = models.ForeignKey(ApplicationLevel, default=1, verbose_name="应用的级别", on_delete=models.CASCADE)
    Description = models.CharField("描述", max_length=200, blank=True, null=True)

    class Meta:
        ordering = ["ApplicationName"]
        verbose_name_plural = "所有应用"

    def __str__(self):
        return self.ApplicationName


class ApplicationLogs(models.Model):
    """
    应用的日志
    """
    ApplicationOnTheServer = models.ForeignKey(Server, on_delete=models.CASCADE)
    LogsOfApplication = models.CharField("什么应用的日志", max_length=50)
    PathOfLogs = models.CharField("日志的路径", max_length=150)
    LogsFileName = models.CharField("日志文件名字（支持模糊搜索）", max_length=100, blank=True, null=True)
    Description = models.CharField("描述", max_length=300, blank=True, null=True)

    class Meta:
        ordering = ["ApplicationOnTheServer"]
        verbose_name_plural = "所有应用的日志"

    def __str__(self):
        return self.LogsOfApplication + "在 " + self.ApplicationOnTheServer.server_name + "的日志"


class RemoteServerService(models.Model):
    """
    记录远程服务器服务信息
    默认保存服务的脚本放在OMS(192.168.1.240上)
    """
    ServiceAtServer = models.ForeignKey(Server, "服务在哪台服务器上")
    ServiceName = models.CharField("远程服务的名字", max_length=100)
    ServicePort = models.CharField("该服务启动的端口", max_length=20)

    class Meta:
        ordering = ["ServiceName"]
        verbose_name_plural = "所有远程服务器上的服务"

    def __str__(self):
        return "服务" + self.ServiceName + " 在" + self.ServiceAtServer.server_name + ",使用端口" + self.ServicePort


class UpdateLogs(models.Model):
    """
    更新的日志
    """
    UpdateName = models.CharField("更新的中文名字", max_length=200)
    UpdateServer = models.CharField("更新的服务器", max_length=100, blank=True, null=True)
    UpdateTaskId = models.CharField("更新的taskID", max_length=200)
    UpdateTime = models.DateTimeField("更新task的时间", auto_now=True, blank=True, null=True)
    UpdateUser = models.CharField("更新人", max_length=100, blank=True, null=True)
    UpdateTags = models.CharField("更新的tags", max_length=100, blank=True, null=True)
    UpdateBranch = models.CharField("更新的分支", max_length=50, blank=True, null=True)
    UpdateDescription = models.TextField("本次更新的内容", max_length=500, blank=True, null=True)

    class Meta:
        ordering = ['UpdateName']
        verbose_name_plural = "更新日志"

    def __str__(self):
        return self.UpdateTaskId


class GoTask(models.Model):
    """
    Gotask 配置表
    """
    TaskInServer = models.ForeignKey(Server, "go-task所在的服务器")
    PathOfGoTask = models.CharField("go-task的路径", max_length=200)

    class Meta:
        ordering = ["TaskInServer"]
        verbose_name_plural = "GOtask配置表"

    def __str__(self):
        return "go task 任务在" + self.TaskInServer.server_name


class GoTaskStatus(models.Model):
    """
    更新gotask的状态保存到这里
    """
    GoTaskIP = models.GenericIPAddressField("gotask所在的ip地址")
    GoTaskStatus = models.CharField("Gotask状态", max_length=20)

    class Meta:
        ordering = ["GoTaskIP"]
        verbose_name_plural = "GOtask状态"

    def __str__(self):
        return self.GoTaskIP


class SelfInvoke(models.Model):
    """
    自助申请流程models
    isdeal 字段标明这个申请是否被处理完成! 0 未处理 1 已经处理
    """
    isdeal_choice = (
        (0, "未处理"),
        (1, "已经通过"),
        (2, "已经拒绝")
    )
    InVokedApplicationId = models.ForeignKey(Application, on_delete=models.CASCADE)
    InVokedUser = models.CharField("自助申请流程的人", max_length=100)
    InvokedToken = models.CharField("自助申请的流程的token", max_length=200)
    InVokedTime = models.DateTimeField("申请的时间", auto_now_add=True)
    AuditingUser = models.ForeignKey(User, on_delete=models.CASCADE)
    isdeal = models.IntegerField("是否", choices=isdeal_choice, default=0, blank=True, null=True)

    class Meta:
        ordering = ["InVokedTime"]
        verbose_name_plural = "自助申请的流程"

    def __str__(self):
        return self.InVokedUser + "在{}申请了流程".format(str(self.InVokedTime))


