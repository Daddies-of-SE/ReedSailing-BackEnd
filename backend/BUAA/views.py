from django.shortcuts import render
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponseRedirect,HttpResponse
from django.core.cache import caches
from BUAA.models import *
import json
import uuid
import hashlib
import backend.settings as settings
from django.core.cache import cache

def get_random_str():
    uuid_val = uuid.uuid4()
    uuid_str = str(uuid_val).encode("utf-8")
    md5 = hashlib.md5()
    md5.update(uuid_str)
    return md5.hexdigest()

def send_email(request):
    data = json.loads(request.body)
    email_address = data.get('email')
    random_str = get_random_str()[:6]
    email_from = settings.DEFAULT_FROM_EMAIL
    send_mail('BUAA Certification', 'Your verify code is{}'.format(random_str), email_from,
              [email_address], fail_silently=False)
    cache.set(random_str, email_address, 120)
    res = {
        'success': "true",
        'mess': 'Email send'
    }
    return HttpResponse(json.dumps(res), content_type='application/json')

def verify_email(request):
    data = json.loads(request.body)
    code = data.get('code')
    valid = cache.get(code)
    if valid:
        res = {
            'success': "true",
            'mess': 'Valid Code'
        }
    else:
        res = {
            'success': "false",
            'mess':'Invalid Code'
        }
    return HttpResponse(json.dumps(res), content_type='application/json')



