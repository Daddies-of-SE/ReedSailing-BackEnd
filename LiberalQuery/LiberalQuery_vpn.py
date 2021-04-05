#!/usr/bin/python
#coding=utf-8

MAXTRY = 10

from selenium import webdriver
option = webdriver.ChromeOptions()
#option.add_argument('headless') # 设置option
prefs = {
    'profile.managed_default_content_settings.images': 2,  # 不加载图片
    'permissions.default.stylesheet': 2  # 不渲染CSS
}
option.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(options=option)
driver.minimize_window()

import json
from email.header import Header
from email.mime.text import MIMEText
import smtplib
from html.parser import HTMLParser
from selenium.webdriver.common.action_chains import ActionChains
import traceback
import time
import os
import requests
import re



print('------------Unified Account------------')
if os.path.exists('unifiedaccount.str'):
    print('Saved unified account dectected, program will load your account information from files.')
    print('If you want to update your unified account information, just delete file \'unifiedaccount.str\' and reopen this program.')
    #option=input('Do you want to use saved account information?[y/n]')
    with open('unifiedaccount.str', 'r') as f:
        list = f.read().split('\n')
        user_name = list[0]
        pwd = list[1]
        #print(user_name)
        #print(pwd)
else:
    user_name = input('Please input your username of unified account:\n')
    pwd = input('Please input your password of unified account:\n')
    print('Do you want to save them so that next time you will not need to input these information again?')
    option = input('Please input y for yes or n for no:\n')
    if option.lower() == 'y':
        with open('unifiedaccount.str', 'w') as f:
            f.write(user_name+'\n')
            f.write(pwd+'\n')
        print('Information of your unified account saved. If you don\'t want to keep them anymore, just delete file \'unifiedaccount.str\'.')

print('--------Mail Server Setting---------')
if os.path.exists('mailserv.str'):
    print('Saved mail settings detected and will be loaded.')
    print('If you want to update your mail settings, delete file \'mailserv.str\' and reopen this program')
    with open('mailserv.str', 'r') as f:
        list = f.read().split('\n')
        mail_host = list[0]
        mail_user = list[1]
        mail_pass = list[2]
        sender = list[3]
        receivers = list[4]
else:
    print('Please set your mail settings, this section includes three part.')
    print('Part 1. Set email account you want use for sending mails.')
    mail_host = input(
        'Please input SMTP server you use, e.g. \'smtp.qq.com\':\n')
    mail_user = input(
        'Please input username for logging in your email account:\n')
    mail_pass = input('Please input password:\n')
    print('Part 2. Set sender\'s mail address, normally sender is the same as username:')
    sender = input()
    print('Part 3. Set receiver\'s mail address, to which you want to send mail:')
    receivers = input()
    print('Do you want to save them so that next time you will not need to input these information again?')
    option = input('Please input y for yes or n for no:\n')
    if option.lower() == 'y':
        with open('mailserv.str', 'w') as f:
            f.write(mail_host+'\n')
            f.write(mail_user+'\n')
            f.write(mail_pass+'\n')
            f.write(sender+'\n')
            f.write(receivers+'\n')
        print('Information of your unified account saved. If you don\'t want to keep them anymore, just delete file \'mailserv.str\'.')


def send_mail(title, content,receivers):
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header(sender, 'utf-8')  # 发件人
    message['To'] = Header(receivers, 'utf-8')  # 收件人
    subject = title  # 主题
    message['Subject'] = Header(subject, 'utf-8')
    print('Prepare success')
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
        print('Connect success')
        smtpObj.login(mail_user, mail_pass)
        print('Login success')
        smtpObj.sendmail(sender, receivers, str(message))
        print("邮件发送成功")
    except smtplib.SMTPException:
        print(traceback.format_exc())
        print("ERROR：无法发送邮件")


def tuplefind(l, s):
    for i in range(len(l)):
        if l[i][0] == s:
            return i
    return -1


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.intable = False
        self.inbody = False
        self.inrow = False
        self.infolist = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            id1 = tuplefind(attrs, 'class')
            if id1 != -1 and attrs[id1][1] == 'table table-bordered list-table':
                self.intable = True
        if self.intable and tag == 'tbody':
            self.inbody = True
        if self.intable and self.inbody and tag == 'tr':
            self.inrow = True
            self.infolist = []

    def handle_endtag(self, tag):
        if tag == 'table':
            self.intable = False
        if tag == 'tbody':
            self.inbody = False
        if tag == 'tr':
            self.inrow = False
            if self.intable and self.inbody:
                global courseinfos
                courseinfos.append(self.infolist.copy())

    def handle_data(self, data):
        data = data.strip()
        if self.intable and self.inbody and self.inrow and data:
            self.infolist.append(data)
            #print(data)
        #print("Encountered some data  :", data)

def parseinfo(info):
    htmlstr = '<tr>\n'+'\t<td>%s</td>\n' % info[0]+'\t<td>%s%s</td>\n' % (
        info[1], info[2])+'\t<td>%s<br>%s<br>%s</td>\n' % (info[3], info[4], info[5])+'\t<td>%s<br>%s</td>\n' % (info[6], info[7])+'\t<td>%s<br>%s<br>%s</td>\n' % (info[8], info[9], info[10])+'\t<td>%s<br>%s</td>\n' % (info[11], info[12])+'\t<td>%s%s%s</td>\n' % (info[14], info[15], info[16])+'</tr>\n'
    return htmlstr


def parseprevinfo(info):
    htmlstr = '<tr>\n'+'\t<td><i>%s</i></td>\n' % info[0]+'\t<td>%s%s</td>\n' % (
        info[1], info[2])+'\t<td>%s<br>%s<br>%s</td>\n' % (info[3], info[4], info[5])+'\t<td>%s<br>%s</td>\n' % (info[6], info[7]) +\
        '\t<td>%s<br>%s<br>%s</td>\n' % (info[8], info[9], info[10])+'\t<td>%s<br>%s<br>%s</td>\n' % (
        info[13], info[14], info[15])+'\t<td>%s</td>\n' % (info[12])+'</tr>\n'
    return htmlstr

courseinfos = []

existedcourses = []
if os.path.exists('courses.txt'):
    with open('courses.txt', 'r') as f:
        coursenames = f.readlines()
        for name in coursenames:
            existedcourses.append(name[:-1])
existedprevcourses = []
if os.path.exists('prevcourses.txt'):
    with open('prevcourses.txt', 'r') as f:
        coursenames = f.readlines()
        for name in coursenames:
            existedprevcourses.append(name[:-1])

url_login = r"https://bykc.e2.buaa.edu.cn"
            #r"https://sso.buaa.edu.cn/login?TARGET=http%3A%2F%2Fbykc.buaa.edu.cn%2Fsscv%2FcasLogin"

errcnt = 0
while True:
    try:
        #driver.refresh()
        driver.get(url_login)

        time.sleep(3)

        try:
            # 输用户名和密码
            user_name_input = driver.find_element_by_id('user_login')
            user_name_input.send_keys(user_name)
            user_pwd_input = driver.find_element_by_id('user_password')
            user_pwd_input.send_keys(pwd)

            # 然后点击登录按钮
            login=driver.find_element_by_xpath("//input[@class='btn']")
            login.click()
            time.sleep(7)
        except:
            print(traceback.format_exc())
        
        try:
            # 输用户名和密码
            iframe = driver.find_element_by_xpath('//*[@id="loginIframe"]')
            driver.switch_to.frame(iframe)
            user_name_input = driver.find_element_by_id('unPassword')
            user_name_input.send_keys(user_name)
            user_pwd_input = driver.find_element_by_id('pwPassword')
            user_pwd_input.send_keys(pwd)

            # 然后点击登录按钮
            driver.execute_script('loginPassword()')
            time.sleep(5)
        except:
            print(traceback.format_exc())

        mycourse = driver.find_element_by_xpath("//ul[@class='nav']/li[3]")
        mycourse.click()
        time.sleep(1)
        courseselect = driver.find_element_by_xpath(
            "//ul[@class='nav-sub']/li[2]")
        courseselect.click()
        time.sleep(3)

        webtext=driver.page_source.encode("utf8", "ignore").decode("utf8")

        coursepreview = driver.find_element_by_xpath(
            "//ul[@class='nav-sub']/li[1]")
        coursepreview.click()
        time.sleep(3)
        prevwebtext = driver.page_source.encode(
            "utf8", "ignore").decode("utf8")

        driver.quit()
        break
    except:
        print(traceback.format_exc())
        errcnt += 1
        time.sleep(30)
        if errcnt >= MAXTRY:
            send_mail('Something wrong with liberal query program',
                    traceback.format_exc(),'brooks_sxj@foxmail.com')
            driver.quit()
            os._exit(0)

Parser = MyHTMLParser()
Parser.feed(webtext)

#print(courseinfos)
coursedict = []
newcoursename = []
newprevcoursename = []
declaration = '免责声明：本服务可能有缺陷，包括但不限于<strong>提醒不及时、课程信息错误</strong>等。作者不对本服务的缺陷负责，因使用本服务带来的任何损失（如错过课程信息、未选上课等）由使用者自行承担，使用此服务即视为接受此条款。<br>'
attention = '注：<br>1.为了减少无用的打扰，如果相比上次查询没有新增的课程，则不会发送邮件。因此，如果当日未收到邮件，<strong>大概率</strong>是因为没有新增的课程，也有小概率是因为本服务或博雅选课系统出现故障。<br>'+\
    '2.作者为2018级高工同学，邮件中的课程仅为作者有权限看到的课程。对于其他学院、其他年级的同学，可能出现<strong>自己能看到的课邮件中没有显示、邮件中显示的课看不到</strong>等情况<br>'+\
    '3.遇到bug或者有建议或者想要贡献代码欢迎联系作者，邮箱brooks_sxj@foxmail.com。<br>'
content=declaration+attention+'查询时间：%s<br>\n查询到新增以下博雅课程（含开放选课的和预告的）：<br>\n' % time.asctime(
    time.localtime(time.time()))+'<table border=1>\n<tr>\n\t<th>课程名</th>\n\t<th>课程类型</th>\n' +\
    '\t<th>基本信息</th>\n\t<th>课程时间</th>\n\t<th>开放群体</th>\n\t<th>选课时间</th>\n\t<th>课程人数</th>\n</tr>'

for info in courseinfos:
    if info[0] in existedcourses:
        continue
    newcoursename.append(info[0])
    content = content+parseinfo(info)
with open('courses.txt', 'w') as f:
    for info in courseinfos:
        f.write(info[0]+'\n')

courseinfos=[]
Parser.feed(prevwebtext)
for info in courseinfos:
    if info[0] in existedprevcourses:
        continue
    newprevcoursename.append(info[0])
    content = content+parseprevinfo(info)
with open('prevcourses.txt', 'w') as f:
    for info in courseinfos:
        f.write(info[0]+'\n')

content += '</table>'
#print(content)
#with open('mail.html', 'w') as f:
#    f.write(content)

'''with open('courses.txt', 'a') as f:
    for name in newcoursename:
        f.write(name+'\n')
with open('prevcourses.txt', 'a') as f:
    for name in newprevcoursename:
        f.write(name+'\n')'''
if newcoursename or newprevcoursename:
    send_mail('%s新增的博雅课程' % time.strftime("%m-%d %H:%M:%S",
                                           time.localtime()), content, receivers)
#print(webtext)
