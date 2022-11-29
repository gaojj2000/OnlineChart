# _*_ coding:utf-8 _*_
# FileName: LikeQQServer.py
# IDE: PyCharm

import os
import re
import time
import queue
import socket
import selectors
import threading


class Message(object):
    def __init__(self, obj, now, size, users, user, actives):
        self.socket = obj
        self.now = now
        self.size = size
        self.users = users
        self.user = user
        self.actives = actives
        self.add = False
        self.pas = False
        self.status = False
        self.logout = False
        self.death = False
        self.contact = None
        self.Selector = selectors.DefaultSelector()
        self.Selector.register(self.socket, selectors.EVENT_READ)

    def receive(self):
        while 1:
            self.Selector.select(timeout=1)
            try:
                msg = self.socket.recv(self.size).decode('utf-8')
                print(f'msgs:{msg}')
            except ConnectionResetError:
                address = re.search(r"raddr=(\(.*\))", str(self.socket)).group(1)
                print(f'{address} disconnected .')
                try:
                    self.actives.remove(self.now)
                    self.status = True
                except ValueError:
                    pass
                self.death = True
                return None
            if re.match(r'^::[0-9]{6,10}', msg):
                contact = msg[2:].split(' ')[0]
                if contact not in self.users:
                    server_msg = f'FROM SERVER: no such user {contact}'
                    self.socket.send(server_msg.encode('utf-8'))
                else:
                    self.contact = msg[2:].split(' ')[0]
            elif re.match(r'^::ADD [0-9]{6,10}$', msg):
                self.add = re.findall(r'^::ADD ([0-9]{6,10})$', msg)[0]
                return None
            elif msg == '::LOG OUT':
                self.actives.remove(self.now)
                del self.user[self.now]
                self.socket.send(f'FROM SERVER: You ({self.now}) are login out !'.encode('utf-8'))
                print(f'{self.now} logged out . [{time.ctime()}]')
                self.logout = True
                self.status = True
                return None
            else:
                if self.contact is not None:
                    msg = f'[From {self.now} {time.ctime()}]{msg}'
                    self.user[self.contact].put(msg)
                elif re.match(r'%friend pass%[0-9]{6,10}', msg):
                    self.pas = re.findall(r'%friend pass%([0-9]{6,10})', msg)[0]
                    self.status = True
                elif re.match(r'%friend no pass%[0-9]{6,10}', msg):
                    self.pas = False
                else:
                    server_msg = 'FROM SERVER: Please choose a contact first'
                    self.socket.send(server_msg.encode('utf-8'))

    def __call__(self):
        self.thread = threading.Thread(target=self.receive)
        self.thread.daemon = True
        self.thread.start()
        return self.users, self.user, self.actives


class LikeQQServer(object):
    def __init__(self):
        self.users = {}  # all user exist
        self.user = {}  # login user
        self.friends = {}  # user friends
        self.logged = []  # logged user
        self.actives = []  # active user
        self.contact = None  # contact
        self.size = 1024
        self.now = ''
        self.socket = None
        self.address = '10.2.80.202'
        self.port = 21567
        if os.path.isfile('user.txt'):
            print('Users :', end='')
            for u in open('user.txt', 'r+'):
                user = u.replace('\n', '').split(' ')
                self.users[user[0]] = user[1]
                self.user[user[0]] = queue.Queue(4096)
                print(user[0], end=',')
                self.friends[user[0]] = []
                if len(user) > 2:
                    for i in user[2:]:
                        self.friends[user[0]].append(i)
                    self.friends[user[0]].sort(reverse=False)
                del user
            print()
        else:
            raise FileNotFoundError('Lose `user.txt`, please contact technical person .')
        self.TcpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        while 1:
            try:
                self.TcpSocket.bind((self.address, self.port))
                break
            except OSError:
                print('IP address can\'t reach .')
                self.address = input('IP address :')
            except OverflowError:
                print('Port must be 0-65535 .')
                self.port = input('Port :')
        self.TcpSocket.listen(100)
        self.Selectors = selectors.DefaultSelector()
        self.Selector = selectors.DefaultSelector()
        self.Lock = threading.Lock()
        self.Selectors.register(self.TcpSocket, selectors.EVENT_READ)
        self.thread(self.receive)
        self.thread(self.then)
        self.status = False
        while 1:  # loop
            pass

    def receive(self):
        while 1:
            self.Lock.acquire(blocking=True)
            receive = self.Selectors.select(timeout=1)
            self.Lock.release()
            for key, event in receive:
                if key.fileobj == self.TcpSocket:
                    new_socket, new_address = self.TcpSocket.accept()
                    print(f'connected from {new_address} . [{time.ctime()}]')
                    self.Lock.acquire(blocking=True)
                    self.Selectors.register(new_socket, selectors.EVENT_READ)
                    self.Lock.release()
                else:
                    try:
                        user = str(key.fileobj.recv(self.size).decode('utf-8'))
                        if re.match(r'::[0-9]{6,10}', user):
                            user = user[2:].split(' ')
                    except ConnectionResetError:
                        address = re.search(r"raddr=(\(.*\))", str(key.fileobj)).group(1)
                        print(f'{address} disconnected .')
                        self.Lock.acquire(blocking=True)
                        self.Selectors.unregister(key.fileobj)
                        self.Lock.release()
                        continue
                    self.user[user[0]] = queue.Queue(4096)
                    if re.match(r'[0-9]{6,10}', user[0]) and user[0] not in self.users:
                        self.users[user[0]] = user[1]
                        self.friends[user[0]] = []
                        self.actives.append(user[0])
                        self.status = True
                        print(f'{user[0]} signed up . [{time.ctime()}]')
                        key.fileobj.send(f'FROM SERVER: You ({user[0]}) have success signed up .'.encode('utf-8'))
                        open('user.txt', 'a').write(f'\n{user[0]} {user[1]}')
                    elif re.match(r'[0-9]{6,10}', user[0]):
                        if user[0] in self.actives:
                            key.fileobj.send(f'FROM SERVER: {user[0]} already logged in !'.encode('utf-8'))
                            print(f'FROM SERVER: {user[0]} already logged in !')
                            continue
                        else:
                            if self.users[user[0]] == user[1]:
                                self.actives.append(user[0])
                                self.status = True
                                key.fileobj.send(f'FROM SERVER: You ({user[0]}) are login in !'.encode('utf-8'))
                                print(f'{user[0]} logged in . [{time.ctime()}]')
                                time.sleep(1)
                                if user[0] in self.friends:
                                    print('ok')
                                    key.fileobj.send(f'%friends%{self.friends[user[0]]}'.encode('utf-8'))
                                    print(f'%friends%{self.friends[user[0]]}')
                                else:
                                    key.fileobj.send('%no friend%'.encode('utf-8'))
                                    print('%no friend%')
                                time.sleep(1)
                                key.fileobj.send(f'%online friends%{self.actives}'.encode('utf-8'))
                                print(f'%online friends%{self.actives}')
                            else:
                                key.fileobj.send(f'FROM SERVER: Your ({user[0]}) password is not right !'.encode('utf-8'))
                    try:
                        self.Selector.register(key.fileobj, selectors.EVENT_READ)
                    except KeyError:
                        pass
                    print(type(key.fileobj))
                    message = Message(key.fileobj, user[0], self.size, self.users, self.user, self.actives)
                    self.logged.append(message)
                    self.users, self.user, self.actives = message()
                    self.Lock.acquire(blocking=True)
                    self.Selectors.unregister(key.fileobj)
                    self.Lock.release()

    def then(self):
        while 1:
            try:
                for eachUser in self.logged:
                    if eachUser.pas:
                        self.friends[eachUser.pas].append(eachUser.now)
                        self.friends[eachUser.now].append(eachUser.pas)
                        open('user.txt', 'w').write('')
                        for u in self.friends:
                            self.friends[u].sort(reverse=False)
                            text = ''
                            for f in self.friends[u]:
                                text += f' {f}'
                            open('user.txt', 'a').write(f'{u} {self.users[u]}{text}\n')
                        self.status = True
                        eachUser.pas = False
                    if eachUser.add:
                        for each in self.logged:
                            if each.now == eachUser.add:
                                each.socket.send(f'%new friend%{eachUser.now}'.encode('utf-8'))
                        eachUser.add = False
                    if eachUser.status or self.status:
                        for each in self.logged:
                            if each.now in self.friends:
                                try:
                                    each.socket.send(f'%friends%{self.friends[each.now]}'.encode('utf-8'))
                                    print(f'%friends%{self.friends[each.now]}')
                                    time.sleep(1)
                                    each.socket.send(f'%online friends%{self.actives}'.encode('utf-8'))
                                    print(f'%online friends%{self.actives}')
                                except ConnectionResetError:
                                    pass
                        eachUser.status = False
                        self.status = False
                    if eachUser.logout:
                        self.Lock.acquire(blocking=True)
                        try:
                            self.Selectors.register(eachUser.socket, selectors.EVENT_READ)
                        except ValueError:
                            pass
                        except KeyError:
                            pass
                        self.Lock.release()
                        self.logged.remove(eachUser)
                        del eachUser
                        continue
                    if eachUser.death:
                        self.logged.remove(eachUser)
                        del eachUser
                        continue
                    if self.user and self.user[eachUser.now].qsize():
                        try:
                            eachUser.socket.send(self.user[eachUser.now].get().encode('utf-8'))
                        except ConnectionResetError:
                            pass
            except RuntimeError:
                pass
            except AttributeError:
                pass
            finally:
                time.sleep(1)

    @staticmethod
    def thread(function, *args):
        t = threading.Thread(target=function, args=args)
        t.daemon = True
        t.start()


if __name__ == '__main__':
    LikeQQServer()
