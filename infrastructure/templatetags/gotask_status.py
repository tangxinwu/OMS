from django import template
from infrastructure.plugin.process_check import GoTaskCheck
from infrastructure.models import *
import paramiko

register = template.Library()


@register.filter
def gotask_status(value):
    selectd_objects = GoTaskStatus.objects.get(GoTaskIP=value)
    status = selectd_objects.GoTaskStatus
    return status
