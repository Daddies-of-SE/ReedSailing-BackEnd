from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.exceptions import ValidationError
from BUAA.models import *


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

class WXUserSerializer(ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = WXUser
        fields = "__all__"

    def update(self, instance, validated_data):
        """更新，instance为要更新的对象实例"""
        instance.openid = instance.openid
        instance.name = validated_data.get('name', instance.name)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.sign = validated_data.get('sign',instance.sign)
        instance.save()
        return instance

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

class OrganizationSerializer(ModelSerializer):
    """组织序列化器"""
    owner = WXUserSerializer()
    block = BlockSerializer()
    class Meta:
        model = Organization
        fields = ('name', 'description', 'create_time', 'avatar', 'owner', 'block')

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




class UserFeedbackSerializer(ModelSerializer):
    """用户反馈序列化器"""
    user = WXUserSerializer()

    class Meta:
        model = UserFeedback
        fields = ('content','pub_time','user')


class OrgApplySerializer(ModelSerializer):
    """组织申请序列化器"""
    # user = WXUserSerializer()
    # block = BlockSerializer()
    # 组织申请的时候肯定有组织有用户的

    class Meta:
        model = OrgApplication
        fields = "__all__"


class OrgAppDetialSerializer(ModelSerializer):
    class Meta:
        model = OrgApplication
        fields = "__all__"
        depth = 2


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


class OrgManagerSerializer(ModelSerializer):
    """组织管理员序列化器"""
    org = OrganizationSerializer()
    person = WXUserSerializer()
    class Meta:
        model = OrgManager
        fields = ('org','person')


class FollowedOrgSerializer(ModelSerializer):
    """关注组织序列化器"""
    org = OrganizationSerializer()
    person = WXUserSerializer()
    class Meta:
        model = FollowedOrg
        fields = ('org', 'person')

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
