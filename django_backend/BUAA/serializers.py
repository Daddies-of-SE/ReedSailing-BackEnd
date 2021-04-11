from rest_framework import serializers
from BUAA.models import *


class UserLoginSerializer(serializers.ModelSerializer):
    """用户登录数据序列化器"""
    class Meta:
        model = WXUser
        fields = ['openid']


class UserVerifySerializer(serializers.ModelSerializer):
    """用户认证序列化器"""
    class Meta:
        model = WXUser
        fields = ['openid', 'email']


class OrganizationSerializer(serializers.ModelSerializer):
    """组织序列化器"""
    class Meta:
        model = Organization
        fields = '__all__'


class WXUserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = WXUser
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    class Meta:
        model = Category
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    """地址序列化器"""
    class Meta:
        model = Address
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    class Meta:
        model = Comment
        fields = "__all__"


class BlockSerializer(serializers.ModelSerializer):
    """版块序列化器"""
    class Meta:
        model = Block
        fields = "__all__"


class UserFeedbackSerializer(serializers.ModelSerializer):
    """用户反馈序列化器"""
    class Meta:
        model = UserFeedback
        fields = "__all__"


class OrgApplySerializer(serializers.ModelSerializer):
    """组织申请序列化器"""
    class Meta:
        model = OrgApplication
        fields = "__all__"


class ActivitySerializer(serializers.ModelSerializer):
    """活动序列化器"""
    class Meta:
        model = Activity
        fields = "__all__"


class OrgManagerSerializer(serializers.ModelSerializer):
    """组织管理员序列化器"""
    class Meta:
        model = OrgManager
        fields = "__all__"


class FollowedOrgSerializer(serializers.ModelSerializer):
    """关注组织序列化器"""
    class Meta:
        model = FollowedOrg
        fields = "__all__"


class JoinActApplicationSerializer(serializers.ModelSerializer):
    """活动加入申请序列化器"""
    class Meta:
        model = JoinActApplication
        fields = "__all__"


class JoinedActSerializer(serializers.ModelSerializer):
    """已加入活动序列化器"""
    class Meta:
        model = JoinedAct
        fields = "__all__"
