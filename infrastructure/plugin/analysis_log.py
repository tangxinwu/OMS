#! coding=utf-8

# 分析日志 #

from abc import abstractmethod, ABC
import re


class Analysis(ABC):
    """日志分析抽象类"""

    def __init__(self, log_file):
        """
        初始化
        :param log_file: 传入log日志文件路径
        """
        self._log_file = log_file
        self._data = ""

    def _gen_data(self):
        with open(self._log_file, encoding="utf8") as f:
            self._data = [i.replace(r"\r", "").replace(r"\n", "") for i in f.readlines()]

    @abstractmethod
    def process(self):
        """
        处理日志的方法
        :return:
        """


class AnalysisNginx(Analysis):
    """
    分析nginx日志
    """
    def __init__(self, log_file):
        super().__init__(log_file)

    def process(self):
        self._gen_data()


class AnalysisSystem(Analysis):
    """分析系统日志"""
    def __init__(self, log_file):
        super().__init__(log_file)

    def process(self):
        pass


if __name__ == "__main__":
    pass
