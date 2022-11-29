# _*_ coding:utf-8 _*_
# FileName: Message.py
# IDE: PyCharm

import queue
import socket
import threading


class Message(object):

    __slots__ = ['_all_user', '_connect', '_friends', '_lock', '_messages', '_new', '_online', '_refuse', '_socket_socket', '_raddr', '_user']

    def __init__(self, s=None, qm=64):
        self._all_user = []  # 所有用户数据
        self._connect = False  # 连接状态【True=在线，False=离线】
        self._friends = {}  # 整个好友分组数据
        self._lock = threading.Lock()  # 线程锁
        self._messages = queue.Queue(maxsize=qm)  # 消息队列
        self._new = False  # 是否有新的好友申请【False表示未有该数据】
        self._online = []  # 在线好友数据
        self._refuse = None  # 加好友是否失败【True=失败，False=成功，None表示未有该数据】
        self._socket_socket = s or socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)  # socket对象
        self._raddr = None  # 连接地址
        self._user = None  # 当前用户

    def __call__(self):
        # 暂未定义可调用对象
        pass

    @property
    def all_user(self):
        return self._all_user

    @all_user.setter
    def all_user(self, all_user):
        if not isinstance(all_user, list):
            raise ValueError("variable `all_user` must be type of `list`")
        self._all_user = all_user

    @property
    def connect(self):
        return self._connect

    @connect.setter
    def connect(self, connect):
        if not isinstance(connect, bool):
            raise ValueError("variable `connect` must be type of `bool`")
        self._connect = connect

    @property
    def friends(self):
        return self._friends

    @friends.setter
    def friends(self, friends):
        if not isinstance(friends, dict):
            raise ValueError("variable `friends` must be type of `dict`")
        self._friends = friends

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, messages):
        if not isinstance(messages, queue.Queue):
            raise ValueError("variable `messages` must be type of `queue.Queue`")
        self._messages = messages

    @property
    def new(self):
        return self._new

    @new.setter
    def new(self, new):
        if not isinstance(new, bool):
            raise ValueError("variable `new` must be type of `bool`")
        self._new = new

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, online):
        if not isinstance(online, list):
            raise ValueError("variable `online` must be type of `list`")
        self._online = online

    @property
    def refuse(self):
        return self._refuse

    @refuse.setter
    def refuse(self, refuse):
        if not isinstance(refuse, bool):
            raise ValueError("variable `refuse` must be type of `bool`")
        self._refuse = refuse

    @property
    def socket_socket(self):
        return self._socket_socket

    @socket_socket.setter
    def socket_socket(self, socket_socket):
        if not isinstance(socket_socket, socket.socket):
            raise ValueError("variable `socket_socket` must be type of `socket.socket`")
        self._socket_socket = socket_socket

    @property
    def raddr(self):
        return self._raddr

    @raddr.setter
    def raddr(self, raddr):
        if not isinstance(raddr, str):
            raise ValueError("variable `raddr` must be type of `str`")
        self._raddr = raddr

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        if not isinstance(user, str):
            raise ValueError("variable `user` must be type of `str`")
        self._user = user

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, value):
        # self.__dict__[key] = value
        raise TypeError("'Message' object does not support item assignment !")

    def __delitem__(self, key):
        # self.__dict__.pop(key)
        raise TypeError("'Message' object does not support item assignment !")


if __name__ == '__main__':
    Message(socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM))
