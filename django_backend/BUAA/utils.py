from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
from email.header import Header
from itsdangerous.jws import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings

mail_host = "smtp.126.com"  # 设置SMTP服务器，如smtp.qq.com
mail_user = "reedsailing@126.com"  # 发送邮箱的用户名，如xxxxxx@qq.com
mail_pass = "SJHDAZYRQSGNXCTH"  # 发送邮箱的密码（注：QQ邮箱需要开启SMTP服务后在此填写授权码）
sender = mail_user  # 发件邮箱，如xxxxxx@qq.com


class MailSender:
    def __init__(self):
        self.mail_host = mail_host  # 设置SMTP服务器，如smtp.qq.com
        self.mail_user = mail_user  # 发送邮箱的用户名，如xxxxxx@qq.com
        self.mail_pass = mail_pass  # 发送邮箱的密码（注：QQ邮箱需要开启SMTP服务后在此填写授权码）
        self.sender = mail_user  # 发件邮箱，如xxxxxx@qq.com

    def send_mail(self, title, content, receiver=None):
        if receiver is None:
            receiver = self.mail_user
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = self.sender  # 发件人
        message['To'] = receiver  # 收件人
        subject = title  # 主题
        message['Subject'] = Header(subject, 'utf-8')
        try:
            smtpObj = SMTP()
            smtpObj.connect(self.mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(self.sender, receiver, str(message))
            # print("邮件发送成功")
        except SMTPException:
            # print("ERROR：无法发送邮件")


# 1, 加密openid
def encode_openid(openid, ex):
    # 1, 创建加密对象
    serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=ex)

    # 2, 加密数据
    token = serializer.dumps({"openid": openid})

    # 3, 返回加密结果
    return token.decode()


# 2, 解密openid
def decode_openid(token, ex):
    # 1, 创建加密对象
    serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=ex)

    # 2, 加密数据
    try:
        openid = serializer.loads(token).get("openid")
    except Exception as e:
        return None

    # 3, 返回加密结果
    return openid

if __name__ == "__main__":
    a=MailSender()
    a.send_mail("asdaf","ASdasdasd", "847791804@qq.com")
