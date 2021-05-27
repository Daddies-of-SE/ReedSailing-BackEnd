import random
import os
import json
import jieba.analyse
import math
import sys
from functools import cmp_to_key
from BUAA.models import *

MAX_ACCEPT = 100
ACCEPT_THRESH = 0
WEIGHT_HEAT = 3
WEIGHT_TYPE = 2
WEIGHT_KEYWORD = 10


if sys.platform in ["win32", "win64", "darwin"]:
    portrait_dir = './portraits/'
elif sys.platform in ['linux']:
    portrait_dir = '/root/portraits/'
else:
    portrait_dir = '/root/portraits/'

if not os.path.exists(portrait_dir):
    os.mkdir(portrait_dir)


def get_portrait_path(id_):
    path = portrait_dir+str(id_)+".json"
    if not os.path.exists(path):
        with open(path, "w") as f:
            init = {
                'type': {},
                'keyword': {}
            }
            json.dump(init, f)
    return path


def load_portrait(id_):
    with open(get_portrait_path(id_), 'r') as f:
        port = json.load(f)
    return port


def save_portrait(id_, port):
    with open(get_portrait_path(id_), 'w') as f:
        json.dump(port, f)


def portrait_add_keyword(port, kwds):
    d = port['keyword']
    if kwds:
        kwds = kwds.split(' ')
        for kwd in kwds:
            if not d.get(kwd):
                d[kwd] = 1
            else:
                d[kwd] += 1


def portrait_add_type(port, typ):
    d = port['type']
    if typ:
        if not d.get(typ):
            d[typ] = 1
        else:
            d[typ] += 1


def portrait_del_keyword(port, kwds):
    d = port['keyword']
    if kwds:
        kwds = kwds.split(' ')
        for kwd in kwds:
            if d.get(kwd, 0) > 0:
                d[kwd] -= 1


def portrait_del_type(port, typ):
    d = port['type']
    if typ:
        if d.get(typ, 0) > 0:
            d[typ] -= 1


def update_kwd_typ(id_, old_kwds, new_kwds, old_typ, new_typ):
    port = load_portrait(id_)
    portrait_del_keyword(port, old_kwds)
    portrait_del_type(port, old_typ)
    portrait_add_keyword(port, new_kwds)
    portrait_add_type(port, new_typ)
    save_portrait(id_, port)


def delete_kwd_typ(id_, kwds, typ):
    port = load_portrait(id_)
    portrait_del_keyword(port, kwds)
    portrait_del_type(port, typ)
    save_portrait(id_, port)


def add_kwd_typ(id_, kwds, typ):
    port = load_portrait(id_)
    portrait_add_keyword(port, kwds)
    portrait_add_type(port, typ)
    save_portrait(id_, port)


def get_keyword(text):
    K = min(5, math.floor(len(text)/20))
    kwds = jieba.analyse.extract_tags(text, topK=K)
    kwds = set(map(lambda x: x.lower(), kwds))
    return ' '.join(kwds)


def cal_suitability(act, user_pic):
    # todo
    suit = 0
    kwds = act.keywords
    typ = act.type.name.lower() if act.type else None
    if typ:
        type_dict = user_pic['type']
        suit += type_dict.get(typ, 0)*WEIGHT_TYPE
    if kwds:
        kwds = kwds.split()
        kwd_dict = user_pic['keyword']
        for kwd in kwds:
            suit += kwd_dict.get(kwd, 0)*WEIGHT_KEYWORD
    return suit


def get_heat(act):
    number = max(JoinedAct.objects.filter(act=act.id).count(), 1)
    comments = Comment.objects.filter(act=act.id, score__gt=0)
    total_score = 0
    for comment in comments:
        total_score += comment.score
    avg_score = total_score/len(comments) if comments else 0
    print(number, avg_score)
    return math.log(number)*math.exp(avg_score)


def act_cmp(a, b):
    if a.suitability > b.suitability:
        return -1
    if a.suitability < b.suitability:
        return 1
    if a.name < b.name:
        return -1
    if a.name > b.name:
        return 1
    return 0


def get_accept_list(act_list, user):
    user_pic = load_portrait(user.id) if user.email else None
    accept_list = []
    accept_cnt = 0
    for act in act_list:
        suitability = get_heat(act)
        if user_pic:
            suitability += cal_suitability(act, user_pic)
        if suitability >= ACCEPT_THRESH:
            setattr(act, 'suitability', suitability)
            accept_cnt += 1
            accept_list.append(act)
            if accept_cnt > MAX_ACCEPT:
                break
    accept_list.sort(key=cmp_to_key(act_cmp))
    return accept_list


def take_count(elem):
    return elem.count


def group_cmp(a, b):
    if a.count > b.count:
        return -1
    if a.count < b.count:
        return 1
    if a.name < b.name:
        return -1
    if a.name > b.name:
        return 1
    return 0


def getgroup(accept_list):
    group_cnt = {}
    for act in accept_list:
        if act.org:
            # exclude activities from boya and individual block
            org_id = act.org.id
            if org_id not in group_cnt:
                setattr(act.org, 'count', 1)
                group_cnt[org_id] = act.org
            else:
                group_cnt[org_id].count += 1
    groups = list(group_cnt.values())
    groups.sort(key=cmp_to_key(group_cmp))
    return groups


def get_recommend(user, init_list):
    assert isinstance(user.id, int)
    act_list = get_accept_list(init_list, user)
    group_list = getgroup(act_list)
    return act_list, group_list
