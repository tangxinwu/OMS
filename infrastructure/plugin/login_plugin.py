from redis import StrictRedis
from infrastructure.models import User
import time
import uuid


class LoginSession:
    """
    检测用户是否存在，匹配用户名和密码
    匹配成功写入redis, 设置过期时间默认600秒
    """
    def __init__(self, request, logged_username="", logged_password="", redis_host="127.0.0.1",
                 redis_port="6379", redis_db=0, expire=6000):
        """
        :param request 传入的http request
        :param logged_username: 传入的登录的用户名
        :param logged_password: 传入登录的用户名对应的密码
        :param redis_host:  redis服务的主机名
        :param redis_port:  redis的端口
        :param redis_db:    redis的db
        :param expire:      登录缓存过期时间 默认600秒
        """
        self._request = request
        self._logged_username = logged_username
        self._logged_password = logged_password
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._redis_db = redis_db
        self._expire = expire
        self._redis_conn = ""

    def _init_redis_conn(self):
        """
        初始化redis链接
        :return:
        """
        if not self._redis_conn:
            self._redis_conn = StrictRedis(host=self._redis_host, db=self._redis_db, port=self._redis_port)

    def _pre_check(self):
        """
        检测redis中是否有存在的缓存
        检测本地session中是否有cookie
        先从session中读出token--->根据token 在redis中找到对应的username -->判断这两个username是不是一样
        session 中存在的键值对是：{"token"：随机数}
        redis 中存在的键值对是: {获取到的token的随机数 : 对应的username}
        :return:存在并相同返回1
                不存在或不匹配返回0
        """
        local_session_check = self._request.session.get("token", "")
        redis_check = self._redis_conn.get(local_session_check)
        if all([redis_check, local_session_check]):
            return 1
        else:
            print("调试1")
            return 0

    def _verify_userinfo(self):
        """
        从数据库中校验登录的用户名和密码
        :return:成功匹配写入session["login_info"]返回1
                失败返回0
        """
        checked_user = User.objects.filter(login_name=self._logged_username, login_password=self._logged_password)
        if checked_user:
            self._request.session["login_info"] = {"name": self._logged_username,
                                                   "role": checked_user[0].role_type.RoleType}
            return 1
        else:
            return 0

    def _write_to_redis_and_session(self):
        """
        校验成功写入redis缓存和本地cookie
        :return:
        """
        # 写入redis
        token = str(uuid.uuid4())
        self._redis_conn.set(token, self._logged_username)
        self._redis_conn.expire(token, self._expire)
        # 写入session
        self._request.session["token"] = token

    def clean_cache(self):
        """
        清除所有的登录缓存
        :return:
        """
        if not self._redis_conn:
            self._init_redis_conn()
        if self._request.session.get("token", ""):
            self._redis_conn.delete(self._request.session.get("token", ""))
        # 删除session["token"]
        try:
            del self._request.session["token"]
        except KeyError:
            pass
        # 删除session["login_info"]
        try:
            del self._request.session["login_info"]
        except KeyError:
            pass

    def __call__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: 不同的返回代表不同的结果：
                2 --> 用户登录没有过期，无需登录
                1 --> 用户验证成功
                0 --> 用户名和密码错误
        """
        self._init_redis_conn()
        if self._pre_check():
            return 2
        # 非登录流程 只是校验是否登录流程 不再校验用户名和密码
        if any([self._logged_username, self._logged_password]):
            if self._verify_userinfo():
                self._write_to_redis_and_session()

                return 1
            else:

                return 0
