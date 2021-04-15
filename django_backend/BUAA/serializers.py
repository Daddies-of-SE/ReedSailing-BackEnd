from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.exceptions import ValidationError
from BUAA.models import *
from rest_framework import exceptions


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


class CategorySerializer(ModelSerializer):
    """分类序列化器"""
    class Meta:
        model = Category
        fields = "__all__"
    def validate(self, attrs):
        name = attrs.get('name')
        if Category.objects.filter(name=name):
            raise ValidationError({'category': '名字重复'})
        return attrs


class AddressSerializer(ModelSerializer):
    """地址序列化器"""
    class Meta:
        model = Address
        fields = "__all__"

    def validate(self, attrs):
        name = attrs.get('name')
        longitude = attrs.get('longitude')
        latitude = attrs.get('latitude')
        if Address.objects.filter(name=name):
            raise ValidationError({'address': '地点名称重复'})
        if Address.objects.filter(longitude=longitude,latitude=latitude):
            raise ValidationError({'address': '地点重复'})
        return attrs










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
            raise ValidationError('该用户已是此组织管理员。')
        return value


class UserManagedOrgSerializer(ModelSerializer):
    class Meta:
        model = OrgManager
        fields = ['org']
        depth = 2


class OrgAllManagersSerializer(ModelSerializer):
    class Meta:
        model = OrgManager
        fields = ['person']
        depth = 2
















"""--------------------------未完成------------------------------"""



class UserFeedbackSerializer(ModelSerializer):
    """用户反馈序列化器"""
    user = WXUserSerializer()

    class Meta:
        model = UserFeedback
        fields = ('content','pub_time','user')


class ActivitySerializer(ModelSerializer):
    """活动序列化器"""
    owner = WXUserSerializer()
    type = CategorySerializer()
    org = OrganizationSerializer()
    location = AddressSerializer()
    class Meta:
        model = Activity
        fields = ('name','begin_time','end_time','pub_time','contain',
                  'description','review','owner','type','org','location')







class CommentSerializer(ModelSerializer):
    """评论序列化器"""
    act = ActivitySerializer()
    user = WXUserSerializer()
    class Meta:
        model = Comment
        fields = ('content','pub_time','score','act','user')


class JoinActApplicationSerializer(ModelSerializer):
    """活动加入申请序列化器"""
    act = ActivitySerializer()
    user = WXUserSerializer()
    class Meta:
        model = JoinActApplication
        fields = ('act', 'user')


class JoinedActSerializer(ModelSerializer):
    """已加入活动序列化器"""
    act = ActivitySerializer()
    person = WXUserSerializer()
    class Meta:
        model = JoinedAct
        fields = ('act', 'person')


class ManagerApplicationSerializer(ModelSerializer):
    org = OrgManagerSerializer()
    user = WXUserSerializer()
    class Meta:
        model = ManagerApplication
        fields = ('org', 'user', 'content', 'pub_time')



# test
class TestUserSerializer(ModelSerializer):
    class Meta:
        model = WXUser
        fields = "__all__"