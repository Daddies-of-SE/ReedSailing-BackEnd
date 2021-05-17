from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from django.core.cache import cache
from .serializers import *


class UserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization = request.META.get('HTTP_AUTHORIZATION')
        if not authorization:
            return None
        token = authorization.split()[1]
        if not token:
            return None
        openid = cache.get(token)
        if not openid:
            raise exceptions.AuthenticationFailed('非法token')
        user = WXUser.objects.get(openid=openid)
        return user, None

    def authenticate_header(self, request):
        return '缺少token。'


class SuperAdminAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_TOKEN')
        if not token:
            return None
        username = cache.get(token)
        if not username:
            raise exceptions.AuthenticationFailed('非法token')
        user = SuperAdmin.objects.get(username=username)
        return user, None

    def authenticate_header(self, request):
        return '缺少token。'


