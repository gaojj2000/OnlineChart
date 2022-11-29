# _*_ coding:utf-8 _*_
# FileName: GJJClient.py
# IDE: PyCharm

import os
import re
# import json
import time
import socket
import random
import tkinter
import tkinter.messagebox
from ClientGUI import GUI
from Message import Message


class Client(GUI):

    m = Message()

    def __init__(self, w=800, h=500, t=None, o=None):
        super(Client, self).__init__(w, h, t=t or {'好友列表': {'我的好友': []}, '群组列表': {'我的群聊': []}}, o=o or [])
        self.ip = ''
        self.live = False
        self.s = self.m.socket_socket
        self.text1.configure(state=tkinter.NORMAL)
        self.button5['state'] = tkinter.DISABLED
        self.threads(self.get_server_ip)

    def login(self):
        # 登录
        if re.match(r'^[0-9]{6,10}$', self.entry4.get()) and self.entry5.get():
            msg = {
                'type': 'login',
                'data': {
                    "user": str(self.entry4.get()),
                    "password": self.encryption(str(self.entry4.get()), str(self.entry5.get()))
                },
                'status': 'send'
            }
            try:
                self.s.send(str(msg).encode('GB18030'))
                try:
                    back = self.s.recv(1024)
                    if back:
                        back = eval(back.decode('GB18030'))
                        if back['status'] == 'success':
                            self.label3['foreground'] = 'black'
                            self.button5['state'] = tkinter.DISABLED
                            if back['type'] == 'login':
                                self.label3['text'] = '登录成功！正在加载...'
                            elif back['type'] == 'registry':
                                self.entry5['show'] = ''
                                for i in range(5):
                                    self.label3['text'] = f'注册成功！请牢记您的账号密码，{5-i}秒后自动登录...'
                                    time.sleep(1)
                                self.entry5['show'] = '*'
                            self.m.user = self.entry4.get()
                            self.tree = back['data']['friends']
                            self.on = back['data']['online']
                            if not os.path.isdir('Data\\Example'):
                                os.mkdir('Data\\Example')
                            open(f'Data\\Example\\{self.entry4.get()}.password', 'w', encoding='utf-8').write(self.entry5.get())
                            super(Client, self).login()
                            self.trees_set()
                            self.live = True
                            self.threads(self.receive_message)
                            self.attributes("-disabled", 1)
                            time.sleep(1)
                            self.attributes("-disabled", 0)
                        else:
                            self.entry5.delete(0, tkinter.END)
                            tkinter.messagebox.showerror(title='错误', message=back['data'])
                except ConnectionResetError:
                    tkinter.messagebox.showerror(title='错误', message='服务器异常关闭，请稍等重试！')
                    self.logout()
            except ConnectionResetError:
                tkinter.messagebox.showerror(title='错误', message='服务器异常关闭，请稍等重试！')
                self.logout()
        else:
            self.entry4.delete(0, tkinter.END)
            self.entry5.delete(0, tkinter.END)
            tkinter.messagebox.showerror(title='错误', message='请输入正确的账号和密码！')

    def logout(self):
        # 登出
        self.live = False
        self.s.close()
        self.ip = ''
        self.button5['state'] = tkinter.DISABLED
        self.s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.threads(self.get_server_ip)
        super(Client, self).logout()

    def online_states(self):
        # 在线状态调整
        super(Client, self).online_states()
        if self.focus:
            msg = {
                'type': 'state',
                'data': self.focus,
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def double_tree(self, e):
        # 双击好友进入聊天
        super(Client, self).double_tree(1)
        if self.person not in self.chat:
            self.chat[self.person] = {}
        self.chat_set()

    def chat_load(self):
        # 导入聊天记录
        if os.path.isdir('Data\\ChatSave'):
            for f in os.walk('Data\\ChatSave'):
                for file in f[2]:
                    u = file.rstrip('.json')
                    if u == self.m.user:
                        try:
                            with open(f'Data\\ChatSave\\{file}', 'r', encoding='utf-8') as f2:
                                text = eval(f2.read())
                                f2.close()
                            for item in text:
                                if item in self.chat:
                                    temp = self.chat[item]
                                    self.chat[item] = text[item].copy()
                                    self.chat[item].update({k+len(self.chat[item]): v for k, v in temp.items()})
                                else:
                                    self.chat[item] = text[item]
                            self.chat_set()
                            os.remove(f'Data\\ChatSave\\{file}')
                            tkinter.messagebox.showinfo(title='注意', message='导入聊天记录成功，原保存的已自动删除（为了避免多次导入），欲保存请手动保存！')
                        except SyntaxError:
                            tkinter.messagebox.showerror(title='错误', message='聊天记录格式损坏！')
                    else:
                        tkinter.messagebox.showerror(title='错误', message='未找到聊天记录！')
        else:
            os.mkdir('Data\\ChatSave')
            tkinter.messagebox.showerror(title='警告', message='保存文件夹路径丢失，现已重新创建该目录！')

    def chat_save(self):
        # 保存聊天记录
        if not os.path.isdir('Data\\ChatSave'):
            os.mkdir('Data\\ChatSave')
        if os.path.isfile(f'Data\\ChatSave\\{self.m.user}.json'):
            self.chat_load()
        with open(f'Data\\ChatSave\\{self.m.user}.json', 'w', encoding='utf-8') as f1:
            f1.write(str(self.chat))
            f1.close()

    def add_group(self):
        # 添加分组
        super(Client, self).add_group()
        if self.t:
            msg = {
                'type': 'add',
                'data': {
                    'type': 'group',
                    'from': self.m.user,
                    'to': 'server',
                    'msg': self.tree
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def delete_group(self):
        # 删除分组
        super(Client, self).delete_group()
        if self.focus:
            msg = {
                'type': 'delete',
                'data': {
                    'type': 'group',
                    'from': self.m.user,
                    'to': 'server',
                    'msg': self.tree
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def rename_group(self):
        # 重命名分组
        super(Client, self).rename_group()
        if self.t:
            msg = {
                'type': 'rename',
                'data': {
                    'type': 'group',
                    'from': self.m.user,
                    'to': 'server',
                    'msg': self.tree
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def add_person(self):
        # 添加好友
        super(Client, self).add_person()
        if self.focus:
            for i in self.tree['好友列表']:
                for ii in self.tree['好友列表'][i]:
                    if ii == self.focus:
                        tkinter.messagebox.showerror(title='注意', message=f'{self.focus} 已经是你的好友！')
                        return
            msg = {
                'type': 'add',
                'data': {
                    'type': 'friend',
                    'from': self.m.user,
                    'to': self.focus,
                    'msg': self.t
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def add_groups(self):
        # 添加群聊
        super(Client, self).add_groups()
        if self.focus:
            msg = {
                'type': 'add',
                'data': {
                    'type': 'groups',
                    'from': self.m.user,
                    'to': self.focus,
                    'msg': self.t
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def delete_friend(self):
        # 删除好友
        super(Client, self).delete_friend()
        if self.focus:
            msg = {
                'type': 'delete',
                'data': {
                    'type': 'friend',
                    'from': self.m.user,
                    'to': self.focus,
                    'msg': self.focus
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def quit_groups(self):
        # 退出群聊
        super(Client, self).quit_groups()
        if self.focus:
            msg = {
                'type': 'delete',
                'data': {
                    'type': 'groups',
                    'from': self.m.user,
                    'to': 'server',
                    'msg': self.focus
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def move_friend(self):
        # 移动好友分组
        super(Client, self).move_friend()
        if self.t:
            msg = {
                'type': 'move',
                'data': {
                    'type': 'friend',
                    'from': self.m.user,
                    'to': 'server',
                    'msg': self.tree
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def move_groups(self):
        # 移动群聊分组
        super(Client, self).move_groups()
        if self.t:
            msg = {
                'type': 'move',
                'data': {
                    'type': 'groups',
                    'from': self.m.user,
                    'to': 'server',
                    'msg': self.tree
                },
                'status': 'send'
            }
            self.s.send(str(msg).encode('GB18030'))

    def get_server_ip(self):
        # 获取服务器IP和端口并连接
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        s.bind(('', 21678))
        while not self.ip:
            self.label3['text'] = '正在连接服务器...'
            self.label3['foreground'] = 'black'
            for _ in range(3):
                try:
                    s.settimeout(2)
                    r, a = s.recvfrom(60 * 1024)
                    if r[:19] == b'This is GJJServer .':
                        s.close()
                        self.ip = a[0]
                        self.s.connect((self.ip, int(r[19:])))
                        self.label3['text'] = f'连接服务器成功，服务器IP：{self.ip}'
                        self.label3['foreground'] = 'green'
                        self.button5['state'] = tkinter.NORMAL
                        return
                except socket.timeout:
                    time.sleep(1)
            self.label3['text'] = '连接服务器失败，10秒后将重试。'
            self.label3['foreground'] = 'red'
            time.sleep(10)

    def send_message(self, e=None):
        # 发送消息
        if e:
            self.s.send(str(e).encode('GB18030'))
        elif self.person and self.text2.get(tkinter.START, tkinter.END).rstrip('\n\n'):
            msg = {
                'type': 'normal',
                'data': {
                    'type': 'friend',
                    'from': self.m.user,
                    'to': self.person,
                    'msg': self.text2.get(tkinter.START, tkinter.END).rstrip('\n\n')
                },
                'status': 'send'
            }
            if len(str(msg).encode('GB18030')) > 1024:
                tkinter.messagebox.showerror(title='警告', message='消息内容过长，请分条发送！')
                return
            self.s.send(str(msg).encode('GB18030'))
            n = 1
            while n in self.chat[self.person]:
                n += 1
            self.chat[self.person][n] = f"[{self.m.user}]{msg['data']['msg']}"
            self.chat_set()
            super(Client, self).send_message()
        else:
            tkinter.messagebox.showerror(title='注意', message='请先选择聊天对象和输入要发送的内容！')

    def receive_message(self):
        # 接收消息
        while self.live:
            try:
                back = self.s.recv(1024)
                if back:
                    back = back.decode('GB18030')
                    try:
                        backs = [eval(back)]
                    except SyntaxError:
                        backs = [eval('{'+b+'}') for b in back.lstrip('{').rstrip('}').split('}{')]
                    for back in backs:
                        if back['type'] == 'normal':
                            if back['status'] == 'success':
                                if back['data']['from'] not in self.chat:
                                    self.chat[back['data']['from']] = {}
                                n = 1
                                while n in self.chat[back['data']['from']]:
                                    n += 1
                                self.chat[back['data']['from']][n] = f"[{back['data']['from']}]{back['data']['msg']}"
                            else:
                                n = 1
                                while n in self.chat[back['data'].split(' ')[1]]:
                                    n += 1
                                self.chat[back['data'].split(' ')[1]][n] = f"[来自服务器的消息]{back['data']}"
                            if self.online.get() == '强聊':
                                self.person = back['data']['from']
                                self.title(f'与{self.person}')
                            self.chat_set()
                        elif back['type'] == 'online':
                            self.on = back['data']['online']
                            self.trees_set()
                        elif back['type'] == 'friends':
                            self.tree = back['data']['friends']
                            self.trees_set()
                        # 仅 add 和 delete + friend 和 groups 需要检测
                        elif back['type'] == 'add':
                            if back['status'] == 'wait':
                                if isinstance(back['data'], dict) and back['data']['type'] == 'friend':
                                    if tkinter.messagebox.askyesno(title='好友邀请', message=f"用户 {back['data']['from']} 发来好友邀请"):
                                        back['status'] = 'success'
                                        self.tree['好友列表']['我的好友'].append(back['data']['from'])
                                        self.trees_set()
                                    else:
                                        back['status'] = 'failed'
                                    self.send_message(back)
                            elif back['status'] == 'success':
                                tkinter.messagebox.showinfo(title='加好友成功', message=back['data'])
                            elif back['status'] == 'failed':
                                tkinter.messagebox.showinfo(title='加好友失败', message=back['data'])
                        elif back['type'] == 'delete':
                            if back['status'] == 'success':
                                if isinstance(back['data'], dict) and back['data']['type'] == 'friend':
                                    tkinter.messagebox.showinfo(title='删除成功', message=f"删除好友 {back['data']['to']} 成功！")
                            elif back['status'] == 'failed':
                                tkinter.messagebox.showerror(title='错误', message=back['data'])
            except ConnectionResetError:
                tkinter.messagebox.showerror(title='错误', message='服务器异常关闭，请稍等重试！')
                self.logout()
                break
            except ConnectionAbortedError:
                break
            time.sleep(1)

    def chat_set(self):
        self.clear_message()
        if self.person in self.chat:
            n = 1
            while n in self.chat[self.person]:
                self.insert_message(f"{self.chat[self.person][n]}\n")
                n += 1

    @staticmethod
    def encryption(u: str, p: str):
        # 密码加密
        random.seed(p)
        p = ""
        for nums in u:
            p += chr(ord(nums) ^ random.randint(0, 255))
        return p


if __name__ == '__main__':
    # j = json.loads(open('Data/users.json', 'r', encoding='utf-8').read(), encoding='utf-8')
    # print(json.dumps(j, indent=4, ensure_ascii=False))
    # '666666', 'Gjj666666'
    # t=j['666666']['friends']
    Client().mainloop()
