from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.exceptions import ValidationError
from BUAA.models import *
from rest_framework import exceptions
from django.utils import timezone


class UserLoginSerializer(ModelSerializer):
    """用户登录数据序列化器"""

    class Meta:
        model = WXUser
        fields = ['openid']


class UserVerifySerializer(ModelSerializer):
    """用户认证序列化器"""

    class Meta:
        model = WXUser
        fields = ['openid', 'email']


"""------------------------完成--------------------------"""


# 用户
class WXUserSerializer(ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = WXUser
        exclude = ['openid']
        read_only_fields = ['email']


class WXUserUpdateSerializer(ModelSerializer):
    class Meta:
        model = WXUser
        fields = ['name', 'sign']


# 版块
class BlockSerializer(ModelSerializer):
    """版块序列化器"""

    class Meta:
        model = Block
        fields = "__all__"

    def validate(self, attrs):
        name = attrs.get('name')
        if Block.objects.filter(name=name):
            raise ValidationError({'block': '板块名称重复'})
        return attrs


# 组织申请
class OrgApplySerializer(ModelSerializer):
    user = WXUserSerializer(read_only=True)

    class Meta:
        model = OrgApplication
        fields = "__all__"
        depth = 2


class OrgAppCreateSerializer(ModelSerializer):
    class Meta:
        model = OrgApplication
        fields = "__all__"
        read_only_fields = ['status']

    def validate_name(self, value):
        org_name = self.initial_data.get('name')
        exists = Organization.objects.filter(name=org_name).exists()
        if exists:
            raise ValidationError('已经存在该名称的组织。')
        exists = OrgApplication.objects.filter(name=org_name, status=0).exists()
        if exists:
            raise ValidationError('已经存在该名称组织的申请。')
        return value


class OrgAppVerifySerializer(ModelSerializer):
    class Meta:
        model = OrgApplication
        fields = ['status']

    def validated_status(self, value):
        status = self.initial_data.get('value')
        if not (status in [1, 2]):
            raise ValidationError('审批状态有误。')


# 组织
class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


class OrgDetailSerializer(ModelSerializer):
    owner = WXUserSerializer(read_only=True)

    class Meta:
        model = Organization
        fields = "__all__"
        depth = 2


class OrgOwnerSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ['owner']


# 关注组织
class FollowedOrgSerializer(ModelSerializer):

    class Meta:
        model = FollowedOrg
        fields = "__all__"

    def validate(self, value):
        org = self.initial_data.get('org')
        user = self.initial_data.get('person')
        exists = FollowedOrg.objects.filter(org=org, person=user).exists()
        if exists:
            raise ValidationError('已关注该组织。')
        return value


class UserFollowedOrgSerializer(ModelSerializer):
    org = OrgDetailSerializer(read_only=True)

    class Meta:
        model = FollowedOrg
        fields = ['org']
        depth = 2


# 组织管理
class OrgManagerSerializer(ModelSerializer):
    """组织管理员序列化器"""

    class Meta:
        model = OrgManager
        fields = "__all__"

    def validate(self, value):
        org = self.initial_data.get('org')
        user = self.initial_data.get('person')
        exists = OrgManager.objects.filter(org=org, person=user).exists()
        if exists:
            raise ValidationError({'detail': '该用户已是此组织管理员。'})
        return value


class UserManagedOrgSerializer(ModelSerializer):
    org = OrgDetailSerializer(read_only=True)

    class Meta:
        model = OrgManager
        fields = ['org']


class OrgAllManagersSerializer(ModelSerializer):
    person = WXUserSerializer(read_only=True)

    class Meta:
        model = OrgManager
        fields = ['person']
        depth = 2


# 超级管理员
class SuperUserSerializer(ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = ['username']


# 活动分类
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# 活动地址
class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

    # def validate(self, attrs):
    #     longitude = attrs.get('longitude')
    #     latitude = attrs.get('latitude')
    #     #if Address.objects.filter(longitude=longitude, latitude=latitude):
    #     #    raise ValidationError({'address': '地点重复。'})
    #     return attrs


# 用户反馈
class UserFeedbackSerializer(ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = "__all__"


# 活动
class ActivitySerializer(ModelSerializer):
    """活动序列化器"""

    class Meta:
        model = Activity
        fields = "__all__"

    def validate(self, attrs):
        org = attrs.get('org')
        if org is None:
            return attrs
        block = attrs.get('block')
        if org.block != block:
            raise ValidationError({'org/block': '组织与版块不匹配。'})
        begin_time = attrs.get('begin_time')
        end_time = attrs.get('end_time')
        if end_time < begin_time:
            raise ValidationError({'begin_time/end_time': '活动开始时间不应迟于结束时间。'})
        if begin_time < timezone.now():
            raise ValidationError({'begin_time': "活动开始时间不应早于当前时间。"})
        return attrs


class ActUpdateSerializer(ModelSerializer):
    class Meta:
        model = Activity
        fields = ("name", "begin_time", "end_time", "contain", "description", "type", "location")


class ActDetailSerializer(ModelSerializer):
    owner = WXUserSerializer(read_only=True)

    class Meta:
        model = Activity
        fields = "__all__"
        depth = 1


# 活动参与
class JoinedActSerializer(ModelSerializer):

    class Meta:
        model = JoinedAct
        fields = "__all__"

    def validate(self, value):
        act = self.initial_data.get('act')
        user = self.initial_data.get('person')
        exists = self.Meta.model.objects.filter(act=act, person=user).exists()
        if exists:
            raise ValidationError({'detail': '不可重复加入活动。'})
        return value


class JoinedActDetailSerializer(ModelSerializer):
    person = WXUserSerializer(read_only=True)

    class Meta:
        model = JoinedAct
        fields = "__all__"
        depth = 1


class UserJoinedActSerializer(ModelSerializer):
    class Meta:
        model = JoinedAct
        fields = ['act']
        depth = 1


class JoinedActParticipants(ModelSerializer):
    class Meta:
        model = JoinedAct
        fields = ['person']
        depth = 1


# 活动评价
class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class CommentDetailSerializer(ModelSerializer):
    user = WXUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"


class CommentUpdateSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'score']


class CommentListSerializer(ModelSerializer):
    user = WXUserSerializer(read_only=True)
    act = ActivitySerializer(read_only=True)

    class Meta:
        model = Comment
        fields = "__all__"


"""--------------------------未完成------------------------------"""





class ManagerApplicationSerializer(ModelSerializer):
    org = OrgManagerSerializer()
    user = WXUserSerializer()

    class Meta:
        model = ManagerApplication
        fields = ('org', 'user', 'content', 'pub_time')


# 加入活动申请
class JoinActApplicationSerializer(ModelSerializer):
    class Meta:
        model = JoinActApplication
        fields = "__all__"


# test
class TestUserSerializer(ModelSerializer):
    class Meta:
        model = WXUser
        fields = "__all__"
