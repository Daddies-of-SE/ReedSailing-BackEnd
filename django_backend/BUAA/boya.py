#!/usr/bin/python
#coding=utf-8

MAXTRY = 10


import json
from email.header import Header
from email.mime.text import MIMEText
import smtplib
from html.parser import HTMLParser
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import traceback
import time
import os
import requests
import re


user_name = "wzk1015"
pwd = "" ###TODO: fill

if pwd == "" or mail_pass == "":
    print("please fill pwd and mail_pass in the .py file")
    exit(-1)

def _sleep(n_sec):
    _debug("sleep for", n_sec, "seconds")
    time.sleep(n_sec)

def _debug(*args, **kwargs):
    pass
    # comment the line below to disable debugging
    print(*args, **kwargs)


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
    htmlstr = '<tr>\n'+'\t<td>%s</td>\n' % info[0]+'\t<td>%s%s</td>\n' % (
        info[1], info[2])+'\t<td>%s<br>%s<br>%s</td>\n' % (info[3], info[4], info[5])+'\t<td>%s<br>%s</td>\n' % (info[6], info[7]) +\
        '\t<td>%s<br>%s<br>%s</td>\n' % (info[8], info[9], info[10])+'\t<td>%s<br>%s<br>%s</td>\n' % (
        info[13], info[14], info[15])+'\t<td>%s</td>\n' % (info[12])+'</tr>\n'
    return htmlstr

courseinfos = []

existedcourses = []
existedprevcourses = []
# if os.path.exists('courses.txt'):
#     with open('courses.txt', 'r') as f:
#         coursenames = f.readlines()
#         for name in coursenames:
#             existedcourses.append(name[:-1])
# if os.path.exists('prevcourses.txt'):
#     with open('prevcourses.txt', 'r') as f:
#         coursenames = f.readlines()
#         for name in coursenames:
#             existedprevcourses.append(name[:-1])
#print(existedcourses)

url_login = r"https://sso.buaa.edu.cn/login?TARGET=http%3A%2F%2Fbykc.buaa.edu.cn%2Fsscv%2FcasLogin"

option = webdriver.FirefoxOptions()
option.add_argument('--headless')
option.set_preference('permissions.default.stylesheet', 2)

driver = webdriver.Firefox(options=option)

errcnt = 0
print("start running")
while True:
    try:
        #driver.refresh()
        driver.get(url_login)
        try:
            _debug("putting username and pwd")
            # ?????????????????????
            _sleep(5)
            iframe = driver.find_element_by_xpath('//*[@id="loginIframe"]')
            driver.switch_to.frame(iframe)
            _sleep(5)
            user_name_input = driver.find_element_by_id('unPassword')
            user_name_input.send_keys(user_name)
            user_pwd_input = driver.find_element_by_id('pwPassword')
            user_pwd_input.send_keys(pwd)
            
            _debug("pressing login")
            # ????????????????????????
            driver.execute_script('loginPassword()')
            _sleep(10)
            _debug("refreshing")
            driver.refresh()
            _sleep(10)
        except:
            print(traceback.format_exc())
        
        _debug("finding course")
        mycourse = driver.find_element_by_xpath("//ul[@class='nav']/li[3]")
        mycourse.click()
        _sleep(1)
        courseselect = driver.find_element_by_xpath(
            "//ul[@class='nav-sub']/li[2]")
        courseselect.click()
        _sleep(10)
        
        _debug("decoding")
        webtext=driver.page_source.encode("utf8", "ignore").decode("utf8")

        coursepreview = driver.find_element_by_xpath(
            "//ul[@class='nav-sub']/li[1]")
        coursepreview.click()
        _sleep(10)
        prevwebtext = driver.page_source.encode(
            "utf8", "ignore").decode("utf8")

        driver.quit()
        break
    except:
        print(traceback.format_exc())
        # send_mail('Something wrong with course selection program',
        #           traceback.format_exc(),receivers)
        errcnt += 1
        _sleep(30)
        if errcnt >= MAXTRY:
            #driver.close()
            os._exit(0)

_debug("parsing")
Parser = MyHTMLParser()
Parser.feed(webtext)

#print(courseinfos)
coursedict = []
newcoursename = []
newprevcoursename = []
content='??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????<br>' +\
    '?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????<br>'+'???????????????%s<br>\n????????????????????????????????????????????????<br>\n' % time.asctime(
    time.localtime(time.time()))+'<table>\n<tr>\n\t<th>?????????</th>\n\t<th>????????????</th>\n' +\
    '\t<th>????????????</th>\n\t<th>????????????</th>\n\t<th>????????????</th>\n\t<th>????????????</th>\n\t<th>????????????</th>\n</tr>'

for info in courseinfos:
    if info[0] in existedcourses:
        continue
    newcoursename.append(info[0])
    content = content+parseinfo(info)
courseinfos=[]
Parser.feed(prevwebtext)
for info in courseinfos:
    if info[0] in existedprevcourses:
        continue
    newprevcoursename.append(info[0])
    content = content+parseprevinfo(info)

content += '</table>'
print(content)
#with open('mail.html', 'w') as f:
#    f.write(content)
# with open('courses.txt', 'a') as f:
#     for name in newcoursename:
#         f.write(name+'\n')
# with open('prevcourses.txt', 'a') as f:
#     for name in newprevcoursename:
#         f.write(name+'\n')
# if newcoursename or newprevcoursename:
#     send_mail('%s?????????????????????' % time.strftime("%m-%d %H:%M:%S",
#                                            time.localtime()), content, receivers)
#print(webtext)
