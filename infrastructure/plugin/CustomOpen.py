"""
自定义的open， 用于不同之间的编码
"""

# 支持的编码类型
Codings = {"utf8", "gbk"}

# 文件操作符类型
fs_oprate = {"w", "r"}


class OprationError(Exception):
    def __str__(self):
        return "文件操作符类型不正确！，仅支持{}".format("和".join(fs_oprate))


class CustomOpen:
    """
    重写open
    """
    def __init__(self, file, rwmode=""):
        self.rwmode = rwmode
        self.file = file
        self._f = ""
        self.data = ""
        self.__initread()

    def __initread(self):
        if not self.rwmode:
            for code in Codings:
                try:
                    self._f = open(self.file, encoding=code)
                    self.data = self._f.read()
                    break
                except UnicodeDecodeError:
                    continue
        else:
            if self.rwmode == "r":
                for code in Codings:
                    try:
                        self._f = open(self.file, self.rwmode, encoding=code)
                        self.data = self._f.read()
                        break
                    except UnicodeDecodeError:
                        continue
            if self.rwmode == "w":
                for code in Codings:
                    try:
                        self._f = open(self.file, self.rwmode, encoding=code)
                        break
                    except UnicodeDecodeError:
                        continue

    def read(self):
        return self.data

    def write(self, content):
        self._f.write(content)

    def close(self):
        self._f.close()

    def __setattr__(self, key, value):
        if key == "rwmode":
            if value not in {"r", "w", ""}:
                raise OprationError
        super().__setattr__(key, value)


if __name__ == "__main__":
    f = CustomOpen(r"/home/tangxinwu/Desktop/workspace/Android/gradle.properties")
    print(f.read())
