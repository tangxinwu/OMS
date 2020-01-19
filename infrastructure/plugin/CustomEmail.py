from email.utils import formataddr
import smtplib
from email.mime.text import MIMEText


class SendMailFail(Exception):
    def __str__(self):
        return "发送邮件失败"


class SendMail:
    """
    发送邮件的库
    """
    def __init__(self, sender="tangxinwu@tinytiger.cn", reciver="tangxinwu@tinytiger.cn", sender_password="MwzrPsiieUPFua9G"):
        """
        初始化发送邮件的库
        :param sender:  发送邮件的人
        :param reciver: 接受邮件的人
        :param sender_password: 发送邮件的人的邮箱密码
        """
        self._sender = sender
        self._reciver = reciver
        self._sender_password = sender_password

    def send_mail(self, title, mail_content):
        """
        发送邮件
        :param mail_content: 发送邮件的内容
        :return:
        """
        try:
            msg = MIMEText(mail_content, 'plain', 'utf-8')
            # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['From'] = formataddr(["内部邮件通知", self._sender])
            # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['To'] = formataddr(["内部通知人", self._reciver])
            # 邮件的主题
            msg['Subject'] = title

            # SMTP服务器，腾讯企业邮箱端口是465，腾讯邮箱支持SSL(不强制)， 不支持TLS
            # qq邮箱smtp服务器地址:smtp.qq.com,端口号：456
            # 163邮箱smtp服务器地址：smtp.163.com，端口号：25
            server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)
            # 登录服务器，括号中对应的是发件人邮箱账号、邮箱密码
            server.login(self._sender, self._sender_password)
            # 发送邮件，括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            server.sendmail(self._sender, [self._reciver, ], msg.as_string())
            # 关闭连接
            server.quit()
        except:
            raise SendMailFail
        else:
            return "发送邮件成功"


if __name__ == "__main__":
    p = SendMail()
    p.send_mail("新的审核通知!", "这个只是测试邮件!")
