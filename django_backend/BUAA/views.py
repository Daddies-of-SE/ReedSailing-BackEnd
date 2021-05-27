from __future__ import unicode_literals
import BUAA.models
import BUAA.utils as utils
import json
import uuid
import hashlib
import backend.settings as settings
from django.core.cache import cache
import requests
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import *
from rest_framework.response import Response
from rest_framework.viewsets import *
from rest_framework import status
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django_redis import get_redis_connection
from BUAA.authentication import *
import datetime
from BUAA.const import NOTIF, BLOCKID, NOTIF_TYPE_DICT
import time
import os
from BUAA.accessPolicy import *
import random
import traceback
from BUAA.recommend import update_kwd_typ, add_kwd_typ, delete_kwd_typ, get_keyword, get_recommend

base_dir = '/root/ReedSailing-Web/server_files/'
#base_dir = '/Users/wzk/Desktop/'
web_dir = 'https://www.reedsailing.xyz/server_files/'


sender = utils.MailSender()

def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()

# 仅供文件内部调用
def _create_notif_for_all(user_id_list, notif, add_receivers = None):
    """revoke when user keeps online"""
    user_id_list = [int(x) for x in user_id_list]
    if add_receivers is not None:
        add_receivers['__receivers__'] = user_id_list
    for p_id in user_id_list:
        p_id = int(p_id)
        if notif['type'] == NOTIF.NewBoya:
            sender.send_mail('【一苇以航】' + NOTIF_TYPE_DICT[notif['type']], notif['content'], _user_id2user_email(p_id))
        new_send_notification(notif['id'], p_id)

        # if p_id in clients :
        #     p_ws = clients[p_id]
        #     utils.push_all_notif(p_id, p_ws)

def _act_id2act_name(pk):
    pk = int(pk)
    return BUAA.models.Activity.objects.get(id=pk).name

def _org_id2org_name(pk):
    pk = int(pk)
    return BUAA.models.Organization.objects.get(id=pk).name

def _user_id2user_name(pk):
    pk = int(pk)
    return BUAA.models.WXUser.objects.get(id=pk).name

def _user_id2user_email(pk):
    pk = int(pk)
    return BUAA.models.WXUser.objects.get(id=pk).email


def send_new_boya_notf(data):
    """interface for external boya creating function"""
    content = utils.get_notif_content(NOTIF.NewBoya, act_name=data['name'])
    notif = new_notification(NOTIF.NewBoya, content, act_id=data['act'], org_id=None)
    followers = _get_boya_followers()
    receivers = [f.id for f in followers]
    _create_notif_for_all(receivers, notif)
    # return receivers

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


@api_view(['POST'])
def web_token_identify(request):
    token = request.data['token']
    username = cache.get(token)
    if not username:
        res = {'status': 0, 'name': ''}
    else:
        res = {'status': 1, 'name': username if len(username) <= 15 else "regular user"}
        cache.set(token, username, 24*60*60)
    return Response(res, 200)


@api_view(['POST'])
@authentication_classes([UserAuthentication, SuperAdminAuthentication, ErrorAuthentication])
def get_page_qrcode(request):
    body = {
        "path" : request.data["path"],
        "width" : request.data["width"],
    }
    r = requests.post(url="https://api.weixin.qq.com/cgi-bin/wxaapp/createwxaqrcode?access_token=" + utils.get_access_token(), data=json.dumps(body), headers={"Content-Type": "application/json"})
    
    path = "qrcode/" + get_random_str() + '.png'
    with open(base_dir + path, 'wb') as f:
            f.write(r.content)
    
    res = {
        "img" : web_dir + path
    }
    
    return Response(data=res, status=200)


def _get_boya_followers():
    return WXUser.objects.filter(follow_boya=True)


@api_view(['POST'])
@authentication_classes([UserAuthentication, ErrorAuthentication])
def send_email(request):
    try:
        email_address = request.data['email']
        if not email_address.endswith("@buaa.edu.cn"):
            res = {
                'status' : 1,
                'msg' : 'Email address not belong to BUAA'
            }
            return Response(data=res, status=400)
    
        random_str = get_random_str()[:6]
        sender.send_mail('ReedSailing Certification', 'Your verify code is {}, valid in 5 minutes.'.format(random_str),
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
    except:
        return Response({"errMsg" : traceback.format_exc()}, 400)
    # return my_response(res)


@api_view(['POST'])
@authentication_classes([UserAuthentication, ErrorAuthentication])
@permission_classes((OtherAccessPolicy,))
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
        "contact" : user.contact,
        "follow_boya" : user.follow_boya
    }
    return Response(data=res, status=200)
    

@api_view(['POST'])
@authentication_classes([])  # 用户认证
def user_register(request):
    # 取出数据
    try:
        id_ = request.data['id']
        user_info = request.data['userInfo']
        
        WXUser.objects.filter(id=id_).update(name=user_info.get("nickName"), avatar=user_info.get("avatarUrl"))
        
        # print("register user", WXUser.objects.get_or_create(id=id_))
    
        res = {
            "status": 0
        }
        return Response(data=res, status=200)
    except:
        return Response({"errMsg" : traceback.format_exc()}, 400)


@api_view(['POST'])
@authentication_classes([UserAuthentication, SuperAdminAuthentication, ErrorAuthentication])
@permission_classes((OtherAccessPolicy,))
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
@authentication_classes([UserAuthentication, SuperAdminAuthentication, ErrorAuthentication])
@permission_classes((OtherAccessPolicy,))
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
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (WXUserAccessPolicy,)

    queryset = WXUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return TestUserSerializer
        return WXUserSerializer

    def get_boya_followers(self, request):
        users = _get_boya_followers()
        serializer = self.get_serializer(users, many=True)

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

    def search_user(self,request):
        try:
            name = request.data.get("name")
            users = WXUser.objects.filter(name__contains=name)
        except:
            import traceback
            return Response({"errMsg":traceback.format_exc()},400)
        return self.paginate(users)


# 版块
class BlockViewSet(ModelViewSet):
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (BlockAccessPolicy,)
    queryset = Block.objects.all()
    serializer_class = BlockSerializer


# 组织申请
class OrgApplicationViewSet(ModelViewSet):
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (OrgAppAccessPolicy,)
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

            data = serializer.data
            _create_notif_for_all([owner_id], notif, data)

            return Response(data, 201)

        else:
            serializer = self.get_serializer(instance=application, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # notification
            content = utils.get_notif_content(NOTIF.OrgApplyRes, org_name=org_name, status=False)
            notif = new_notification(NOTIF.OrgApplyRes, content, org_id=None)
            data = serializer.data
            _create_notif_for_all([application.user.id], notif, data)

            return Response(data, 200)


# 组织
class OrganizationModelViewSet(ModelViewSet):
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (OrgAccessPolicy,)
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

        data = serializer.data
        _create_notif_for_all([request.data['owner']], notif, data)


        return Response(data, 200)

    # 推荐组织
#    def get_recommended_org(self, request, *args, **kwargs):
#        queryset = self.filter_queryset(self.get_queryset())
#        page = self.paginate_queryset(queryset)
#        if page is not None:
#            serializer = self.get_serializer(page, many=True)
#            return self.get_paginated_response(serializer.data)
#
#        serializer = self.get_serializer(queryset, many=True)
#        return Response(serializer.data)

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
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (FollowedOrgAccessPolicy,)
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
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (OrgManagerAccessPolicy,)
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

    def create_wrapper(self, request):
        res = self.create(request)
        user_id = request.data['person']
        org_id = request.data['org']
        content = utils.get_notif_content(NOTIF.BecomeAdmin, org_name=_org_id2org_name(org_id))
        notif = new_notification(NOTIF.BecomeAdmin, content, org_id=org_id)
        _create_notif_for_all([user_id], notif, res.data)

        return res

    def destroy(self, request, *args, **kwargs):
        user_id = request.query_params.get('user')
        org_id = request.query_params.get('org')
        OrgManager.objects.filter(org=org_id, person=user_id).delete()

        content = utils.get_notif_content(NOTIF.RemovalFromAdmin, org_name=_org_id2org_name(org_id))
        notif = new_notification(NOTIF.RemovalFromAdmin, content, org_id=org_id)
        data = {}
        _create_notif_for_all([user_id], notif, data)
        return Response(data, status=200)

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
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (CategoryAccessPolicy,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# 活动地址
class AddressViewSet(ModelViewSet):
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (AddressAccessPolicy,)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


# 用户反馈
class UserFeedbackViewSet(ModelViewSet):
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (FeedbackAccessPolicy,)
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer

    def get_serializer_class(self):
        if self.action == "search_all_feedback":
            return FeedbackDetailSerializer
        return UserFeedbackSerializer

    def search_all_feedback(self,request):
        content = request.data.get("content")
        feedbacks = UserFeedback.objects.filter(content__contains=content)
        serializer = self.get_serializer(feedbacks,many=True)
        return Response(serializer.data)

    def search_user_feedback(self,request,user_id):
        content = request.data.get("content")
        feedbacks = UserFeedback.objects.filter(content__contains=content,user=user_id)
        serializer = self.get_serializer(feedbacks,many=True)
        return Response(serializer.data)


# 活动
class ActivityViewSet(ModelViewSet):
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (ActAccessPolicy,)
    queryset = Activity.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "create_wrapper"]:
            return ActivitySerializer
        if self.action in ["destroy", "destroy_wrapper"]:
            return ActivitySerializer
        if self.action in ["update", "update_wrapper"]:
            return ActUpdateSerializer
        if self.action == 'get_recommended_act':
            return RecommendActSerializer
        return ActDetailSerializer

    def paginate(self, objects):
        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)


    def create_wrapper(self, request):
        try:
            res = self.create(request)
            
            act = Activity.objects.get(id=res.data['id'])
            act.keywords = get_keyword(act.name+' '+act.description)
            act.save()
            return res
        except:
            return Response({"errMsg" : traceback.format_exc()}, 400)

    # update_wrapper
    def update_wrapper(self, request, pk):
        pk = int(pk)
        res = self.update(request)

        act = Activity.objects.get(id=pk)
        old_keys = act.keywords 
        old_typ = act.type.name.lower() if act.type else None #TODO
        act.keywords = get_keyword(act.name+' '+act.description)
        new_keys = act.keywords
        act.save()
        
        # create notif
        content = utils.get_notif_content(NOTIF.ActContent, act_name=_act_id2act_name(pk))
        notif = new_notification(NOTIF.ActContent, content, act_id=pk, org_id=None)
        # send notification
        persons = JoinedAct.objects.filter(act=pk)
        for p in persons:
            update_kwd_typ(p.person_id, old_keys, new_keys) #TODO
        _create_notif_for_all([p.person_id for p in persons], notif, res.data)
        return res

    def destroy_wrapper(self, request, pk):
        try:
            pk = int(pk)
            #res = self.destroy(request)
            content = utils.get_notif_content(NOTIF.ActCancel, act_name=_act_id2act_name(pk))
            # notif = new_notification(NOTIF.ActCancel, content, act_id=pk, org_id=None)
            # Here we MUST set act_id to null, because the act will be deleted later.
            # If we don't set act_id to null, the related notification will be deleted under CASCADE model.
            notif = new_notification(NOTIF.ActCancel, content, act_id=None, org_id=None)
            persons = JoinedAct.objects.filter(act=pk)
            receivers = [p.person_id for p in persons]
            _create_notif_for_all(receivers, notif)
    
            act = Activity.objects.get(id=pk)
            kwds = act.keywords
            typ = act.type.name.lower() if act.type else None
            for id_ in receivers:
                delete_kwd_typ(id_, kwds, typ)
                
            res = self.destroy(request)
            res.status_code = 200
            if res.data is None:
                res.data = {}
            res.data['__receivers__'] = receivers
            return res
        except:
            return Response({"errMsg" : traceback.format_exc()}, 400)


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
        'cur': self.get_serializer(Activity.objects.filter(block = block_id, end_time__gte=now, begin_time__lte=now) , many=True).data,
        'end': self.get_serializer(Activity.objects.filter(block = block_id, end_time__lt=now), many=True).data
        }
        return Response(ret, 200)

    # 获取用户关注的组织发布的活动
    def get_followed_org_act(self, request, user_id):
        orgs = FollowedOrg.objects.filter(person=user_id)
        acts = Activity.objects.filter(org__in=[org.org_id for org in orgs]).order_by('pub_time').reverse()
        return self.paginate(acts)

    # 推荐活动
    def get_recommended_act(self, request, user_id):
        try:
            user = WXUser.objects.get(id=user_id)
            now = datetime.datetime.now()
            not_end_acts = list(Activity.objects.filter(end_time__gte=now))
            k = min(len(not_end_acts), 1000)
            random_acts = random.sample(not_end_acts, k)
            recommend_acts, recommend_orgs, act_su = get_recommend(user, random_acts)
            ret = {
                'acts' : self.get_serializer(recommend_acts, many=True).data,
                'orgs' : OrgDetailSerializer(recommend_orgs, many=True).data,
                #'act_suitability' : act_su
            }
        except:
            return Response({"errMsg": traceback.format_exc()}, 400)
        return Response(ret, 200)

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
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (JoinedActAccessPolicy,)
    queryset = JoinedAct.objects.all()

    def get_serializer_class(self):
        if self.action == "get_user_joined_act":
            return UserJoinedActSerializer
        if self.action == "get_user_joined_act_begin_order":
            return UserJoinedActSerializer
        if self.action == "get_user_joined_act_status":
            return UserJoinedActSerializer
        if self.action == "search_user_joined_act":
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
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            act_id = request.data.get("act")
            current_number = JoinedAct.objects.filter(act=act_id).count()
            act = Activity.objects.get(id=act_id)
            limit_number = act.contain
            kwds = act.keywords
            typ = act.type.name.lower() if act.type else None
            if current_number < limit_number:
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                user = request.data.get("person")
                add_kwd_typ(user, kwds, typ)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"detail": "活动人数已满。"}, 400)
        except:
            return Response({"errMsg" : traceback.format_exc()}, 400)
    
    # 退出活动
    def destroy(self, request, *args, **kwargs):
        user_id = request.query_params.get('person')
        act_id = request.query_params.get('act')
        JoinedAct.objects.filter(act=act_id, person=user_id).delete()
        act = Activity.objects.get(id=act_id)
        kwds = act.keywords
        typ = act.type.name.lower() if act.type else None
        delete_kwd_typ(user_id, kwds, typ)

    def destroy_wrapper(self, request) :
        user_id = request.query_params.get('person')
        act_id = request.query_params.get('act')
        operator_id = request.query_params.get('operator')
        
        data = {}
        #self.destroy(request)
        if operator_id != user_id:
            content = utils.get_notif_content(NOTIF.RemovalFromAct, act_name=_act_id2act_name(act_id))
            # content = utils.get_notif_content(NOTIF.RemovalFromAct, act_name=None)
            notif = new_notification(NOTIF.RemovalFromAct, content, act_id=act_id, org_id=None)
            _create_notif_for_all([user_id], notif, data)
        self.destroy(request)
            
        return Response(data, 200)

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
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (CommentAccessPolicy,)
    queryset = Comment.objects.all()

    def get_serializer_class(self):
        if self.action == "get_act_comments" or self.action == "search_by_act":
            return CommentDetailSerializer
        if self.action == "list":
            return CommentListSerializer
        if self.action == "get_user_comment":
            return CommentDetailSerializer
        if self.action == "update" or "update" in self.action:
            return CommentUpdateSerializer
        if self.action == "retrieve":
            return CommentUpdateSerializer
        if self.action == "search_all_comment":
            return CommentListSerializer
        if self.action == "search_by_user":
            return CommentActDetailSerializer

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

    def search_all_comment(self,request):
        content = request.data.get("query")
        comments = Comment.objects.filter(content__contains=content)
        return self.paginate(comments)

    def search_by_user(self,request,user_id):
        content = request.data.get("query")
        comments = Comment.objects.filter(user=user_id,content__contains=content)
        return self.paginate(comments)

    def search_by_act(self, request, act_id):
        content = request.data.get("query")
        comments = Comment.objects.filter(act=act_id,content__contains=content)
        return self.paginate(comments)

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
            _create_notif_for_all([act.owner.pk], notif, res.data)
        elif act.block_id == BLOCKID.BOYA:
            pass
        else:
            # manegers = BUAA.models.OrgManager.objects.filter(org_id=act.org.pk).values('person')
            # _create_notif_for_all([m['person'] for m in manegers], notif, res.data)
            _create_notif_for_all([act.owner.pk], notif, res.data)
        return res

    def update_wrapper(self, request, pk):
        res = self.update(request)
        comment_obj = BUAA.models.Comment.objects.get(id=pk)
        act_id = comment_obj.act.id
        user_id = comment_obj.user.id
        comment = request.data['content']
        content = utils.get_notif_content(NOTIF.ActCommentModified, user_name=_user_id2user_name(user_id),
                                          act_name=_act_id2act_name(act_id), comment=comment)
        notif = new_notification(NOTIF.ActCommentModified, content, act_id=act_id)
        act = BUAA.models.Activity.objects.get(id=act_id)
        if act.block_id == BLOCKID.PERSONAL:
            _create_notif_for_all([act.owner.pk], notif, res.data)
        elif act.block_id == BLOCKID.BOYA:
            pass
        else:
            # manegers = BUAA.models.OrgManager.objects.filter(org_id=act.org.pk).values('person')
            # _send_notif(m.id, notif)
            # m is dict which has key list ['person']
            # receivers = [m['person'] for m in manegers]
            # _create_notif_for_all(receivers, notif, res.data)
            _create_notif_for_all([act.owner.pk], notif, res.data)
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
    authentication_classes = [UserAuthentication, SuperAdminAuthentication, ErrorAuthentication]
    permission_classes = (ImageAccessPolicy,)
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


import pandas as pd
import numpy as np

from django.http import HttpResponse
from django.template import loader
import plotly.graph_objects as go
import plotly.offline as opy
import matplotlib.pyplot as plt

@api_view(['GET'])
def lines(request):
    template = loader.get_template('index.html')
    
    df = pd.read_csv('/root/rank.csv')
    
    x = df.Time.values
    col_num = df.shape[1]
    colors = plt.cm.Spectral(list(range(1, col_num))) # 👴 比较喜欢用的 colormap 之一，参见 matplotlib.pyplot.cm，matplotlib.colors，matplotlib.colormap
    fig = go.Figure() # 参见 plotly 文档
    fig.update_layout(
        title="《实时战况》", 
        xaxis={'title': '时间'}, 
        yaxis={'title': '通过人数', 'range': [0, 460]}
    )
    for i in range(1, col_num):
        y = df['{}'.format(i)].values
        
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                marker={'color': colors[i-1], 'symbol': 104, 'size': 10},
                mode="lines",
                name='Problem {}'.format(i)
            )
        )
        
    div = opy.plot(fig, auto_open=False, output_type='div')
    
    context = {}
    context['graph'] = div
    
    return HttpResponse(template.render(context, request))


if __name__=="__main__":
    print(utils.get_access_token())
    
    
    
    
