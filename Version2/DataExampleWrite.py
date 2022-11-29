# _*_ coding:utf-8 _*_
# Project: 
# FileName: DataExampleWrite.py
# UserName: 高俊佶
# ComputerUser：19305
# Day: 2020/4/23
# Time: 15:03
# IDE: PyCharm
# 最爱洪洪，永无BUG！

import os
import json
import random


def encryption(u: str, p: str):
    random.seed(p)
    p = ""
    for nums in u:
        p += chr(ord(nums) ^ random.randint(0, 255))
    return p


cts_path = os.getcwd() + r'\Data\Example\client-to-server.json'
stc_path = os.getcwd() + r'\Data\Example\server-to-client.json'
user_path = os.getcwd() + r'\Data\Example\users.json'
group_path = os.getcwd() + r'\Data\Example\groups.json'
set_user_path = os.getcwd() + r'\Data\users.json'
set_group_path = os.getcwd() + r'\Data\groups.json'

cts = {
    'type': ['add', 'delete', 'rename', 'move',  'normal', 'login', 'state', 'group'],
    'data': 'num/text',
    'status': ['send', 'wait', 'success', 'failed']
}

stc = {
    'type': ['add', 'delete', 'normal', 'login', 'logout', 'registry', 'friends', 'online'],
    'data': 'num/text',
    'status': ['wait', 'success', 'failed']
}

user = {
    'num1': {
        'type': ['admin', 'user'],
        'password': '******',
        'friends': {
            '好友列表': {
                '我的好友': ['num2', 'num3'],
            }
        }
    }
}

group = {
    'num1': {
        'maker': 'person',
        'auto': True,  # 自动通过进群请求
        'users': ['num2', 'num3'],
        'notices': ['num4', 'num5']  # 询问是否允许进群
    }
}

users = {
    '666666': {
        'type': 'admin',
        'password': encryption('666666', 'Gjj666666'),
        'friends': {
            '好友列表': {
                '我的好友': ['1930502098', '2832561754', '2717057684'],
                '特别': ['1332848443', '1696085768', '1835609982'],
                '真实好友': [],
            },
            '群组列表': {
                '我的群聊': ['645289967', '864663886'],
                '个人群': ['536640287', '415107147'],
            }
        }
    }
}

groups = {
    '536640287': {
        'maker': '666666',
        'auto': False,
        'users': ['666666', '1930502098', '2832561754', '2717057684', '1332848443', '1696085768', '1835609982'],
        'notices': ['1598359293', '35386550']
    }
}

open(cts_path, 'w', encoding='utf-8').write(json.dumps(cts, indent=4, ensure_ascii=False))
open(stc_path, 'w', encoding='utf-8').write(json.dumps(stc, indent=4, ensure_ascii=False))
open(user_path, 'w', encoding='utf-8').write(json.dumps(user, indent=4, ensure_ascii=False))
open(group_path, 'w', encoding='utf-8').write(json.dumps(group, indent=4, ensure_ascii=False))
# open(set_user_path, 'w', encoding='utf-8').write(json.dumps(users, indent=4, ensure_ascii=False))
open(set_group_path, 'w', encoding='utf-8').write(json.dumps(groups, indent=4, ensure_ascii=False))

# ADD
data_example1 = {
    'type': 'friend',  # group/groups
    'from': '1',
    'to': '3',
    'msg': '我是1，请求加你为好友。'
}

# ADD_SUCCESS
data_example2 = {
    'type': 'friend',  # group/groups
    'from': '3',
    'to': '1',
    'msg': '（成功的备注，时间等）'
}

# ADD_FAILED
data_example3 = {
    'type': 'friend',  # group/groups
    'from': '1',
    'to': '3',
    'msg': '（失败的备注，时间、原因等）'
}

# DELETE
data_example4 = {
    'type': 'friend',  # group/groups
    'from': '3',
    'to': '1',
    'msg': '（删除的备注，时间等）'
}

# NORMAL
data_example5 = {
    'type': 'friend',  # groups
    'from': '1',
    'to': '3',
    'msg': '你好，我是1'
}

# LOGIN
data_example6 = {
    'from': '2',
    'to': 'server',
    'msg': '（上线的备注，时间等）'
}

# LOGOUT
data_example7 = {
    'from': '2',
    'to': 'server',
    'msg': '（下线的备注，时间等）'
}

# STATE
data_example8 = {
    '在线'  # 隐身/强聊
}

# FRIENDS
data_example9 = {
    '好友列表': {
        '我的好友': ['1930502098', '2832561754', '2717057684'],
        '特别': ['1332848443', '1696085768', '1835609982'],
    },
    '群组列表': {
        '我的群聊': ['645289967', '864663886'],
        '个人群': ['536640287', '415107147'],
    }
}

# ONLINE
data_example10 = {
    'online': ['1', '3']
}
