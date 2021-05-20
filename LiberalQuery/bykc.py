# -*- coding: utf-8 -*-
import requests
import re
import os
import time
import getpass
import traceback
import json
import sys

DEBUG = True
LOG_DIR = './log'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
log_file = open(os.path.join(LOG_DIR, 'log.txt'), 'a')
ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
     'Chrome/86.0.4240.75 Safari/537.36'

vpn_url = 'https://e2.buaa.edu.cn/vpn_key/update?origin=https%3A%2F%2Fbykc.e2.buaa.edu.cn%2F&reason=site+bykc.e2.buaa.edu.cn+not+found'
sso_url = 'https://sso-443.e2.buaa.edu.cn/login?TARGET=https%3A%2F%2Fbykc.e2.buaa.edu.cn%2Fsscv%2FcasLogin'
bykc_url = 'https://bykc.e2.buaa.edu.cn/'

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def to_log(*object):
    print(get_log_time(), *object)
    print(get_log_time(), *object, file=log_file)


def save_html(dir, content):
    f = open(os.path.join(LOG_DIR, dir+get_file_time()+'.html'), 'wb')
    f.write(content)
    f.close()


def get_file_time(_time=time.localtime()):
    return time.strftime('_%m%d_%H%M%S', _time)


def get_log_time(_time=time.localtime()):
    return time.strftime('[%m.%d %H:%M:%S] ', _time)


def finalize():
    log_file.close()


def printd(*obj):
    if DEBUG:
        print(*obj)


class BYKC:
    def __init__(self, username, password):
        self.session = requests.session()
        self.session.headers['User-Agent'] = ua
        self.vpn_token = None
        self.vpn_form = {
            'utf8': '✓',
            'authenticity_token': self.vpn_token,
            'user[login]': username,
            'user[password]': password,
            'user[dymatice_code]': 'unknown',
            'commit': '登录 Login',
        }
        self.sso_execution = None
        self.sso_form = {
            "username": username,
            "password": password,
            "submit": "登录",
            "type": "username_password",
            "execution": self.sso_execution,
            "_eventId": "submit",
        }
        self.bykc_token = None
        self.session.headers.update({
            # 'Content-Type': 'application/json;charset=utf-8',
            'User-Agent': ua,
            'auth_token': self.bykc_token
        })

    def update_vpn_token(self):
        resp = self.session.get(vpn_url)
        to_log('VPN login page is redirected to', resp.url)
        if 'bykc' in resp.url:
            to_log('VPN redirected to bykc')
            return False
        pattern = '<meta name="csrf-token" content="(.*?)" />'
        result = re.search(pattern, resp.content.decode())
        if not result:
            to_log('No token found in VPN login page')
            save_html('vpn_login_error', resp.content)
            return False
        self.vpn_token = result.group(1)
        self.vpn_form['authenticity_token'] = self.vpn_token
        to_log('vpn token is updated')
        return True

    def login_vpn(self):
        if self.update_vpn_token():
            resp = self.session.post(
                'https://e2.buaa.edu.cn/users/sign_in', data=self.vpn_form)
            return resp
        else:
            to_log('No need to login vpn again')

    def update_bykc_token(self, url):
        result = re.search('token=(.*)', url)
        if not result:
            to_log('No token found in', url)
            return False
        self.bykc_token = result.group(1)
        self.session.headers.update({'auth_token': self.bykc_token})
        return True

    def update_sso_execution(self):
        resp = self.session.get(sso_url)
        to_log('SSO login page is redirected to', resp.url)
        if resp.url.startswith('https://bykc.'):
            to_log('SSO redirected to bykc')
            self.update_bykc_token(resp.url)
            return False
        pattern = '<input name="execution" value="(.*?)"/>'
        result = re.search(pattern, resp.content.decode())
        if not result:
            to_log('No execution found in SSO login page')
            save_html('sso_login_error', resp.content)
            return False
        self.sso_execution = result.group(1)
        self.sso_form['execution'] = self.sso_execution
        to_log('sso execution is updated')
        return True

    def login_sso(self):
        if self.update_sso_execution():
            resp = self.session.post(sso_url, data=self.sso_form)
            self.update_bykc_token(resp.url)
            return resp
        else:
            to_log('No need to login sso again')

    def login(self):
        res1 = self.login_vpn()
        res2 = self.login_sso()
        return res1, res2

    def query_selectable(self):
        self.login()
        to_log("query selectable begin")

        resp = self.session.post(
            bykc_url+'sscv/querySelectableCourse', data={})
        try:
            j = resp.json()
        except:
            to_log('response error at:', resp.url)
            save_html('query_error', resp.content)
            return
        if '成功' not in j.get('errmsg', ''):
            to_log('query error:', j.get('errmsg', ''))
            save_html('selectable_error', resp.content)
            return
        if 'data' not in j:
            to_log("unknown error")
            save_html('selectable_unknown_error', resp.content)
            return

        to_log('query selectable end')
        return j

    def chose(self, id):
        self.login()
        to_log("chose begin")
        resp = self.session.post(bykc_url+'sscv/choseCourse',
                                 data='{"courseId": % d}' % id)
        to_log("chose end")
        print(resp.json())

    def del_chosen(self, id):
        to_log("del_chosen begin")
        resp = self.session.post(
            bykc_url+'sscv/delChosenCourse', data='{"id":%d} ' % id)
        to_log("del_chosen end")
        print(resp.json())


def time_convert(t):
    return 'T'.join(t.split()[:2])


def info_convert(info):
    data = {
        'name': info['courseName'],
        'contain': info['courseMaxCount'],
        'begin_time': time_convert(info['courseStartDate']),
        'end_time': time_convert(info['courseEndDate']),
        'location': info['coursePosition']
    }
    return {str(info['id']): data}


def time_before_now(t):
    return time.mktime(time.strptime(t, '%Y-%m-%dT%H:%M:%S')) < time.time()


def create_new_course(cid, cinfo, BASE_PATH):
    with open(BASE_PATH+cid+'.tmp', 'w') as f:
        f.write(json.dumps(cinfo))
    if os.path.exists(BASE_PATH+cid+'.json'):
        os.remove(BASE_PATH+cid+'.json')
    os.rename(BASE_PATH+cid+'.tmp', BASE_PATH+cid+'.json')


if __name__ == '__main__':
    INTERVAL = 300
    ERR_MAX = 10
    HISTORY_PATH = os.path.join(LOG_DIR, 'history.json')
    NEW_PATH = os.path.expanduser('~/boya/')
    if not os.path.exists(NEW_PATH):
        os.makedirs(NEW_PATH)

    print('For safety reason, you should run this program in a tmux session and\n'
          'destory the session after you entered your password')
    # pwd should be input, rather than saved in config.json
    if sys.platform == 'win32':
        import config
        Config = config.Config()
        username = Config.username
        pwd = Config.password
    else:
        username = input('Your username:')
        pwd = getpass.getpass('Your password:')
    b = BYKC(username, pwd)

    error_cnt = 0
    while True:
        try:
            courses_raw = b.query_selectable()
            courses = {}
            for info in courses_raw['data']:
                courses.update(info_convert(info))
            history_courses = {}
            if os.path.exists(HISTORY_PATH):
                with open(HISTORY_PATH, 'r') as f:
                    history_courses = json.loads(f.read())
            for cid, cinfo in courses.items():
                if history_courses.get(cid) == None:
                    create_new_course(cid, cinfo, NEW_PATH)
            for hid, hinfo in list(history_courses.items()):
                if time_before_now(hinfo['courseEndDate']):
                    history_courses.pop(hid)
            history_courses.update(courses)
            with open(HISTORY_PATH, 'w') as f:
                f.write(json.dumps(history_courses))
            error_cnt = 0
        except:
            error_cnt += 1
            to_log(traceback.format_exc())
            if error_cnt >= ERR_MAX:
                to_log('Errors occured have exceeded limit, program will exit')
                break
        time.sleep(INTERVAL)

    finalize()
