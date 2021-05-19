from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
from email.header import Header
from itsdangerous.jws import TimedJSONWebSignatureSerializer as TJWSSerializer
from django.conf import settings
import BUAA.models as models
import BUAA.serializers as serializers
from BUAA.const import NOTIF

mail_host = "smtp.126.com"  # 设置SMTP服务器，如smtp.qq.com
mail_user = "reedsailing@126.com"  # 发送邮箱的用户名，如xxxxxx@qq.com
mail_pass = "SJHDAZYRQSGNXCTH"  # 发送邮箱的密码（注：QQ邮箱需要开启SMTP服务后在此填写授权码）
sender = mail_user  # 发件邮箱，如xxxxxx@qq.com

# Notification part
def get_notif_content(type_, **kwargs):
    act = kwargs['act_name'] if 'act_name' in kwargs else ''
    org = kwargs['org_name'] if 'org_name' in kwargs else ''

    content = ''
    if type_== NOTIF.ActContent:
        content = f"您参与的活动\'{act}\'内容发生了改变，请及时查看"
    elif type_ == NOTIF.ActCancel:
        content = f"您参与的活动\'{act}\'已被取消"
    elif type_ == NOTIF.RemovalFromAct:
        content = f"您已被管理员从活动\'{act}\'中移除"
    elif type_ == NOTIF.NewBoya:
        content = f"有新的博雅\'{act}\', 如有需要请及时报名"
    elif type_ == NOTIF.ActCommented:
        content = f"您管理的活动\'{act}\'被评论了"
    elif type_ == NOTIF.OrgApplyRes:
        content = f"您创建\'{org}\'组织的申请已经"
    elif type_ == NOTIF.BecomeOwner:
        content = f"您被转让成为\'{org}\'组织的负责人"
    elif type_ == NOTIF.RemovalFromAdmin:
        content = f"您被\'{org}\'组织的负责人移除了管理员身份"

    return content





def push_all_notif(user_id, ws):
    """revoke when user gets online"""
    unread_send_notifs = models.SentNotif.objects.filter(person=user_id, already_read=False)
    unread_notifs = list(map(lambda x: serializers.NotificationSerializer(x.notif).data ,unread_send_notifs))
    ws.send(str(unread_notifs))
    unread_send_notifs.update(already_read = True)

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
            #print("中文测试")
            smtpObj = SMTP()
            smtpObj.connect(self.mail_host, 25)  # 25 为 SMTP 端口号
            smtpObj.login(self.mail_user, self.mail_pass)
            smtpObj.sendmail(self.sender, receiver, str(message))
            # print("邮件发送成功")
        except SMTPException:
            print("error")
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

import traceback
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('default')
logger2 = logging.getLogger('django.server')

class ExceptionLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        import traceback
        #with open("/root/test.txt", "w") as f:
        #    f.write(traceback.format_exc())
        logger.error(traceback.format_exc())
        logger2.error(traceback.format_exc())

if __name__ == "__main__":
    a=MailSender()
    a.send_mail("asdaf","ASdasdasd", "847791804@qq.com")
