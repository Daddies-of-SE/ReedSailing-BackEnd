from rest_framework import serializers
from BUAA.models import *


class UserLoginSerializer(serializers.ModelSerializer):
    """用户登录数据序列化器"""
    class Meta:
        model = WXUser
        fields = ['openid']

