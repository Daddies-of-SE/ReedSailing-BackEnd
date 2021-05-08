import requests
from django.core.cache import cache
import backend.settings as settings
import datetime
from .serializers import *


def get_access_token():
    print(str(datetime.datetime.now()) + " get_access_token")
    response = requests.get(
        f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={settings.APPID}&secret={settings.SECRET}')
    response = response.json()
    if response.get('access_token', ''):
        cache.set('access_token', response['access_token'])
        cache.expire('access_token', response['expires_in'])


def get_boya():
    print(str(datetime.datetime.now()) + " get_boya")
    add_to_activities("test_boya", "test_description", 100, "2021-9-9T20:00:00", "2021-9-9T21:00:00", "test_address")



def add_to_activities(name, description, contain, begin_time, end_time, location):
    if Address.objects.filter(name=location).exists():
        address = Address.objects.get(name=location).id
    else:
        serializer = AddressSerializer(data={"name": location, "longitude": 1.0, "latitude": 1.0})
        serializer.is_valid()
        serializer.save()
        address = serializer.data.get("id")
    data = {
        "name": name,
        "begin_time": begin_time,
        "end_time": end_time,
        "contain": contain,
        "description": description,
        "owner": 1,
        "block": 2,
        "location": address,
    }
    print(data)
    serializer = OrganizationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
