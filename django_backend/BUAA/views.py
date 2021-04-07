from django.shortcuts import render
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponseRedirect,HttpResponse
from django.core.cache import caches
from BUAA.models import *
from BUAA import utils
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

    sender=utils.MailSender()
    
    print("request is", request.POST)

    email_address = request.POST.get('email')

    #data = json.loads(request.body)
    #email_address = data.get('email')
    random_str = get_random_str()[:6]
    sender.send_mail('BUAA Certification', 'Your verify code is {}, valid in 2 minutes'.format(random_str), email_address)

    # TODO: a bug says 'table buaa.my_cache_table does not exist'
    cache.set(random_str, email_address, 120)

    res = {
        'success': "true",
        'mess': 'Email send'
    }
    print("successfully send email to", email_address)
    return HttpResponse(json.dumps(res), content_type='application/json')

def verify_email(request):
    code = request.POST.get('code')
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



