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
# import requests
#
# request_url = "http://192.168.1.246:3000/user/login"
#
# post_data = {
#     "_csrf": "e6jpcDd1BOU1xXAF-v_bRveZwvQ6MTU2ODk2MTM1MTk1MTUyNTQ4MQ==",
#     "user_name": "zhangpengbo",
#     "password": "xiaohu123"
#
# }
#
#
# next_url = "http://192.168.1.246:3000/zhangpengbo/web_app"
#
# get_header = {
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
#     "Cookie": "lang=zh-CN; i_like_gogits=921323a619781a60; _csrf=e6jpcDd1BOU1xXAF-v_bRveZwvQ6MTU2ODk2MTM1MTk1MTUyNTQ4MQ%3D%3D"
# }
# index_page = requests.get(request_url, headers=get_header)
#
# response = requests.post(request_url, post_data, headers=get_header)
#
#
# response2 = requests.get(next_url, headers=get_header, cookies=response.cookies)
#
# # response3 = requests.get()
# f = open("/home/tangxinwu/Desktop/web_app_interface.html", "w")
#
# f.write(response2.content.decode("utf8"))
#
# f.close()


file_path = """/home/tangxinwu/Downloads/xhdj_game_data.sql"""

f = open(file_path)

f1 = open("/home/tangxinwu/Downloads/xhdj_game_data.txt", "a")
data = f.readlines()


class Count:
    def __init__(self, table_name):
        self.table_name = table_name
        self.count = 0


for i in data:
    if i.startswith("CREATE TABLE"):
        table_name = i.split(" ")[2]
        print(table_name, "table_name")

        p = Count(table_name)

        f1.write(table_name + "||")
        continue
    if "COMMENT" in i and "ENGINE=InnoDB" not in i:
        p.count += 1
        continue
    if "int" in i:
        p.count += 1
        continue
    if "datetime" in i:
        p.count += 1
        continue
    if "ENGINE=InnoDB" in i:
        try:
            table_comment = i.split("COMMENT=")[1]
        except IndexError:
            table_comment = "表备注为空" + "\n"
        f1.write(str(p.count) + "||")
        f1.write(table_comment)

        continue


f.close()
f1.close()
