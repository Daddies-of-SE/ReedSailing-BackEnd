from django.shortcuts import render
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.cache import caches
from BUAA.models import *
from BUAA import utils
import json
import uuid
import hashlib
import backend.settings as settings
from django.core.cache import cache
import requests
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from django_redis import get_redis_connection
from .serializers import *


def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()


def send_email(request):
    sender = utils.MailSender()

    print("request is", request.POST)
    email_address = request.POST.get('email')
    random_str = get_random_str()[:6]
    sender.send_mail('BUAA Certification', 'Your verify code is {}, valid in 5 minutes'.format(random_str),
                     email_address)

    cache.set(random_str, email_address, 300)

    res = {
        'success': "true",
        'mess': 'Email send'
    }
    print("successfully send email to", email_address)
    print(res)
    return HttpResponse(json.dumps(res), content_type="application/json", charset='utf-8', status='200',
                        reason='success')


def verify_email(request):
    code = request.POST.get('code')
    valid = cache.get(code)
    if valid:
        res = {
            'success': "true",
            'mess': 'Valid Code'
        }
    else:
        res = {
            'success': "false",
            'mess': 'Invalid Code'
        }
    return HttpResponse(json.dumps(res), content_type="application/json", charset='utf-8', status='200',
                        reason='success')


@api_view(['POST'])
@authentication_classes([])  # 添加
def code2Session(request):
    appid = 'wx6e4e33e0b6db916e'
    secret = 'fc9689a2497195707d9f85e48628b351'
    js_code = request.data['code']
    url = 'https://api.weixin.qq.com/sns/jscode2session' + '?appid=' + appid + '&secret=' + secret + '&js_code=' + js_code + '&grant_type=authorization_code'
    response = json.loads(requests.get(url).content)  # 将json数据包转成字典
    if 'errcode' in response:
        # 有错误码
        return Response(data={'code': response['errcode'], 'msg': response['errmsg']})
    # 登录成功
    openid = response['openid']
    session_key = response['session_key']
    # 保存openid, 需要先判断数据库中有没有这个openid
    user, created = User.objects.get_or_create(openid=openid)
    user_str = str(UserLoginSerializer(user).data)
    # 生成自定义登录态，返回给前端
    sha = hashlib.sha1()
    sha.update(openid.encode())
    sha.update(session_key.encode())
    digest = sha.hexdigest()
    # 将自定义登录态保存到缓存中, 两个小时过期
    conn = get_redis_connection('session')
    conn.set(digest, user_str, ex=2 * 60 * 60)
    return Response(data={'code': 200, 'msg': 'ok', 'data': {'skey': digest}})
