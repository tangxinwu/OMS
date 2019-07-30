#! coding=utf-8
import datetime

"""
只能用于抓取
"""

# 返回到现在为止多少分钟内的日志,注意单位是分钟
time_to_return = 60*24

month_map = {
    "Jan":  "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "July": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}

# 错误的flag 标记
error_flag = ("err", "ERR", "error", "ERROR")


class GenLog:
    def __init__(self, log_path):
        self._log_path = log_path
        self._modified_time = ""
        self._ended_time = ""

    def modify_time(self):
        """
        修正开始时间和结束时间
        :return:
        """
        time_now = datetime.datetime.now()
        self._modified_time = time_now - datetime.timedelta(minutes=time_to_return)
        self._ended_time = time_now
        print("输出日志从{}到{}的错误日志".format(self._modified_time, self._ended_time))

    def _tranfor_date(self, readed_time):
        """
        把datetime模式的日期 转成字符串形式（比如Nov 19 14:41:40）
        方便去日志里面找
        :return:
        """
        if not self._ended_time or not self._modified_time:
            self.modify_time()
        tranfored_year = self._modified_time.year
        tranfored_month = int(month_map.get(readed_time.split()[0]))
        transfored_day = int(readed_time.split()[1])
        transfored_hour = int(readed_time.split()[2].split(":")[0])
        transfored_minute = int(readed_time.split()[2].split(":")[1])
        transfored_second = int(readed_time.split()[2].split(":")[2])
        transfored_time = datetime.datetime(year=tranfored_year, month=tranfored_month, day=transfored_day,
                                            hour=transfored_hour, minute=transfored_minute, second=transfored_second)
        return transfored_time

    def read_from_log(self):
        if not self._ended_time or not self._modified_time:
            self.modify_time()
        with open(self._log_path, encoding="utf8") as f:
            data = f.readlines()
        for line in data:
            date = " ".join(line.split(" ")[:3])
            text = " ".join(line.split(" ")[3:])
            tmp_date = self._tranfor_date(date)
            if self._modified_time < tmp_date < self._ended_time:
                for errors in error_flag:
                    if errors in text:
                        print(line)
                        break


if __name__ == "__main__":
    p = GenLog(r"C:\Users\tang\Desktop\1118.log")
    p.read_from_log()
