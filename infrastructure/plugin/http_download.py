#! coding=utf-8
"""
下载http的文件

"""

from django.shortcuts import HttpResponse


class DownloadFile:
    """
    下载文件，返回浏览器下载
    """
    def __init__(self, local_file):
        """
        构造函数
        :param local_file: 本地文件
        """
        self._local_file = local_file

