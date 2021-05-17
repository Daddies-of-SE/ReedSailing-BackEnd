import json
import requests

#url = 'http://127.0.0.1:8000/login/'
#s = json.dumps({'code': '1', 'userInfo': '222'})
#r = requests.post(url, data=s, headers={"Content-Type": "application/json"})
#print(r.content.decode())

import os
import time

def get_access_token():
	def get_from_wx_api():
		appid = 'wx6e4e33e0b6db916e'
		secret = 'fc9689a2497195707d9f85e48628b351'
		url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + secret
		response = json.loads(requests.get(url).content)
		with open("./access_token.txt", "w") as f:
			print(response["access_token"], file=f)
			print(time.time(), file=f)
			print(response["expires_in"], file=f)
		return response["access_token"]
	
	if not os.path.exists("./access_token.txt"):
		return get_from_wx_api()
	
	with open("./access_token.txt") as f:
		lines = f.readlines()
		if time.time() - float(lines[1].strip()) > float(lines[2].strip()):
			return get_from_wx_api()
		return lines[0].strip()


body = {
	"path" : "pages/sections/act-list/act-list?orgId=1",
	"width" : 430,
}
#print(get_access_token())
r = requests.post(url="https://api.weixin.qq.com/cgi-bin/wxaapp/createwxaqrcode?access_token=" + get_access_token(), data=json.dumps(body), headers={"Content-Type": "application/json"})
#r = json.loads(r.content, encoding="gbk")
#print(str(r.content))

#import uuid
#import hashlib
#
#def get_random_str():
#	uuid_val = uuid.uuid4()
#	uuid_str = str(uuid_val).encode("utf-8")
#	md5 = hashlib.md5()
#	md5.update(uuid_str)
#	return md5.hexdigest()
#print(get_random_str())

with open('/root/ReedSailing-Web/server_files/1.png', 'wb') as f:
		f.write(r.content)
