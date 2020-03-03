# import pyinotify
# import datetime
#
#
# class MyEvent(pyinotify.ProcessEvent):
#     def __init__(self):
#         self.log_file_path = r"/tmp/watchFile.log"
#         self._f = open(self.log_file_path, "a+")
#         super().__init__()
#
#     def process_IN_MODIFY(self, event):
#         print("{} 文件正在被修改中！".format(str(datetime.datetime.now())))
#
#     def process_IN_CREATE(self, event):
#         print("{} 文件被创建！".format(str(datetime.datetime.now())))
#
#     def process_IN_DELETE(self, event):
#         print("{} 文件被删除！".format(str(datetime.datetime.now())))
#
#
# def main(path):
#     wm = pyinotify.WatchManager()
#     wm.add_watch(path, pyinotify.ALL_EVENTS, rec=True)
#     ev = MyEvent()
#     notifier = pyinotify.Notifier(wm, ev)
#     print("开始监控")
#     notifier.loop()
#
#
# if __name__ == "__main__":
#     path = r"/home/tangxinwu/Desktop/test_modify"
#     main(path)
#
#
# import requests
#
# request_url = "http://192.168.1.246:3000/user/login"
#
# post_data = {
#     # "_csrf": "e6jpcDd1BOU1xXAF-v_bRveZwvQ6MTU2ODk2MTM1MTk1MTUyNTQ4MQ==",
#     "user_name": "zhangpengbo",
#     "password": "xiaohu123"
#
# }
# session = requests.session()
#
# next_url = "http://192.168.1.246:3000/zhangpengbo/web_app"
#
# get_header = {
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
#     # "Cookie": "lang=zh-CN; i_like_gogits=921323a619781a60; _csrf=e6jpcDd1BOU1xXAF-v_bRveZwvQ6MTU2ODk2MTM1MTk1MTUyNTQ4MQ%3D%3D"
# }
# index_page = session.get(request_url, headers=get_header)
#
# response = session.post(request_url, post_data, headers=get_header)
#
#
# response2 = session.get(next_url, headers=get_header)
#
# # response3 = requests.get()
# f = open("/home/tangxinwu/Desktop/web_app_interface.html", "w")
#
# f.write(response2.content.decode("utf8"))
#
# f.close()
###############################################################################

# file_path = """/home/tangxinwu/Downloads/xhdj_game_data.sql"""
#
# f = open(file_path)
#
# f1 = open("/home/tangxinwu/Downloads/xhdj_game_data.txt", "a")
# data = f.readlines()
#
#
# class Count:
#     def __init__(self, table_name):
#         self.table_name = table_name
#         self.count = 0
#
#
# for i in data:
#     if i.startswith("CREATE TABLE"):
#         table_name = i.split(" ")[2]
#         print(table_name, "table_name")
#
#         p = Count(table_name)
#
#         f1.write(table_name + "||")
#         continue
#     if "COMMENT" in i and "ENGINE=InnoDB" not in i:
#         p.count += 1
#         continue
#     if "int" in i:
#         p.count += 1
#         continue
#     if "datetime" in i:
#         p.count += 1
#         continue
#     if "ENGINE=InnoDB" in i:
#         try:
#             table_comment = i.split("COMMENT=")[1]
#         except IndexError:
#             table_comment = "表备注为空" + "\n"
#         f1.write(str(p.count) + "||")
#         f1.write(table_comment)
#
#         continue
#
#
# f.close()
# f1.close()
###################################################
#
# from openpyxl import Workbook
# from openpyxl import load_workbook
#
# wb = load_workbook("""/home/tangxinwu/Documents/(1).xlsx""")
#
# ws = wb.active
# wb.guess_types = True
# cols = []
#
# rows = []
# for col in ws.iter_cols():
#     cols.append(col)
#
# for row in ws.iter_rows():
#     rows.append(row)
#
# print(rows)
#
# print(len(rows))
#
# data = dict()
# for i in rows:
#     temp_name = i[2].value.replace(":", "/")
#     if "/" in temp_name:
#         temp_list = temp_name.split("/")
#         if not temp_list[0]:
#             controller_name = temp_list[1]
#         else:
#             controller_name = temp_list[1]

###################

# import JsonModel
#
# s1 = JsonModel.SeriesBar(name="test内容", data=[1,2,3])
#
# q = JsonModel.GenJSONBar(title="测试图表内容", tooltip=True, )

import random

# print(random.randint(0, 26))

# print(ord("t"))

# jsad#%#$%%#qjwidkqw



#########################
# import os
# import random
#
# pic_path = """/home/tangxinwu/Desktop/鬼刀"""
#
# pic_list = [i for i in os.listdir(pic_path) if i.endswith(".jpg")]
#
#
# print(pic_list)
# change_cmd = """gsettings set com.deepin.wrap.gnome.desktop.background picture-uri "{}" """.format(os.path.join(pic_path, pic_list[random.randint(0, len(pic_list) - 1)]))
#
# print(change_cmd)
#
# os.system(change_cmd)

#
# import difflib
#
# compare = difflib.HtmlDiff()
#
# f1 = open("/home/tangxinwu/Desktop/test1.txt")
#
# f2 = open("/home/tangxinwu/Desktop/test2.txt")
#
# report = open("/home/tangxinwu/Desktop/report.html", "w+")
#
# f1_text = f1.readlines()
#
# f2_text = f2.readlines()
#
# report.write(compare.make_file(f2_text, f1_text, context=True))
#
# f1.close()
# f2.close()
# report.close()
#
#
# class Compare:
#     """
#     比较两个文件不同，输出到html文件
#     """
#     def __init__(self, file1_path, file2_path, outpath="/tmp/report.html"):
#         self._file1_path = file1_path
#         self._file2_path = file2_path
#         self._outpath = outpath
#
#     def run(self):
#         c = difflib.HtmlDiff()
#         f1 = open(self._file1_path)
#         f2 = open(self._file2_path)
#         f1_text = f1.readlines()
#         f2_text = f2.readlines()
#         report = open(self._outpath, "w+")
#         report.write(c.make_file(f1_text, f2_text, c  ontext=True))
#         f1.close()
#         f2.close()
#         report.close()


# -*- coding: utf-8 -*-

from tkinter import *

root = Tk()

root.title = ("GKP计算器")
root.geometry("800x600")
Label(root, text="测试label").pack(side=LEFT)
frm = Frame(root)

# left


root.mainloop()

