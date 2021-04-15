from rest_framework.decorators import api_view, authentication_classes
# from django_redis import get_redis_connection
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import *
import json
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render, redirect
from django.contrib import auth
from .models import *

class SuperUserViewSet(ModelViewSet):
    queryset = SuperAdmin.objects.all()
    serializers_class = SuperUserSerializer

def register(request):
    data = json.loads(request.body)
    name = data.get('username')
    passwd1 = data.get('password')
    email = data.get('email')
    name_exist = SuperAdmin.objects.filter(username=name)
    if name_exist:
        res = {
            'success': "false",
            'mess': 'Name exist'
        }
        return HttpResponse(json.dumps(res), content_type='application/json')
    else:
        exist = SuperAdmin.objects.filter(email=email)
        if exist:
            res = {
                'success': "false",
                'mess': 'Email exist'
            }
            return HttpResponse(json.dumps(res), content_type='application/json')
        else:
            SuperAdmin.objects.create_user(username=name, email=email, password=passwd1)
            res = {
                'success': "true",
            }
            return HttpResponse(json.dumps(res), content_type='application/json')


def login(request):
    data = json.loads(request.body)
    name = data.get('username')
    passwd = data.get('password')
    user = auth.authenticate(username=name, password=passwd)
    if user is None:
        res = {
            'success': 'false',
            'mess': 'Invalid User'

        }
        return HttpResponse(json.dumps(res), content_type='application/json')
    auth.login(request, user)
    ser = SuperUserSerializer(user)
    res = {
        'success': 'true',
        'user': ser.data,
    }
    return HttpResponse(json.dumps(res), content_type='application/json')