import json
import requests

url = 'http://127.0.0.1:8000/login/'
s = json.dumps({'code': '1', 'userInfo': '222'})
r = requests.post(url, data=s, headers={"Content-Type": "application/json"})
print(r.content.decode())