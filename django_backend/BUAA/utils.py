from smtplib import SMTP, SMTPException
from email.mime.text import MIMEText
from email.header import Header

# FILL THIS
mail_host="smtp.qq.com"  #设置SMTP服务器，如smtp.qq.com
mail_user="847791804@qq.com"    #发送邮箱的用户名，如xxxxxx@qq.com
mail_pass= ""  #发送邮箱的密码（注：QQ邮箱需要开启SMTP服务后在此填写授权码）
sender = '847791804@qq.com' #发件邮箱，如xxxxxx@qq.com


class MailSender:
        def __init__(self):
                self.mail_host = mail_host  #设置SMTP服务器，如smtp.qq.com
                self.mail_user = mail_user  #发送邮箱的用户名，如xxxxxx@qq.com
                self.mail_pass = mail_pass  #发送邮箱的密码（注：QQ邮箱需要开启SMTP服务后在此填写授权码）
                self.sender = mail_user  #发件邮箱，如xxxxxx@qq.com
        
        def send_mail(self, title, content, receiver=None):
                if receiver is None:
                        receiver = self.mail_user
                message = MIMEText(content, 'plain', 'utf-8')
                message['From'] = Header(self.sender, 'utf-8')  #发件人
                message['To'] = Header(receiver, 'utf-8')  #收件人
                subject = title  #主题
                message['Subject'] = Header(subject, 'utf-8')
                try:
                        smtpObj = SMTP()
                        smtpObj.connect(self.mail_host, 25)  # 25 为 SMTP 端口号
                        smtpObj.login(self.mail_user, self.mail_pass)
                        smtpObj.sendmail(self.sender, receiver, str(message))
                        print("邮件发送成功")
                except SMTPException:
                        print("ERROR：无法发送邮件")