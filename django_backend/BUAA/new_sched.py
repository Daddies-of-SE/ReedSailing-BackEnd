import requests
from django.core.cache import cache
import traceback
try:
    pass
    #import backend.settings as settings
except:
    print(traceback.format_exc())
import datetime
import json
import os
#from BUAA.serializers import *
#import BUAA.views
from serializers import *
from views import *
BOYA_PATH = os.path.expanduser('~/boya/')




def add_to_activities(name, description, contain, begin_time, end_time, location, **kwargs):
    if Address.objects.filter(name=location).exists():
        address = Address.objects.get(name=location).id
    else:
        serializer = AddressSerializer(
            data={"name": location, "longitude": 1.0, "latitude": 1.0})
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
    serializer = ActivitySerializer(data=data)
    serializer.is_valid()
    serializer.save()

    # send notif


if __name__ == "__main__":
    data = {
        "name" : 'boya_test',
        "begin_time" : str(datetime.datetime.now()),
        "end_time" : str(datetime.datetime.now()),
        "contain" : 100,
        "description" : str(datetime.datetime.now()),
        "owner" : 1,
        "block" : 2,
        "location" : 1,
    }
    add_to_activities(description='无' ,**data)
