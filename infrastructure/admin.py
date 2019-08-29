from django.contrib import admin
from infrastructure.models import *

# Register your models here.


class ServeAdmin(admin.ModelAdmin):
    list_display = ["server_name", "wan_ip", "lan_ip", "applications", "descriptions",]


admin.site.register(Server, ServeAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ["login_name", "xshell_path", "role_type"]


admin.site.register(User, UserAdmin)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["ApplicationName", "ApplicationServer", "ApplicationPath", "ApplicationUpdateScriptPath",
                    "ApplicationUpdateScriptPathAfter", "ApplicationBranch", "ApplicationLevel", "Description"]


admin.site.register(Application, ApplicationAdmin)


class ApplicationLogsAdmin(admin.ModelAdmin):
    list_display = ["ApplicationOnTheServer", "LogsOfApplication", "PathOfLogs", "Description", "LogsFileName"]


admin.site.register(ApplicationLogs, ApplicationLogsAdmin)


class RemoteServerServiceAdmin(admin.ModelAdmin):
    list_display = ["ServiceAtServer", "ServiceName", "ServicePort"]


admin.site.register(RemoteServerService, RemoteServerServiceAdmin)


class UpdateLogAdmin(admin.ModelAdmin):
    list_display = ["UpdateName", "UpdateTaskId", "UpdateUser", "UpdateTime"]


admin.site.register(UpdateLogs, UpdateLogAdmin)


class GoTaskAdmin(admin.ModelAdmin):
    lis_display = ["TaskInServer", "PathOfGoTask"]


admin.site.register(GoTask, GoTaskAdmin)


class RoleTypeAdmin(admin.ModelAdmin):
    list_display = ["RoleType"]


admin.site.register(RoleType, RoleTypeAdmin)


class ApplicationLevelAdmin(admin.ModelAdmin):
    list_display = ["application_level"]


admin.site.register(ApplicationLevel, ApplicationLevelAdmin)


class GoTaskStatusAdmin(admin.ModelAdmin):
    list_display = ["GoTaskIP", "GoTaskStatus"]


admin.site.register(GoTaskStatus, GoTaskStatusAdmin)


class SelfInvokeAdmin(admin.ModelAdmin):
    list_display = ["InVokedApplicationId", "InVokedUser", "InvokedToken", "InVokedTime", "AuditingUser", "isdeal"]


admin.site.register(SelfInvoke, SelfInvokeAdmin)
