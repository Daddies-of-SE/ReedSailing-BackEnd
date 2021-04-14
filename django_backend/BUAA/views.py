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
from rest_framework.views import APIView
from rest_framework.response import Response
                        

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
        'status': 0,
        'msg': 'Email send'
    }
    print("successfully send email to", email_address)
    return Response(data=res, status=200)
    # return my_response(res)


@api_view(['POST'])
@authentication_classes([])  # 添加
def verify_email(request):
    verifyCode = request.data['verifyCode']
    config_email = request.data['email']
    id = request.data['id']

    # token = request.COOKIES.get('token')
    # openid = utils.decode_openid(token)
    email = cache.get(verifyCode)

    if config_email == email:
        res = {
            'status': 0,
            'msg': 'Valid Code'
        }
        WXUser.objects.filter(id=id).update(email=email)
    else:
        res = {
            'status': 1,
            'msg': 'Invalid Code'
        }
    return Response(res,200)
    # return my_response(res)


@api_view(['POST'])
@authentication_classes([])  # 用户认证
def code2Session(request):
    # 取出数据
    js_code = request.data['code']
    user_info = request.data['userInfo']

    # 获取openid和session_key
    appid = settings.APPID
    secret = settings.SECRET
    url = 'https://api.weixin.qq.com/sns/jscode2session' + '?appid=' + appid + '&secret=' + secret + '&js_code=' + js_code + '&grant_type=authorization_code'
    response = json.loads(requests.get(url).content)  # 将json数据包转成字典
    if 'errcode' in response:
        # 有错误码
        return Response(data={
            'status': 1, 
            'code': response['errcode'], 
            'msg': response['errmsg']
        }, status=400)
    # 登录成功
    openid = response['openid']
    session_key = response['session_key']

    # 保存openid, name, avatar
    user, create = WXUser.objects.get_or_create(openid=openid)
    WXUser.objects.filter(openid=openid).update(name=user_info.get("nickName"), avatar=user_info.get("avatarUrl"))
    
    print(WXUser.objects.get_or_create(openid=openid))

    token = utils.encode_openid(openid, 24*60*60)
    cache.set(token, openid)

    res = {
        "status" : 0,
        "user_Exist": 0 if create else 1,
        "token": token,
        "email": user.email,
        "id": user.id,
        "avatar": user.avatar,
        "sign": user.sign,
        "name": user.name,
    }
    return Response(data=res, status=200)


# 管理端接口
class OrganizationModelViewSet(APIView):
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
    def get(self, request, *args, **kwargs):
        # 查询所有
        if not request.query_params.get('org'):
            all_orgs = Organization.objects.all()
            data = OrganizationSerializer(all_orgs, many=True).data
        else:
            org_name = request.query_params.get('org')
            try:
                org = Organization.objects.get(name=org_name)
                data = OrganizationSerializer(org).data
            except:
                return Response({
                    'status': 1,
                    'msg': 'invalid org name'
                })
        return Response({
            'status': 0,
            'msg': 'ok',
            'results': data
        })

class WXUserViewSet(APIView):
    def get(self, request, *args, **kwargs):
        id = request.query_params.get('id')
        try:
            user = WXUser.objects.get(id=id)
        except:
            return Response({
                'status': 1,
                'msg': 'invalid userID'
            })
        data = WXUserSerializer(user).data
        return Response({
            'status': 0,
            'msg': 'ok',
            'results': data
        })

    def patch(self, request, *args, **kwargs):
        request_data = dict(request.data)
        request_query = request.query_params
        try:
            user_id = request_query.get('id')
            usr = WXUser.objects.get(id=user_id)
        except:
            return Response({
                'status': 1,
                'msg': 'invalid userID'
            })
        request_data["openid"] = usr.openid
        if not request_data.get("name"):
            request_data['name'] = usr.name
        ser = WXUserSerializer(instance=usr, data=request_data)
        ser.is_valid(raise_exception=True) # 校验不通过自动抛异常
        objs = ser.save()
        return Response({
            'status': 0,
            'msg': 'ok',
            'results':WXUserSerializer(objs).data
        })


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


class BlockOrgsViewSet(APIView):
    #查看block下的所有组织
    def get(self, request, *args, **kwargs):
        block_id = request.query_params.get('block')
        block = Block.objects.get(id=block_id)
        query = Organization.objects.filter(block=block)
        data = OrganizationSerializer(query, many=True).data
        return Response({
            'status': 0,
            'msg': 'ok',
            'results': data
        })

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


class OrgMangerViewSet(APIView):

    #查看组织所有管理员
    def get(self, request, *args, **kwargs):
        def get_managers(request):
        # 查看某组织的所有管理员
            org_name = request.query_params.get('org')
            # 群查
            if not org_name:
                all_orgs = OrgManager.objects.all()
                data = OrgManagerSerializer(all_orgs, many=True).data
            else:
                try:
                    org = Organization.objects.get(name=org_name)
                    query = OrgManager.objects.filter(org=org)
                    data = OrgManagerSerializer(query, many=True).data
                except:
                    return Response({
                        'status': 1,
                        'msg': 'invalid org name'
                    })
            return Response({
                'status': 0,
                'msg': 'ok',
                'results': data
            })

        #查看当前用户管理的所有组织
        def get_orgs(request):
            id = request.query_params.get('id')
            try:
                user = WXUser.objects.get(id=id)
            except:
                return Response({
                    'status': 1,
                    'msg': 'invalid userID'
                })
            query = OrgManager.objects.filter(person=user)
            data = OrgManagerSerializer(query, many=True).data
            return Response({
                'status': 0,
                'msg': 'ok',
                'results': data
            })

        if request.query_params.get('user_view', False):
            return get_orgs(request)
        return get_managers(request)



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
    