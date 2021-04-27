import requests
from django.core.cache import cache
import backend.settings as settings


def get_access_token():
    response = requests.get(
        f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={settings.APPID}&secret={settings.APPSECRET}')
    response = response.json()
    if response.get('access_token', ''):
        cache.set('access_token', response['access_token'])
        cache.expire('access_token', response['expires_in'])

