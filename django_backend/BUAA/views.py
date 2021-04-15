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
# from django_redis import get_redis_connection
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import *
                        

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
    
    cache.set(random_str, email_address, 300)  # 验证码时效5分钟
    
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
        status = 200
    else:
        res = {
            'status': 1,
            'msg': 'Invalid Code'
        }
        status = 400
    return Response(res, status)
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








class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer





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
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer




class ActivityViewSet(ModelViewSet):
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


class JoinActApplicationViewSet(ModelViewSet):
    queryset = JoinActApplication.objects.all()
    serializer_class = JoinActApplicationSerializer


class JoinedActViewSet(ModelViewSet):
    queryset = JoinedAct.objects.all()
    serializer_class = JoinedActSerializer





"""-------------------完成--------------------"""
# 用户
class WXUserViewSet(ModelViewSet):
    queryset = WXUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return TestUserSerializer
        return WXUserSerializer


# 版块
class BlockViewSet(ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer


# 组织申请
class OrgApplicationViewSet(ModelViewSet):
    queryset = OrgApplication.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return OrgAppCreateSerializer
        if self.action == "verify":
            return OrgAppVerifySerializer
        return OrgApplySerializer

    def user_get_all(self, request, user_id):
        applications = OrgApplication.objects.filter(user=user_id)
        serializer = self.get_serializer(instance=applications, many=True)
        return Response(serializer.data)

    def verify(self, request, pk):
        application = self.get_object()
        old_status = application.status
        if old_status != 0:
            return Response(data={"detail": ["该组织申请已审批。"]}, status=400)
        serializer = self.get_serializer(instance=application, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, 201)


# 组织
class OrganizationModelViewSet(ModelViewSet):
    queryset = Organization

    def get_serializer_class(self):
        if self.action == "create":
            return OrganizationSerializer
        return OrgDetailSerializer

    def get_org_by_block(self, request, block_id):
        organizations = Organization.objects.filter(block=block_id)
        serializer = self.get_serializer(instance=organizations, many=True)
        return Response(serializer.data, 200)


# 关注组织
class FollowedOrgViewSet(ModelViewSet):
    queryset = FollowedOrg.objects.all()

    def get_serializer_class(self):
        if self.action == "get_followed_org_by_user":
            return UserFollowedOrgSerializer
        return FollowedOrgSerializer

    def destroy(self, request, *args, **kwargs):
        user_id = request.query_params.get('user')
        org_id = request.query_params.get('org')
        FollowedOrg.objects.filter(org=org_id, person=user_id).delete()
        return Response(status=204)

    def get_followed_org_by_user(self, request, pk):
        followed = FollowedOrg.objects.filter(person=pk)
        serializer = self.get_serializer(instance=followed, many=True)
        return Response(serializer.data, 200)



