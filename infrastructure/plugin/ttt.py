import pyinotify
import datetime


class MyEvent(pyinotify.ProcessEvent):
    def __init__(self):
        self.log_file_path = r"/tmp/watchFile.log"
        self._f = open(self.log_file_path, "a+")
        super().__init__()

    def process_IN_MODIFY(self, event):
        print("{} 文件正在被修改中！".format(str(datetime.datetime.now())))

    def process_IN_CREATE(self, event):
        print("{} 文件被创建！".format(str(datetime.datetime.now())))

    def process_IN_DELETE(self, event):
        print("{} 文件被删除！".format(str(datetime.datetime.now())))


def main(path):
    wm = pyinotify.WatchManager()
    wm.add_watch(path, pyinotify.ALL_EVENTS, rec=True)
    ev = MyEvent()
    notifier = pyinotify.Notifier(wm, ev)
    print("开始监控")
    notifier.loop()


if __name__ == "__main__":
    path = r"/home/tangxinwu/Desktop/test_modify"
    main(path)
