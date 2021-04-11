from django.shortcuts import render
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from BUAA.models import *
from BUAA import utils
import json
import uuid
import hashlib
import backend.settings as settings
from django.core.cache import cache
import requests
# from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
# from django_redis import get_redis_connection
from .serializers import *
from rest_framework.viewsets import ModelViewSet

def my_response(js_obj):
    print("RETURN RESPONSE: " + str(js_obj))
    return HttpResponse(json.dumps(js_obj), content_type="application/json", charset='utf-8', status='200',
                        reason='success')
                        

def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()


@api_view(['POST'])
@authentication_classes([])  # 添加
def send_email(request):
    sender = utils.MailSender()
#
#    print("request is", request.POST)
    email_address = request.data['email']
    random_str = get_random_str()[:6]
    sender.send_mail('BUAA Certification', 'Your verify code is {}, valid in 5 minutes'.format(random_str),
                     email_address)
    
    cache.set(random_str, email_address, 300)
    
    res = {
        'success': True,
        'msg': 'Email send'
    }
    print("successfully send email to", email_address)
    return my_response(res)

@api_view(['POST'])
@authentication_classes([])  # 添加
def verify_email(request):
    # TODO
    verifyCode = request.data['verifyCode']
    config_email = request.data['email']

    # token = request.COOKIES.get('token')
    # openid = utils.decode_openid(token)
    email = cache.get(verifyCode)

    if config_email == email:
        res = {
            'success': True,
            'msg': 'Valid Code'
        }
    else:
        res = {
            'success': False,
            'msg': 'Invalid Code',
            'errCode': 1 # TODO:分配一波errCode编码
        }
    return my_response(res)


@api_view(['POST'])
@authentication_classes([])  # 用户认证
def code2Session(request):
    print("code to session called")
    js_code = request.data['code']
    
    appid = settings.APPID
    secret = settings.SECRET
    
#    print(js_code)
    
    # TODO: save request.data['userInfo'] in database
    
    url = 'https://api.weixin.qq.com/sns/jscode2session' + '?appid=' + appid + '&secret=' + secret + '&js_code=' + js_code + '&grant_type=authorization_code'
    response = json.loads(requests.get(url).content)  # 将json数据包转成字典
    if 'errcode' in response:
        # 有错误码
        return my_response({'errCode': response['errcode'], 'msg': response['errmsg']})
    
    
    # 登录成功
    openid = response['openid']
    session_key = response['session_key']
    # 保存openid, 需要先判断数据库中有没有这个openid
    WXUser.objects.get_or_create(openid=openid)
    
    # 生成token,有效期1h
    token = utils.encode_openid(openid, 60 * 60)
    print('token is ', token)
    
#    print(user)
    
    # TODO: change this, refer to 后端接口说明.md
    res = {
        "code" : "blablabla", 
        "token" : token,
        "email" : ""
    }
    
    return my_response(res)

# 管理端接口
class OrganizationModelViewSet(ModelViewSet):
    """
    list:
    返回所有组织信息

    create:
    新建组织

    read:
    获取组织详情

    update:
    修改组织详情

    delete:
    删除组织
    """

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class WXUserViewSet(ModelViewSet):
    """
    list:
    返回所有用户信息

    create:
    新建用户（目前没用）

    read:
    获取用户信息

    update:
    修改用户信息

    delete:
    删除用户
    """

    queryset = WXUser.objects.all()
    serializer_class = WXUserSerializer


class CategoryViewSet(ModelViewSet):
    """
    list:
    返回所有分类

    create:
    新建分类

    read:
    获取分类

    update:
    修改分类

    delete:
    删除分类
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AddressViewSet(ModelViewSet):
    """
    list:
    返回所有地址

    create:
    新建地址

    read:
    获取地址

    update:
    修改地址

    delete:
    删除地址
    """
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class CommentViewSet(ModelViewSet):
    """
    list:
    返回所有评论

    create:
    新建评论

    read:
    获取评论

    update:
    修改评论

    delete:
    删除评论
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class BlockViewSet(ModelViewSet):
    """
    list:
    返回所有版块

    create:
    新建版块

    read:
    获取版块

    update:
    修改版块

    delete:
    删除版块
    """
    queryset = Block.objects.all()
    serializer_class = BlockSerializer


class UserFeedbackViewSet(ModelViewSet):
    """
    list:
    返回所有用户反馈

    create:
    新建用户反馈

    read:
    获取用户反馈

    update:
    修改用户反馈

    delete:
    删除用户反馈
    """
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer


class OrgApplicationViewSet(ModelViewSet):
    """
    list:
    返回所有组织申请

    create:
    新建组织申请

    read:
    获取组织申请

    update:
    修改组织申请

    delete:
    删除组织申请
    """
    queryset = OrgApplication.objects.all()
    serializer_class = OrgApplySerializer


class ActivityViewSet(ModelViewSet):
    """
    list:
    返回所有活动

    create:
    新建活动

    read:
    获取活动

    update:
    修改活动

    delete:
    删除活动
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer


class OrgMangerViewSet(ModelViewSet):
    """
    list:
    返回所有组织管理员

    create:
    新建组织管理员

    read:
    获取组织管理员

    update:
    修改组织管理员

    delete:
    删除组织管理员
    """
    queryset = OrgManager.objects.all()
    serializer_class = OrgManagerSerializer


class FollowedOrgViewSet(ModelViewSet):
    """
    list:
    返回所有关注组织

    create:
    新建关注组织

    read:
    获取关注组织

    update:
    修改关注组织

    delete:
    删除关注组织
    """
    queryset = FollowedOrg.objects.all()
    serializer_class = FollowedOrgSerializer


class JoinActApplicationViewSet(ModelViewSet):
    """
    list:
    返回所有加入活动申请

    create:
    新建加入活动申请

    read:
    获取加入活动申请

    update:
    修改加入活动申请

    delete:
    删除加入活动申请
    """
    queryset = JoinActApplication.objects.all()
    serializer_class = JoinActApplicationSerializer


class JoinedActViewSet(ModelViewSet):
    """
    list:
    返回所有活动参与人员

    create:
    新建活动参与人员

    read:
    获取活动参与人员

    update:
    修改活动参与人员

    delete:
    删除活动参与人员
    """
    queryset = JoinedAct.objects.all()
    serializer_class = JoinedActSerializer
    