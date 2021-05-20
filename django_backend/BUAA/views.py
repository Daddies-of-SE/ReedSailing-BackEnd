from BUAA import utils, notification
import BUAA.models
import json
import uuid
import hashlib
import backend.settings as settings
from django.core.cache import cache
import requests
from rest_framework.decorators import api_view, authentication_classes
from .serializers import *
from rest_framework.response import Response
from rest_framework.viewsets import *
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django_redis import get_redis_connection
import datetime
from BUAA.const import NOTIF, BLOCKID
import time
import os

base_dir = '/root/ReedSailing-Web/server_files/'
#base_dir = '/Users/wzk/Desktop/'
web_dir = 'https://www.reedsailing.xyz/server_files/'


def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()

# 仅供文件内部调用
def _send_notif(p_id, notif):
    """revoke when user keeps online"""
    p_id = int(p_id)
    if p_id in notification.clients :
        p_ws = notification.clients[p_id]
        p_ws.send(str([notif]))
    else :
        new_send_notification(notif['id'], p_id)


def _act_id2act_name(pk):
    pk = int(pk)
    return BUAA.models.Activity.objects.get(id=pk).name

def _org_id2org_name(pk):
    pk = int(pk)
    return BUAA.models.Organization.objects.get(id=pk).name

def _user_id2user_name(pk):
    pk = int(pk)
    return BUAA.models.WXUser.objects.get(id=pk).name



"""
新建通知

输入：
    content：通知内容
输出：
    数据字典
        id：该notification的id
        time： 发布时间
        content： 通知内容
"""
def new_notification(type, content, act_id = None, org_id = None):
    data = {
        'type' : type,
        'content': content,
    }
    if act_id: data['act'] = act_id
    if org_id: data['org'] = org_id
    serializer = NotificationSerializer(data=data)
    serializer.is_valid()
    serializer.save()
    return serializer.data


"""
新建发送通知关系

输入：
    notif_id: 通知的id
    user_id: 接收通知的用户id
输出：
    数据字典：
        id：发送通知关系的id
        notif： 通知的id
        person： 接收通知的用户的id
        already_read： 是否已读（为false）
"""
def new_send_notification(notif_id, user_id):
    data = {
        'notif': notif_id,
        'person': user_id
    }
    serializer = SentNotificationSerializer(data=data)
    serializer.is_valid()
    serializer.save()
    return serializer.data



def get_access_token():
    def get_from_wx_api():
        appid = settings.APPID
        secret = settings.SECRET
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + secret
        response = json.loads(requests.get(url).content)
        with open("./access_token.txt", "w") as f:
            print(response["access_token"], file=f)
            print(time.time(), file=f)
            print(response["expires_in"], file=f)
        return response["access_token"]
    
    if not os.path.exists("../access_token.txt"):
        return get_from_wx_api()
        
    with open("../access_token.txt") as f:
        lines = f.readlines()
        if time.time() - int(lines[1].strip()) > int(lines[2].strip()):
            return get_from_wx_api()
        return lines[0].strip()
            

@api_view(['POST'])
@authentication_classes([])
def get_page_qrcode(request):
    body = {
        "path" : request.data["path"],
        "width" : request.data["width"],
    }
    r = requests.post(url="https://api.weixin.qq.com/cgi-bin/wxaapp/createwxaqrcode?access_token=" + get_access_token(), data=json.dumps(body), headers={"Content-Type": "application/json"})
    
    path = "qrcode/" + get_random_str() + '.png'
    with open(base_dir + path, 'wb') as f:
            f.write(r.content)
    
    res = {
        "img" : web_dir + path
    }
    
    return Response(data=res, status=200)


@api_view(['POST'])
@authentication_classes([])  # 添加
def send_email(request):

    sender = utils.MailSender()
#
#    print("request is", request.POST)
    email_address = request.data['email']
    if not email_address.endswith("@buaa.edu.cn"):
        res = {
            'status' : 1,
            'msg' : 'Email address not belong to BUAA'
        }
        return Response(data=res, status=400)

    random_str = get_random_str()[:6]
    sender.send_mail('BUAA Certification', 'Your verify code is {}, valid in 5 minutes'.format(random_str),
                     email_address)
    
    cache.set(random_str, email_address, 300)  # 验证码时效5分钟
    # # 用redis代替
    # redis_conn = get_redis_connection("code")
    # redis_conn.set("sms_code_%s" % email_address, random_str, 300)
    
    res = {
        'status': 0,
        'msg': 'Email send'
    }
    # print("successfully send email to", email_address)
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
        WXUser.objects.filter(id=id).update(email=config_email)
        status = 200
    else:
        res = {
            'status': 1,
            'msg': 'Invalid Code',
        }
        status = 400

    # # 用redis代替
    # redis_conn = get_redis_connection("code")
    # redis_sms_code = redis_conn.get("sms_code_%s" % config_email)
    # if verifyCode == redis_sms_code:
    #     res = {
    #         'status': 0,
    #         'msg': 'Valid Code'
    #     }
    #     WXUser.objects.filter(id=id).update(email=config_email)
    #     status = 200
    #
    # else:
    #     res = {
    #         'status': 1,
    #         'msg': 'Invalid Code',
    #     }
    #     status = 400

    return Response(res, status)
    # return my_response(res)


@api_view(['POST'])
@authentication_classes([])
def user_login(request):
    #raise Exception
    # 取出数据
    # print('login')
    js_code = request.data['code']
    
    # 获取openid和session_key
    appid = settings.APPID
    secret = settings.SECRET
    url = 'https://api.weixin.qq.com/sns/jscode2session' + '?appid=' + appid + '&secret=' + secret + '&js_code=' + js_code + '&grant_type=authorization_code'
    response = json.loads(requests.get(url).content)  # 将json数据包转成字典
    
    if 'errcode' in response:
        # 有错误码
        # print("err msg" + response['errmsg'])
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
    
    # print(WXUser.objects.get_or_create(openid=openid))
    
    token = utils.encode_openid(openid, 24*60*60)
    cache.set(token, openid, 24*60*60)
    
    res = {
        "status": 0,
        "userExist": 0 if create else 1,
        "token": token,
        "email": user.email,
        "id": user.id,
        "avatar": user.avatar,
        "sign": user.sign,
        "name": user.name,
        "contact" : user.contact
    }
    return Response(data=res, status=200)
    

@api_view(['POST'])
@authentication_classes([])  # 用户认证
def user_register(request):
    # 取出数据
    id_ = request.data['id']
    user_info = request.data['userInfo']
    WXUser.objects.filter(id=id_).update(name=user_info.get("nickName"), avatar=user_info.get("avatarUrl"))
    
    # print("register user", WXUser.objects.get_or_create(id=id_))

    res = {
        "status": 0
    }
    return Response(data=res, status=200)


@api_view(['POST'])
def user_org_relation(request):
    user_id = request.data['user']
    org_id = request.data['org']
    try:
        user = WXUser.objects.get(id=user_id)
    except:
        res = {
            "detail": '未找到用户'
        }
        status = 404
        return Response(res,status)
    try:
        org = Organization.objects.get(id = org_id)
    except:
        res = {
            "detail": '未找到组织'
        }
        status = 404
        return Response(res,status)
    res = {
        "isFollower" : False,
        "isOwner" : False,
        "isManager" : False,
    }
    if FollowedOrg.objects.filter(org=org_id,person=user_id):
        res["isFollower"]=True
    if Organization.objects.filter(id = org_id, owner=user_id):
        res["isOwner"]=True
    if OrgManager.objects.filter(org=org_id,person=user_id):
        res["isManager"]=True
    return Response(res)

@api_view(['POST'])
def user_act_relation(request):
    user_id = request.data['user']
    act_id = request.data['act']
    try:
        user = WXUser.objects.get(id=user_id)
    except:
        res = {
            "detail": '未找到用户'
        }
        status = 404
        return Response(res,status)
    try:
        act = Activity.objects.get(id=act_id)
    except:
        res = {
            "detail": '未找到活动'
        }
        status = 404
        return Response(res,status)
    res = {
        "hasJoined" : False,
        "underReview" : False,
        "isOwner" : False,
        "isManager" :False,
    }
    if JoinedAct.objects.filter(act=act_id,person=user_id):
        res["hasJoined"] = True
    if Activity.objects.filter(id=act_id,owner=user_id):
        res["isOwner"]=True
        res["isManager"] = True
    org_id = act.org_id
    if Organization.objects.filter(id = org_id,owner=user_id):
        res["isManager"] = True
    if OrgManager.objects.filter(org=org_id,person=user_id):
        res["isManager"] = True
    return Response(res)











class JoinActApplicationViewSet(ModelViewSet):
    queryset = JoinActApplication.objects.all()
    serializer_class = JoinActApplicationSerializer


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

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    # 获取用户的组织申请
    def user_get_all(self, request, user_id):
        applications = OrgApplication.objects.filter(user=user_id)
        return self.paginate(applications)

    # 审批组织申请
    def verify(self, request, pk):
        application = self.get_object()
        old_status = application.status
        if old_status != 0:
            return Response(data={"detail": ["该组织申请已审批。"]}, status=400)
        status = int(request.data.get('status'))
        org_name = application.name
        if status == 1:
            # 审核通过
            # 1.创建组织
            data = {
                "name": application.name,
                "owner": application.user.id,
                "block": application.block.id
            }
            serializer = OrganizationSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            org_id = serializer.data.get('id')
            owner_id = application.user.id
            # 2.添加负责人为管理员
            data = {
                "org": org_id,
                "person": owner_id
            }
            serializer = OrgManagerSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # test
            serializer = self.get_serializer(instance=application, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # notification
            content = utils.get_notif_content(NOTIF.OrgApplyRes, org_name=org_name, status=True)
            notif = new_notification(NOTIF.OrgApplyRes, content, org_id=org_id)
            _send_notif(owner_id, notif)

            return Response(serializer.data, 201)

        else:
            serializer = self.get_serializer(instance=application, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # notification
            content = utils.get_notif_content(NOTIF.OrgApplyRes, org_name=org_name, status=False)
            notif = new_notification(NOTIF.OrgApplyRes, content, org_id=None)
            _send_notif(application.user.id, notif)

            return Response(serializer.data, 200)


# 组织
class OrganizationModelViewSet(ModelViewSet):
    queryset = Organization.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return OrganizationSerializer
        if self.action == "change_org_owner":
            return OrgOwnerSerializer
        return OrgDetailSerializer

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    # def create_wrapper(self, request):
    #     self.create(request)
    #     content = utils.get_notif_content(NOTIF.OrgApplyRes, )

    # 获取版块下的组织
    def get_org_by_block(self, request, block_id):
        organizations = Organization.objects.filter(block=block_id)
        return self.paginate(organizations)

    # 修改组织负责人
    def change_org_owner(self, request, pk):
        organization = self.get_object()
        serializer = self.get_serializer(instance=organization, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        content = utils.get_notif_content(NOTIF.BecomeOwner, org_name=_org_id2org_name(pk))
        notif = new_notification(NOTIF.BecomeOwner, content, org_id=pk)
        _send_notif(request.data['owner'], notif)


        return Response(serializer.data, 200)

    # 推荐组织
    def get_recommended_org(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    #搜索组织
    def search_all(self,request):
        org_name = request.data.get('name')
        organizations = Organization.objects.filter(name__contains=org_name)
        return self.paginate(organizations)

    #板块下搜索组织
    def search_org_by_block(self, request, block_id):
        org_name = request.data.get('name')
        organizations = Organization.objects.filter(name__contains=org_name,block=block_id)
        return self.paginate(organizations)


# 关注组织
class FollowedOrgViewSet(ModelViewSet):
    queryset = FollowedOrg.objects.all()

    def get_serializer_class(self):
        if self.action == "get_followed_org":
            return UserFollowedOrgSerializer
        return FollowedOrgSerializer

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user_id = request.query_params.get('user')
        org_id = request.query_params.get('org')
        FollowedOrg.objects.filter(org=org_id, person=user_id).delete()
        return Response(status=204)

    # 获取用户关注的组织
    def get_followed_org(self, request, pk):
        followed = FollowedOrg.objects.filter(person=pk)
        return self.paginate(followed)


# 组织管理
class OrgManageViewSet(ModelViewSet):
    queryset = OrgManager.objects.all()

    def get_serializer_class(self):
        if self.action == "get_managed_org" or self.action == "search_managed_org":
            return UserManagedOrgSerializer
        if self.action == "get_all_managers":
            return OrgAllManagersSerializer
        return OrgManagerSerializer

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user_id = request.query_params.get('user')
        org_id = request.query_params.get('org')
        OrgManager.objects.filter(org=org_id, person=user_id).delete()

        content = utils.get_notif_content(NOTIF.RemovalFromAdmin, org_name=_org_id2org_name(org_id))
        notif = new_notification(NOTIF.RemovalFromAdmin, content, org_id=org_id)
        _send_notif(user_id, notif)

        return Response(status=204)

    # 获取用户管理的组织
    def get_managed_org(self, request, pk):
        managed = OrgManager.objects.filter(person=pk)
        return self.paginate(managed)

    # 获取组织的管理员
    def get_all_managers(self, request, pk):
        managers = OrgManager.objects.filter(org=pk)
        return self.paginate(managers)

    #搜索用户管理的组织
    def search_managed_org(self,request,pk):
        org_name = request.data.get("name")
        managed = OrgManager.objects.filter(person=pk, org__name__contains=org_name)
        return self.paginate(managed)


# 活动分类
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# 活动地址
class AddressViewSet(ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


# 用户反馈
class UserFeedbackViewSet(ModelViewSet):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer


# 活动
class ActivityViewSet(ModelViewSet):
    queryset = Activity.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return ActivitySerializer
        if self.action == "destroy":
            return ActivitySerializer
        if self.action == "update":
            return ActUpdateSerializer
        return ActDetailSerializer

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    # update_wrapper
    def update_wrapper(self, request, pk):
        pk = int(pk)
        res = self.update(request)
        # create notif
        content = utils.get_notif_content(NOTIF.ActContent, act_name=_act_id2act_name(pk))
        notif = new_notification(NOTIF.ActContent, content, act_id=pk, org_id=None)
        # send notification
        persons = JoinedAct.objects.filter(act=pk)
        for p in persons:
            _send_notif(p.person_id, notif)
        return res

    def destroy_wrapper(self, request, pk):
        pk = int(pk)
        res = self.destroy(request)
        content = utils.get_notif_content(NOTIF.ActCancel, act_name=_act_id2act_name(pk))
        notif = new_notification(NOTIF.ActCancel, content, act_id=pk, org_id=None)
        persons = JoinedAct.objects.filter(act=pk)
        for p in persons:
            _send_notif(p.person_id, notif)
        return res


    # 获取组织下的活动
    def get_org_act(self, request, org_id):
        acts = Activity.objects.filter(org=org_id)
        return self.paginate(acts)
    
    def get_org_act_status(self, request, org_id):
        now = datetime.datetime.now()
        ret = {
        'unstart': self.get_serializer(Activity.objects.filter(org=org_id,begin_time__gt=now), many=True).data,
        'cur': self.get_serializer(Activity.objects.filter(org=org_id, end_time__gte=now, begin_time__lte=now), many=True).data,
        'end': self.get_serializer(Activity.objects.filter(org=org_id, end_time__lt=now), many=True).data
        }
        return Response(ret, 200)

    # 获取用户发布的活动
    def get_user_act(self, request, user_id):
        acts = Activity.objects.filter(owner=user_id)
        return self.paginate(acts)
    
    def get_user_act_status(self, request, user_id):
        now = datetime.datetime.now()
        ret = {
        'unstart': self.get_serializer(Activity.objects.filter(owner=user_id,begin_time__gt=now), many=True).data,
        'cur': self.get_serializer(Activity.objects.filter(owner=user_id, end_time__gte=now, begin_time__lte=now), many=True).data,
        'end': self.get_serializer(Activity.objects.filter(owner=user_id, end_time__lt=now), many=True).data
        }
        return Response(ret, 200)

    # 获取用户管理的未开始活动 开始时间>现在
    def get_user_unstart_act(self, request, user_id):
        now = datetime.datetime.now()
        acts = Activity.objects.filter(owner=user_id,begin_time__gt=now)
        return self.paginate(acts)

    # 获取用户管理的进行中活动 开始时间 < 现在 < 结束时间
    def get_user_ing_act(self, request, user_id):
        now = datetime.datetime.now()
        acts = Activity.objects.filter(owner=user_id, end_time__gte=now, begin_time__lte=now)
        return self.paginate(acts)

    # 获取用户管理的已结束活动,结束时间 < 现在
    def get_user_finish_act(self,request,user_id):
        now = datetime.datetime.now()
        acts = Activity.objects.filter(owner=user_id, end_time__lt=now)
        return self.paginate(acts)

    # 获取板块下的活动
    def get_block_act(self, request, block_id):
        acts = Activity.objects.filter(block=block_id)
        return self.paginate(acts)
    
    def get_block_act_status(self, request, block_id):
        now = datetime.datetime.now()
        ret = {
        'unstart': self.get_serializer(Activity.objects.filter(block = block_id,begin_time__gt=now), many=True).data,
        'cur': self.get_serializer(Activity.objects.filter(block = block_id,begin_time__gt=now), many=True).data,
        'end': self.get_serializer(Activity.objects.filter(block = block_id, end_time__lt=now), many=True).data
        }
        return Response(ret, 200)

    # 获取用户关注的组织发布的活动
    def get_followed_org_act(self, request, user_id):
        orgs = FollowedOrg.objects.filter(person=user_id)
        acts = Activity.objects.filter(org__in=[org.org_id for org in orgs]).order_by('pub_time').reverse()
        return self.paginate(acts)

    # 推荐活动
    def get_recommended_act(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    #搜索活动
    def search_all(self,request):
        act_name = request.data.get("name")
        activities = Activity.objects.filter(name__contains=act_name)
        return self.paginate(activities)

    #板块下搜索活动
    def search_act_by_block(self,request,block_id):
        act_name = request.data.get("name")
        activities = Activity.objects.filter(name__contains=act_name,block=block_id)
        return self.paginate(activities)

    #组织下搜索活动
    def search_act_by_org(self,request,org_id):
        act_name = request.data.get("name")
        activities = Activity.objects.filter(name__contains=act_name,org=org_id)
        return self.paginate(activities)

    #搜索指定用户发布的活动
    def search_user_released_act(self, request,user_id):
        act_name = request.data.get("name")
        activities = Activity.objects.filter(name__contains=act_name,owner=user_id)
        return self.paginate(activities)





# 活动参与
class JoinedActViewSet(ModelViewSet):
    queryset = JoinedAct.objects.all()

    def get_serializer_class(self):
        if self.action == "get_user_joined_act":
            return UserJoinedActSerializer
        if self.action == "get_user_joined_act_begin_order":
            return UserJoinedActSerializer
        if self.action == "get_user_joined_act_status":
            return UserJoinedActSerializer
        if self.action == "get_act_participants":
            return JoinedActParticipants
        return JoinedActSerializer

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    # 加入活动
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        act_id = request.data.get("act")
        current_number = JoinedAct.objects.filter(act=act_id).count()
        limit_number = Activity.objects.get(id=act_id).contain
        if current_number < limit_number:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "活动人数已满。"}, 400)

    # 退出活动
    def destroy(self, request, *args, **kwargs):
        user_id = request.query_params.get('person')
        act_id = request.query_params.get('act')
        JoinedAct.objects.filter(act=act_id, person=user_id).delete()

    def destroy_wrapper(self, request) :
        user_id = request.query_params.get('person')
        act_id = request.query_params.get('act')
        self.destroy(request)
        content = utils.get_notif_content(NOTIF.RemovalFromAct, act_name=_act_id2act_name(act_id))
        notif = new_notification(NOTIF.RemovalFromAct, content, act_id=act_id, org_id=None)
        _send_notif(user_id, notif)
        return Response('')

    # 获取活动的参与人数
    def get_act_participants_number(self, request, act_id):
        number = JoinedAct.objects.filter(act=act_id).count()
        return Response({"number": number}, 200)

    # 获取活动的所有的参与者
    def get_act_participants(self, request, act_id):
        users = JoinedAct.objects.filter(act=act_id)
        return self.paginate(users)

    # 获取用户参与的活动
    def get_user_joined_act(self, request, user_id):
        acts = JoinedAct.objects.filter(person=user_id)
        return self.paginate(acts)
    
    def get_user_joined_act_status(self, request, user_id):
        now = datetime.datetime.now()
        ret = {
        'unstart': self.get_serializer(JoinedAct.objects.filter(act__begin_time__gt=now, person=user_id), many=True).data,
        'cur': self.get_serializer(JoinedAct.objects.filter(act__end_time__gte=now, act__begin_time__lte=now, person=user_id), many=True).data,
        'end': self.get_serializer(JoinedAct.objects.filter(act__end_time__lt=now, person=user_id), many=True).data
        }
        return Response(ret, 200)

    # 获取指定用户指定年月中参与的所有活动
    def get_user_joined_act_begin_order(self, request, user_id, month, year):
        acts = JoinedAct.objects.filter(person=user_id, act__begin_time__month=month, act__begin_time__year=year)
        serializer = self.get_serializer(acts, many=True)
        data = serializer.data
        ret = {}
        for d in data:
            act = d['act']
            if act['begin_time'].split('T')[0] in ret.keys():
                ret[act['begin_time'].split('T')[0]].append(act)
            else:
                ret[act['begin_time'].split('T')[0]] = [act]
        return Response(ret, 200)

   #搜索用户参与的活动
    def search_user_joined_act(self,request,user_id):
        act_name = request.data.get("name")
        acts = JoinedAct.objects.filter(person=user_id,act__name__contains=act_name)
        return self.paginate(acts)
    
    


# 活动评价
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.action == "get_act_comments":
            return CommentDetailSerializer
        if self.action == "list":
            return CommentListSerializer
        if self.action == "get_user_comment":
            return CommentDetailSerializer
        if self.action == "update":
            return CommentUpdateSerializer
        if self.action == "retrieve":
            return CommentUpdateSerializer
        return CommentSerializer

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    # 获取指定活动的所有评价
    def get_act_comments(self, request, act_id):
        comments = Comment.objects.filter(act=act_id)
        return self.paginate(comments)

    # 获取指定用户的指定活动的评论
    def get_user_comment(self, request, act_id, user_id):
        if Comment.objects.filter(user=user_id, act=act_id).exists():
            comment = Comment.objects.get(user=user_id, act=act_id)
            serializer = self.get_serializer(instance=comment)
            return Response(serializer.data)
        return Response({"id": -1}, 404)

    def create_wrapper(self, request):
        res = self.create(request)
        act_id = int(request.data['act'])
        user_id = int(request.data['user'])
        comment = request.data['content']
        content = utils.get_notif_content(NOTIF.ActCommented, user_name=_user_id2user_name(user_id),
                                          act_name=_act_id2act_name(act_id), comment=comment)
        notif = new_notification(NOTIF.ActCommented, content, act_id=act_id)
        act = BUAA.models.Activity.objects.get(id=act_id)
        if act.block_id == BLOCKID.PERSONAL:
            _send_notif(act.owner.pk, notif)
        elif act.block_id != BLOCKID.BOYA:
            manegers = BUAA.models.OrgManager.objects.filter(org_id=act.org.pk).values('person')
            for m in manegers:
                _send_notif(m.id, notif)
        return res



# WebSocket实时通信
class SentNotifViewSet(ModelViewSet):
    queryset = SentNotif.objects.all()
    serializer_class = SentNotificationSerializer

    def read_notification(self, request, user_id):
        notifications = request.data.get("notifications")
        for notification in notifications:
            if SentNotif.objects.filter(notif=notification, person=user_id).exists():
                sent = SentNotif.objects.get(notif=notification, person=user_id)
                serializer = self.get_serializer(instance=sent, data={"notif": notification, "person": user_id, "already_read": True})
                serializer.is_valid()
                serializer.save()
        return Response(data=None, status=200)



class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer



class ImageUploadViewSet(ModelViewSet):
    parser_classes = [JSONParser, FormParser, MultiPartParser, ]
    serializer_class = ImageUploadSerializer
    def remove_act_avatar(self,request,act_id):
        try:
            act = Activity.objects.get(id=act_id)
        except:
            res = {
                "detail": '未找到活动'
            }
            status = 404
            return Response(res,status)
        
        act.avatar = None
        act.save()
        return Response(status=204)
    
    def upload_act_avatar(self,request,act_id):
        image = request.FILES['image']
        try:
            act = Activity.objects.get(id=act_id)
        except:
            res = {
                "detail": '未找到活动'
            }
            status = 404
            return Response(res,status)
        path = "acts/" + str(act_id) + '_' + get_random_str() + '.jpg'
        with open(base_dir + path,'wb') as f1:
            f1.write(image.read())
            f1.close()
            act.avatar = web_dir + path
            act.save()
        res = {
            "img" : web_dir + path
        }
        return Response(res,200)
    
    
    def upload_org_avatar(self, request, org_id):
        image = request.FILES['image']
        try:
            org = Organization.objects.get(id=org_id)
        except:
            res = {
                "detail": '未找到组织'
            }
            status = 404
            return Response(res,status)
        
        path = "orgs/" + str(org_id) + '_' + get_random_str() + '.jpg'
        with open(base_dir + path,'wb') as f:
            f.write(image.read())
            f.close()
            org.avatar = web_dir + path
            org.save()
        res = {
            "img" : web_dir + path
        }
        return Response(res,200)


if __name__=="__main__":
    print(get_access_token())
    