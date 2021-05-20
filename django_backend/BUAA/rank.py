import requests as rq
import os
import base64
import json

def base64_api(uname, pwd, img, typeid): # 参见 http://api.ttshitu.com/
    with open(img, 'rb') as f:
        base64_data = base64.b64encode(f.read())
        b64 = base64_data.decode()
    data = {"username": uname, "password": pwd,"typeid":typeid, "image": b64}
    result = json.loads(rq.post("http://api.ttshitu.com/predict", json=data).text)
    if result['success']:
        return result["data"]["result"]
    else:
        return result["message"]
    return ""

def verifycode(img_path):
    result = base64_api(uname='*****', pwd='*****', img=img_path,typeid = 3)
    return result.upper()

getImgVerifyCode=rq.get(
    url='http://www.myrct.cn/buaaoj/BUAAOJ/accounts/getImgVerifyCode'
)

f=open('verifycode.jpeg','wb')
f.write(getImgVerifyCode.content)
f.close()

imageVerCodeToken=getImgVerifyCode.headers['imageVerCodeToken']

login=rq.post(
    url='https://www.myrct.cn/buaaoj/BUAAOJ/accounts/login/1',
    json={
        "email" : "*******", #email
        "verifyCode" : verifycode('verifycode.jpeg'),
        "password" : "*******" #password
    },
    headers={
        "imagevercodetoken":imageVerCodeToken
    }
)

os.remove('verifycode.jpeg')

token=login.headers['token']
userid=login.json()['data']['userId']

getAllContestsOfCourse=rq.get(
    url='https://www.myrct.cn/buaaoj/BUAAOJ/contests/getAllContestsOfCourse/%i/%i'%(userid, 31),
    headers={
        'token':token
    }
)

print('练习列表：')
print(' ID     名称')
for i in getAllContestsOfCourse.json()['data']:
    print('%3i'%i['contestId'],'   ',i['contestName'])
contestid=int(input('选择练习ID：'))
for i in getAllContestsOfCourse.json()['data']:
    if i['contestId']==31:
        contestname=i['contestName']
        break

# %% 核心部分
import time
import pandas as pd
import re

matrix_rank = []
while True:
    try:
        CourseRank = rq.get(
            url='https://www.myrct.cn/buaaoj/BUAAOJ/contests/getContestPageRanks/100/0/{}'.format(contestid),
            headers={
                'token': token
            }
        )

        l_problem = ['Time']
        l_rank = []
        l_rank.append(time.ctime()[11: 19])
        for item in CourseRank.json()["data"]["tHead"]:
            if item["isPNum"]:
                l_problem.append(item["label"])
                l_rank.append(re.match(r'^([0-9]*)/', item["label2"]).group(0)[:-1])
        
        matrix_rank.append(l_rank)

        df = pd.DataFrame(matrix_rank, columns=l_problem)
        df.to_csv('/root/rank.csv', index=False)
        print('当前时间',time.ctime(),'已储存。')
        time.sleep(30)
    except:
        pass