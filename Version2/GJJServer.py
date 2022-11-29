# _*_ coding:utf-8 _*_
# FileName: GJJServer.py
# IDE: PyCharm

import re
import json
import time
import socket
import threading
import selectors
from Message import Message


class Server(object):

    m = Message()

    def __init__(self, ip: str = '127.0.0.1', port: int = 21567, listen: int = 100, dns: str = '8.8.8.8'):
        self.s = self.m.socket_socket
        self.dns = dns
        self.port = port
        self.start = False
        self.objects = []
        self.ip = self.get_host_ip() or ip
        self.s.bind((self.ip, port))
        self.s.listen(listen)
        self.Selectors = selectors.DefaultSelector()
        self.thread(self.connect)
        self.thread(self.receive)
        self.broadcast()

    def broadcast(self):
        # 广播自身
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg = f'This is GJJServer .{self.port}'
        while 1:
            try:
                s.sendto(msg.encode(), ('<broadcast>', 21678))
                time.sleep(1)
            except TypeError:
                print('广播发送失败，请稍后重启服务端！')
                break

    def connect(self):
        # 建立新的连接
        while 1:
            receive, _ = self.s.accept()
            if receive:
                self.Selectors.register(receive, selectors.EVENT_READ)
                self.start = True
                m = Message()
                m.raddr = str(_)
                m.connect = True
                m.socket_socket = receive
                self.objects.append(m)
                self.thread(self.handle, m)
            time.sleep(1)

    def receive(self):
        # 接收新的消息
        while 1:
            while self.start:
                try:
                    receive = self.Selectors.select(timeout=1)
                    for r, _ in receive:
                        address = re.search(r"raddr=(\(.*\))", str(r.fileobj)).group(1)
                        objects = self.objects
                        for o in objects:
                            if o.raddr == address or o.socket_socket == r:
                                try:
                                    msg = r.fileobj.recv(1024)
                                    if msg:
                                        o.messages.put(eval(msg.decode('GB18030')))
                                    else:
                                        self.Selectors.unregister(r.fileobj)
                                        try:
                                            self.m.online.remove(o.user)
                                            self.objects.remove(o)
                                        except ValueError:
                                            pass
                                        finally:
                                            print(f'{address}：对方已下线！')
                                            self.online()
                                            time.sleep(1)
                                except ConnectionResetError:
                                    self.Selectors.unregister(r.fileobj)
                                    try:
                                        self.m.online.remove(o.user)
                                        self.objects.remove(o)
                                    except ValueError:
                                        pass
                                    finally:
                                        print(f'{address}：对方已下线！')
                                        self.online()
                                        time.sleep(1)
                except OSError:
                    time.sleep(1)
            time.sleep(1)

    def handle(self, m: Message):
        # 处理每个客户端发来消息的函数
        while m.connect:
            while m.messages.qsize():
                msg = m.messages.get()
                print(msg)
                send_msg = {
                    'type': '',
                    'data': '',
                    'status': ''
                }
                if msg['type'] == 'login':
                    send_msg['type'] = 'login'
                    success = True
                    if msg['data']['user'] in j:
                        if msg['data']['password'] == j[msg['data']['user']]['password']:
                            m.user = msg['data']['user']
                            m.friends = j[msg['data']['user']]['friends']
                            send_msg['data'] = {
                                'online': self.m.online,
                                'friends': j[msg['data']['user']]['friends']
                            }
                            send_msg['status'] = 'success'
                            if m.user in self.m.online:
                                send_msg['data'] = '该账号已被登录，目前版本禁止强登，请稍后再试！'
                                send_msg['status'] = 'failed'
                                success = False
                            else:
                                self.m.online.append(m.user)
                        else:
                            send_msg['data'] = '密码错误'
                            send_msg['status'] = 'failed'
                            success = False
                    else:
                        send_msg['type'] = 'registry'
                        send_msg['data'] = {
                            'online': self.m.online,
                            'friends': {
                                "好友列表": {
                                    "我的好友": []
                                },
                                "群组列表": {
                                    "我的群聊": []
                                }
                            }
                        }
                        send_msg['status'] = 'success'
                        j[msg['data']['user']] = {
                            'type': 'user',
                            'password': msg['data']['password'],
                            'friends': send_msg['data']['friends']
                        }
                        m.user = msg['data']['user']
                        m.friends = j[msg['data']['user']]['friends']
                        self.m.online.append(m.user)
                    m.socket_socket.send(str(send_msg).encode('GB18030'))
                    time.sleep(1)
                    if success:
                        self.online()
                elif msg['type'] == 'normal':
                    send_msg['type'] = 'normal'
                    if msg['data']['type'] == 'friend':
                        flag = True
                        for obj in self.objects:
                            if obj.user == msg['data']['to']:
                                send_msg['data'] = msg['data']
                                send_msg['status'] = 'success'
                                obj.socket_socket.send(str(send_msg).encode('GB18030'))
                                flag = False
                                break
                        if flag:
                            send_msg['data'] = f"您的好友 {msg['data']['to']} 未在线，消息发送失败~"
                            send_msg['status'] = 'failed'
                            m.socket_socket.send(str(send_msg).encode('GB18030'))
                    elif msg['data']['type'] == 'groups':
                        pass
                elif msg['type'] == 'add':
                    send_msg['type'] = 'add'
                    if msg['data']['type'] == 'friend':
                        if msg['status'] == 'send':
                            send_msg['status'] = 'wait'
                            flag = True
                            for obj in self.objects:
                                if obj.user == msg['data']['to']:
                                    send_msg['data'] = msg['data']
                                    obj.socket_socket.send(str(send_msg).encode('GB18030'))
                                    time.sleep(1)
                                    send_msg['data'] = '消息已送达，请等待对方接收。'
                                    m.socket_socket.send(str(send_msg).encode('GB18030'))
                                    flag = False
                                    break
                            if flag:
                                send_msg['data'] = f"用户 {msg['data']['to']} 暂时不在线，请稍后再试！"
                                if msg['data']['to'] not in j:
                                    send_msg['data'] = f"未找到用户 {msg['data']['to']} ！"
                                send_msg['status'] = 'failed'
                            m.socket_socket.send(str(send_msg).encode('GB18030'))
                        elif msg['status'] == 'success':
                            send_msg['status'] = 'success'
                            send_msg['data'] = f"用户 {msg['data']['to']} 通过了你的好友申请！"
                            j[msg['data']['from']]['friends']['好友列表'][msg['data']['msg']].append(msg['data']['to'])
                            j[msg['data']['to']]['friends']['好友列表']['我的好友'].append(msg['data']['from'])
                            for obj in self.objects:
                                if obj.user == msg['data']['from']:
                                    obj.socket_socket.send(str(send_msg).encode('GB18030'))
                                    time.sleep(1)
                                    send_msg['type'] = 'friends'
                                    send_msg['data'] = {
                                        'friends': j[msg['data']['from']]['friends']
                                    }
                                    obj.socket_socket.send(str(send_msg).encode('GB18030'))
                        elif msg['status'] == 'failed':
                            send_msg['status'] = 'failed'
                            send_msg['data'] = f"用户 {msg['data']['to']} 拒绝了你的好友申请！"
                            for obj in self.objects:
                                if obj.user == msg['data']['from']:
                                    obj.socket_socket.send(str(send_msg).encode('GB18030'))
                    elif msg['data']['type'] == 'group':
                        send_msg['status'] = 'success'
                        j[m.user]['friends'] = msg['data']['msg']
                    elif msg['data']['type'] == 'groups':
                        send_msg['status'] = 'failed'
                        send_msg['data'] = '群功能暂时未开放！'
                elif msg['type'] == 'delete':
                    if msg['data']['type'] == 'friend':
                        if msg['status'] == 'send':
                            send_msg['status'] = 'success'
                            for i in j[msg['data']['from']]['friends']['好友列表']:
                                for ii in j[msg['data']['from']]['friends']['好友列表'][i]:
                                    if ii == msg['data']['to']:
                                        j[msg['data']['from']]['friends']['好友列表'][i].remove(ii)
                                        break
                            for i in j[msg['data']['to']]['friends']['好友列表']:
                                for ii in j[msg['data']['to']]['friends']['好友列表'][i]:
                                    if ii == msg['data']['from']:
                                        j[msg['data']['to']]['friends']['好友列表'][i].remove(ii)
                                        break
                            for obj in self.objects:
                                if obj.user == msg['data']['to']:
                                    send_msg['type'] = 'delete'
                                    send_msg['status'] = 'failed'
                                    send_msg['data'] = f"您的好友 {msg['data']['to']} 已将您删除！"
                                    obj.socket_socket.send(str(send_msg).encode('GB18030'))
                                    time.sleep(1)
                                    send_msg['status'] = 'success'
                                    send_msg['data'] = '消息已送达，请等待对方接收。'
                                    m.socket_socket.send(str(send_msg).encode('GB18030'))
                                    time.sleep(1)
                                    send_msg['type'] = 'friends'
                                    send_msg['data'] = {
                                        'type': 'friends',
                                        'friends': j[msg['data']['to']]['friends']
                                    }
                                    obj.socket_socket.send(str(send_msg).encode('GB18030'))
                                elif obj.user == msg['data']['from']:
                                    send_msg['type'] = 'delete'
                                    send_msg['data'] = msg['data']
                                    m.socket_socket.send(str(send_msg).encode('GB18030'))
                                    time.sleep(1)
                                    send_msg['type'] = 'friends'
                                    send_msg['data'] = {
                                        'friends': j[msg['data']['from']]['friends']
                                    }
                                    m.socket_socket.send(str(send_msg).encode('GB18030'))
                    elif msg['data']['type'] == 'group':
                        send_msg['status'] = 'success'
                        j[m.user]['friends'] = msg['data']['msg']
                    elif msg['data']['type'] == 'groups':
                        send_msg['status'] = 'failed'
                        send_msg['data'] = '群功能暂时未开放！'
                elif msg['type'] == 'rename':
                    send_msg['type'] = 'rename'
                    send_msg['status'] = 'success'
                    j[m.user]['friends'] = msg['data']['msg']
                elif msg['type'] == 'move':
                    send_msg['type'] = 'move'
                    send_msg['status'] = 'success'
                    j[m.user]['friends'] = msg['data']['msg']
                elif msg['type'] == 'state':
                    if msg['data'] == '在线' or '强聊':
                        if m.user not in self.m.online:
                            self.m.online.append(m.user)
                            self.online()
                    elif msg['data'] == '隐身':
                        if m.user in self.m.online:
                            self.m.online.remove(m.user)
                            self.online()
                open('Data/users.json', 'w', encoding='utf-8').write(json.dumps(j, indent=4, ensure_ascii=False))
            time.sleep(1)

    def online(self):
        # 发送好友在线信息
        for obj in self.objects:
            send_msg = {
                'type': 'online',
                'data': {
                    'online': self.m.online
                },
                'status': 'success'
            }
            try:
                obj.socket_socket.send(str(send_msg).encode('GB18030'))
            except ConnectionResetError:
                print(f'{obj.raddr}已下线')
                self.objects.remove(obj)
            except ConnectionAbortedError:
                print('客户端已下线')
                self.objects.remove(obj)

    def get_host_ip(self):
        # 获得主机IP地址
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((self.dns, 80))
            ip = s.getsockname()[0]
            print(f'当前服务器IP：{ip}')
        except OSError:
            print('请检查网络连接！')
            return False
        finally:
            s.close()
        return ip

    @staticmethod
    def thread(target, *args, **kwargs):
        # 建立线程
        threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True).start()


if __name__ == '__main__':
    j = json.loads(open('Data/users.json', 'r', encoding='utf-8').read(), encoding='utf-8')
    print(json.dumps(j, indent=4, ensure_ascii=False))
    out = input('请输入DNS服务器地址或网关（默认：8.8.8.8）：')
    if out and re.findall(r'(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\d*?', out):
        out = re.findall(r'(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\d*?', out)[0]
    else:
        out = '8.8.8.8'
    Server(socket.gethostbyname_ex('')[2][-1], 21567, 100, out)
