# _*_ coding:utf-8 _*_
# Project: 
# FileName: LikeQQClient.py
# UserName: 高俊佶
# ComputerUser：19305
# Day: 2020/3/27
# Time: 14:00
# IDE: PyCharm
# 最爱洪洪，永无BUG！

import re
import time
import queue  # no use
import socket
import tkinter
import selectors
import threading
import tkinter.messagebox


class LikeQQClient(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.ip = '127.0.0.1'
        self.port = 21567
        self.user = ''
        self.password = ''
        self.time = 1024
        self.log = None
        self.re_log = False
        self.to = ''
        self.msg = ''
        self.friend = []
        self.online = []
        self.messages = {}
        self.title(' ChatTogether ')
        self.text = tkinter.StringVar()
        self.num = tkinter.StringVar()
        self.choice = tkinter.IntVar()
        self.label = tkinter.Label(self)
        self.scrollbar1 = tkinter.Scrollbar(self)
        self.text1 = tkinter.Text(self, font=('Fixedsys', 10), yscrollcommand=self.scrollbar1.set, relief=tkinter.FLAT, wrap=tkinter.WORD, highlightthickness=2, highlightcolor='black', highlightbackground='black')
        self.scrollbar1.config(command=self.text1.yview)
        self.scrollbar2 = tkinter.Scrollbar(self)
        self.text2 = tkinter.Text(self, font=('Fixedsys', 10), yscrollcommand=self.scrollbar2.set, relief='flat', wrap=tkinter.WORD, highlightthickness=2, highlightcolor='black', highlightbackground='black')
        self.scrollbar2.config(command=self.text2.yview)
        self.button1 = tkinter.Button(self, font=('Fixedsys', 10), text='SEND', borderwidth=1, foreground='black', activebackground='#f0f0f0', activeforeground='black', command=lambda: self.threads(self.send_message))
        self.entry = tkinter.Entry(self, textvariable=self.num, highlightthickness=2, highlightcolor='black', highlightbackground='black')
        self.check = tkinter.Checkbutton(self, text='Top', font=('Fixedsys', 10), onvalue=1, offvalue=0, variable=self.choice, background='#f7f6e2', command=lambda: self.window())
        self.button2 = tkinter.Button(self, font=('Fixedsys', 10), text='ADD', borderwidth=1, foreground='black', activebackground='#f0f0f0', activeforeground='black', command=lambda: self.threads(self.add))
        self.scrollbar3 = tkinter.Scrollbar(self)
        self.friends = tkinter.Listbox(self, yscrollcommand=self.scrollbar3.set, highlightthickness=2, highlightcolor='black', highlightbackground='black')
        self.scrollbar3.config(command=self.friends.yview)
        self.button3 = tkinter.Button(self, font=('Fixedsys', 10), text='LOGOUT', borderwidth=1, foreground='black', activebackground='#f0f0f0', activeforeground='black', command=lambda: self.threads(self.logout))
        self.text1.configure(state=tkinter.DISABLED)
        self.bind('<Configure>', self.window_set)
        self.protocol("WM_DELETE_WINDOW", 1)
        self.TcpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.Selector = selectors.DefaultSelector()
        self.Selector.register(self.TcpSocket, selectors.EVENT_READ)
        self.Selectors = selectors.DefaultSelector()
        self.Selectors.register(self.TcpSocket, selectors.EVENT_READ)
        self.que = queue.Queue(4096)
        self.threads(self.login)
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.center_window()
        self.minsize(width=500, height=300)
        self.resizable(width=True, height=True)
        self.mainloop()

    def window(self):
        if self.choice.get():
            self.attributes('-topmost', 1)
        else:
            self.attributes('-topmost', 0)

    def center_window(self, width=500, height=300):
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(size)

    def window_set(self, configure):
        w = self.winfo_width()
        h = self.winfo_height()
        if configure and w >= 500 and h >= 300:
            # self.label.place(x=10, y=10, width=360, height=20)
            # self.scrollbar1.place(x=370, y=40, width=10, height=180)
            # self.text1.place(x=10, y=40, width=360, height=180)
            # self.scrollbar2.place(x=310, y=230, width=10, height=60)
            # self.text2.place(x=10, y=230, width=300, height=60)
            # self.button1.place(x=330, y=240, width=50, height=40)
            # self.entry.place(x=390, y=10, width=100, height=20)
            # self.check.place(x=390, y=35, width=50, height=30)
            # self.button2.place(x=450, y=35, width=40, height=30)
            # self.scrollbar3.place(x=480, y=70, width=10, height=190)
            # self.friends.place(x=390, y=70, width=90, height=190)
            # self.button3.place(x=390, y=270, width=90, height=20)
            self.label.place(x=10, y=10, width=w-140, height=20)
            self.scrollbar1.place(x=w-130, y=40, width=10, height=h-120)
            self.text1.place(x=10, y=40, width=w-140, height=h-120)
            self.scrollbar2.place(x=w-190, y=h-70, width=10, height=60)
            self.text2.place(x=10, y=h-70, width=w-200, height=60)
            self.button1.place(x=w-170, y=h-60, width=50, height=40)
            self.entry.place(x=w-110, y=10, width=100, height=20)
            self.check.place(x=w-110, y=35, width=50, height=30)
            self.button2.place(x=w-50, y=35, width=40, height=30)
            self.scrollbar3.place(x=w-20, y=70, width=10, height=h-110)
            self.friends.place(x=w-110, y=70, width=90, height=h-110)
            self.button3.place(x=w-110, y=h-30, width=90, height=20)

    def insert(self, text):
        self.text1.configure(state=tkinter.NORMAL)
        self.text1.insert(tkinter.INSERT, text)
        self.text1.configure(state=tkinter.DISABLED)

    def clear_text1(self):
        self.text1.configure(state=tkinter.NORMAL)
        self.text1.delete(tkinter.START, tkinter.END)
        self.text1.configure(state=tkinter.DISABLED)

    def clear_text2(self):
        self.text2.delete(tkinter.START, tkinter.END)

    def login(self):
        self.iconify()
        self.threads(self.receive_message)

    def add(self):
        if re.match(r'^[0-9]{6,10}$', self.entry.get()):
            self.TcpSocket.send(f'::ADD {self.entry.get()}'.encode('utf-8'))

    def logout(self):
        self.friend = []
        self.online = []
        self.messages = {}
        self.to = {}
        self.TcpSocket.send('::LOG OUT'.encode('utf-8'))
        time.sleep(1)
        self.iconify()
        self.re_log = True
        while 1:
            if self.online:
                self.deiconify()
                break

    def send_message(self):
        if self.to:
            self.TcpSocket.send(self.text2.get(tkinter.START, tkinter.END).encode('utf-8'))
            self.insert(f'[me]{self.text2.get(tkinter.START, tkinter.END)}')
            self.text2.delete(tkinter.START, tkinter.END)
        else:
            tkinter.messagebox.showinfo(title='error', message='no friend choose')

    def receive_message(self):
        self.log = Login(self.ip, self.port, self.TcpSocket, self.Selector, self.time, self.que)
        self.threads(self.friend_check)
        self.ip, self.port, self.user, self.password, self.TcpSocket, self.Selector, self.que = self.log.update()
        while 1:
            if self.online:
                self.deiconify()
                break

    def friend_check(self):
        while 1:
            if self.re_log:
                self.user, self.password, self.TcpSocket, self.Selector, self.que = self.log.re_log()
                self.re_log = False
            self.msg = self.log.msg
            if self.log.pas:
                tkinter.messagebox.showinfo(title='oh~~~', message=f'{self.log.pas} is your friend now !')
                self.friend.append(self.log.pas)
                self.log.pas = ''
            if self.friend != self.log.friend or self.online != self.log.online:
                self.friend = self.log.friend
                self.online = self.log.online
                self.friends.delete(0, tkinter.END)
                for f in self.friend:
                    self.messages[f] = []
                    sf = f
                    if f in self.online:
                        sf += '[on]'
                    else:
                        sf += '[off]'
                    # self.friends.insert(tkinter.END, f + str(len(self.messages[f])) if len(self.messages[f]) else '')
                    self.friends.insert(tkinter.END, sf + (len(self.messages[f]) and str(len(self.messages[f])) or ''))
                self.friends.bind('<Double-1>', self.contact_method)
            if self.log.msg:
                if re.match(r'\[From [0-9]{6,10}.*?\](.*)', self.log.msg):
                    msg = re.findall(r'\[From ([0-9]{6,10}).*?\](.*)', self.log.msg)[0]
                    self.messages[msg[0]].append(msg[1])
                    if self.to != msg[0]:
                        self.to = msg[0]
                        self.threads(self.contact_method, 0)
                    else:
                        self.insert(f'{msg[1]}\n')
                else:
                    self.insert(self.log.msg)
                self.log.msg = ''
            if self.log.nop:
                tkinter.messagebox.showerror(title='error', message=f'{self.log.nop} refuse to be your friend !')
                self.log.nop = ''
            if self.log.new:
                if tkinter.messagebox.askyesno(title='new friend', message=f'Do you want to be friend of {self.log.new} ?'):
                    self.TcpSocket.send(f'%friend pass%{self.log.new}'.encode('utf-8'))
                else:
                    self.TcpSocket.send(f'%friend no pass%{self.log.new}'.encode('utf-8'))
                self.log.new = ''
            time.sleep(1)

    def contact_method(self, event):
        if event:
            self.to = re.findall(r"[0-9]{6,10}", self.friends.get(self.friends.curselection()))[0]
            self.TcpSocket.send(f'::{self.to}'.encode('utf-8'))
            self.label.configure(text=f'Now Window：{self.to}')
            self.clear_text1()
        self.TcpSocket.send(f'::{self.to}'.encode('utf-8'))
        self.label.configure(text=f'Now Window：{self.to}')
        self.clear_text1()
        for t in self.messages[self.to]:
            self.insert(f'{t}\n')

    @staticmethod
    def threads(func, *args):
        t = threading.Thread(target=func, args=args)
        t.daemon = True
        t.start()


class Login(object):
    def __init__(self, ip, port, tcp, selector, size, que):
        self.ip = ip
        self.port = port
        self.TcpSocket = tcp
        self.Selectors = selector
        self.size = size
        self.que = que
        self.msg = ''
        self.user = ''
        self.password = ''
        self.pas = ''
        self.nop = ''
        self.new = ''
        self.friend = []
        self.online = []
        self.root = tkinter.Tk()
        self.root.title(' Choose server ')
        self.root.attributes('-topmost', 1)
        self.label1 = tkinter.Label(self.root, text='Input server ip :')
        self.label1.pack()
        self.label2 = tkinter.Label(self.root, text='Input user :')
        self.label3 = tkinter.Label(self.root, text='Input password :')
        self.entry1 = tkinter.Entry(self.root)
        self.entry1.insert(0, f'{self.ip}/{self.port}')
        self.entry1.pack()
        self.entry2 = tkinter.Entry(self.root)
        self.entry3 = tkinter.Entry(self.root, show='*')
        self.button1 = tkinter.Button(self.root, text='connect', command=lambda: self.threads(self.connect))
        self.button1.pack()
        self.button2 = tkinter.Button(self.root, text='login', command=lambda: self.threads(self.login))
        self.root.protocol("WM_DELETE_WINDOW", 1)
        self.center_window()

    def center_window(self, width=160, height=120):
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(size)

    def connect(self):
        ip = re.compile(r'(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\d*?')
        inp = self.entry1.get().split('/')
        if not (ip.match(inp[0]) and ip.match(inp[0]).group(0) == inp[0]):
            tkinter.messagebox.showerror(title='error', message='Your ip is wrong !')
            return False
        else:
            self.ip = inp[0]
        if not 0 <= int(inp[1]) < 65536:
            tkinter.messagebox.showerror(title='error', message='Your port is wrong !')
            return False
        else:
            self.port = int(inp[1])
        try:
            self.TcpSocket.connect((self.ip, self.port))
        except OSError:
            tkinter.messagebox.showerror(title='error', message='Server ip and port can\'t reach !')
            return False
        self.label1.destroy()
        self.entry1.destroy()
        self.button1.destroy()
        self.label2.pack()
        self.entry2.pack()
        self.label3.pack()
        self.entry3.pack()
        self.button2.pack()

    def login(self):
        if not re.match(r'^[0-9]{6,10}', self.entry2.get()):
            print(self.entry2.get())
            tkinter.messagebox.showerror(title='error', message='Your username is wrong !')
            return False
        else:
            self.user = self.entry2.get()
        if not self.entry3.get():
            tkinter.messagebox.showerror(title='error', message='Your password is empty !')
            return False
        else:
            self.password = self.entry3.get()
        self.Selectors.select(timeout=1)
        self.TcpSocket.send(f'::{self.user} {self.password}'.encode('utf-8'))
        self.threads(self.receive)
        self.root.destroy()
        self.root.quit()

    def update(self):
        self.root.mainloop()
        return self.ip, self.port, self.user, self.password, self.TcpSocket, self.Selectors, self.que

    def re_log(self):
        self.label2.pack()
        self.entry2.pack()
        self.label3.pack()
        self.entry3.pack()
        self.button2.pack()
        self.root.mainloop()
        self.threads(self.login)
        return self.user, self.password, self.TcpSocket, self.Selectors, self.que

    def receive(self):
        while 1:
            try:
                msg = self.TcpSocket.recv(self.size).decode('utf-8')
            except ConnectionResetError:
                tkinter.messagebox.showerror(title='error', message='Server end this connection !')
                return False
            if re.match(r'%.*?%', msg):
                if re.match(r'%friends%(\[.*?\])', msg):
                    self.friend = eval(re.findall(r'%friends%(\[.*?\])', msg)[0])
                if re.match(r'%online friends%(\[.*?\])', msg):
                    self.online = eval(re.findall(r'%online friends%(\[.*?\])', msg)[0])
                if re.match(r'%friend pass%[0-9]{6,10}', msg):
                    self.pas = re.findall(r'%friend pass%([0-9]{6,10})', msg)[0]
                    self.friend.append(self.pas)
                if re.match(r'%friend no pass%[0-9]{6,10}', msg):
                    self.nop = re.findall(r'%friend no pass%[0-9]{6,10}', msg)[0]
                if re.match(r'%new friend%[0-9]{6,10}', msg):
                    self.new = re.findall(r'%new friend%([0-9]{6,10})', msg)[0]
            elif re.match(r'^::ADD [0-9]{6,10}$', msg):
                pass
            elif re.match('FROM SERVER.*', msg):
                if msg == f'FROM SERVER: Your ({self.user}) password is not right !':
                    tkinter.messagebox.showerror(title='error', message='Your password is wrong !')
            else:
                self.msg = msg
            time.sleep(1)

    @staticmethod
    def threads(func, *args):
        t = threading.Thread(target=func, args=args)
        t.daemon = True
        t.start()


if __name__ == '__main__':
    LikeQQClient()
