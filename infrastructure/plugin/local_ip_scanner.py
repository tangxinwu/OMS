#! coding=utf8
import os
import threading
import time


def print_time(n):
    for i in range(n):
        print(time.localtime())
        time.sleep(n)


# class IpScanner(threading.Thread):
#     """
#     IP扫描
#     """
#     def __init__(self, name):
#         """
#         ip初始化
#         """
#         threading.Thread.__init__(self)
#         self.name = name
#
#     def run(self):
#         """
#         重写run方法
#         :return:
#         """
#         print("开始线程:{}".format(self.name))
#
