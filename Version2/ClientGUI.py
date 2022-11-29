# _*_ coding:utf-8 _*_
# FileName: ClientGUI.py
# IDE: PyCharm

import re
import random
import _tkinter
import tkinter as tk
from tkinter import ttk
from _tkinter import TclError
import tkinter.messagebox as msg
from threading import Thread as Th
# from threading import Lock as ThLock


class GUI(tk.Tk):
    # 主界面类
    def __init__(self, w=800, h=500, t=None, o=None):
        super(GUI, self).__init__()
        self.title('GJJ')
        self.person = None  # 当前正在聊天
        self.width = w  # 默认窗口宽度
        self.height = h  # 默认窗口高度
        self.tree = t  # 好友树
        self.on = o  # 当前在线好友
        self.chat = {}  # 聊天记录保存
        self.t = None  # 顶级窗口返回值
        self.focus = None  # 点击文字聚焦

        self.flag = tk.IntVar()  # 换种颜色标志
        self.font_style = tk.StringVar()  # 字体格式
        self.font_size = tk.IntVar()  # 字体大小
        self.online = tk.StringVar()  # 在线状态
        self.choice = tk.IntVar()  # 窗口置顶标志
        self.flag.set(0)
        self.font_style.set('微软雅黑')
        self.font_size.set(10)
        self.online.set('在线')
        self.choice.set(1)

        # 菜单栏
        self.menu = tk.Menu(self, tearoff=0)
        self.states = tk.Menu(self.menu, tearoff=0)
        self.states.add_radiobutton(label='在线', value='在线', variable=self.online, command=self.online_states)
        self.states.add_radiobutton(label='隐身', value='隐身', variable=self.online, command=self.online_states)
        self.states.add_radiobutton(label='强聊', value='强聊', variable=self.online, command=self.online_states)
        self.menu.add_cascade(label='状态', menu=self.states)
        self.operations = tk.Menu(self.menu, tearoff=0)
        self.operations.add_checkbutton(label='换种颜色', variable=self.flag, command=self.bg_set)
        self.operations.add_command(label='导入聊天记录', command=self.chat_load)
        self.operations.add_command(label='保存聊天记录', command=self.chat_save)
        self.operations.add_checkbutton(label='置顶', variable=self.choice, command=self.window)
        self.operations.add_command(label='退出登录', command=self.logout)
        self.menu.add_cascade(label='操作', menu=self.operations)

        # 空菜单
        self.empty = tk.Menu(self)

        # 标签栏
        self.tab = ttk.Notebook(self)
        self.tab1 = tk.Frame(self.tab)
        self.tab2 = tk.Frame(self.tab)
        self.tab3 = tk.Frame(self.tab)
        self.tab.add(self.tab1, text='消息列表')
        self.tab.add(self.tab2, text='找人或群')
        self.tab.add(self.tab3, text='其他设置')
        self.tab.select(self.tab1)

        # 消息列表
        self.scrollbar1 = tk.Scrollbar(self.tab1)
        self.text1 = tk.Text(self.tab1, font=(self.font_style.get(), self.font_size.get()), yscrollcommand=self.scrollbar1.set, relief=tk.FLAT, wrap=tk.WORD)
        self.scrollbar1.config(command=self.text1.yview)
        self.scrollbar2 = tk.Scrollbar(self.tab1)
        self.text2 = tk.Text(self.tab1, font=(self.font_style.get(), self.font_size.get()), yscrollcommand=self.scrollbar2.set, relief=tk.FLAT, wrap=tk.WORD)
        self.scrollbar2.config(command=self.text2.yview)
        self.button1 = tk.Button(self.tab1, font=(self.font_style.get(), self.font_size.get()), text='发送', borderwidth=1, foreground='black', activebackground='#f0f0f0', activeforeground='black', command=lambda: self.threads(self.send_message))
        self.scrollbar3 = tk.Scrollbar(self.tab1)
        self.trees = ttk.Treeview(self.tab1, yscrollcommand=self.scrollbar3.set, show='tree')
        self.scrollbar3.config(command=self.trees.yview)

        self.menu1 = tk.Menu(self.tab1, tearoff=0)
        self.menu1.add_command(label='新建分组', command=self.add_group)

        self.menu2 = tk.Menu(self.tab1, tearoff=0)
        self.menu2.add_command(label='删除分组', command=self.delete_group)
        self.menu2.add_command(label='重命名分组', command=self.rename_group)

        self.menu3 = tk.Menu(self.tab1, tearoff=0)
        self.menu3.add_command(label='删除好友', command=self.delete_friend)
        self.menu3.add_command(label='移动好友', command=self.move_friend)

        self.menu4 = tk.Menu(self.tab1, tearoff=0)
        self.menu4.add_command(label='退出群聊', command=self.quit_groups)
        self.menu4.add_command(label='移动群聊', command=self.move_groups)

        # 分组管理
        self.entry1 = tk.Entry(self.tab2)
        self.box1 = ttk.Combobox(self.tab2, values=list(self.tree['好友列表'].keys()), state='readonly')
        self.box1.set('选择好友分组')
        self.box2 = ttk.Combobox(self.tab2, values=list(self.tree['群组列表'].keys()), state='readonly')
        self.box2.set('选择群聊分组')
        self.button2 = tk.Button(self.tab2, font=(self.font_style.get(), self.font_size.get()), text='找人', borderwidth=1, foreground='black', activebackground='#f0f0f0', activeforeground='black', command=self.add_person)
        self.button3 = tk.Button(self.tab2, font=(self.font_style.get(), self.font_size.get()), text='找群', borderwidth=1, foreground='black', activebackground='#f0f0f0', activeforeground='black', command=self.add_groups)

        # 其他设置
        self.scale = tk.Scale(self.tab3, label='不透明度：', from_=0.30, to=1.00, orient=tk.HORIZONTAL, length=200, showvalue=1, tickinterval=0.1, resolution=0.01, command=self.tou_ming_du)
        self.scale.set(1.00)
        self.label1 = tk.Label(self.tab3, text='字体：                                                            字号：(8-16)                                                  ')
        self.entry2 = tk.Entry(self.tab3, textvariable=self.font_style)
        self.entry3 = tk.Entry(self.tab3, textvariable=self.font_size)
        self.button4 = tk.Button(self.tab3, font=(self.font_style.get(), self.font_size.get()), text='确定', borderwidth=1, foreground='black', activebackground='#f0f0f0', activeforeground='black', command=self.font_set)

        # 登录界面
        self.label2 = tk.Label(self, font=(self.font_style.get(), 15), text='\t\t登录GJJ\n\n\n账号：\n\n密码：')
        self.entry4 = tk.Entry(self)
        self.entry5 = tk.Entry(self, show='*')
        self.button5 = tk.Button(self, font=(self.font_style.get(), 10), text='登录', borderwidth=1, foreground='black', activebackground='#f0f0f0', activeforeground='black', command=lambda: self.threads(self.login))
        self.label3 = tk.Label(self, font=(self.font_style.get(), 15), text='正在连接服务器...')
        self.label2.place(x=140, y=70, width=300, height=160)
        self.entry4.place(x=320, y=150, width=160, height=30)
        self.entry5.place(x=320, y=200, width=160, height=30)
        self.button5.place(x=320, y=250, width=160, height=30)
        self.label3.place(x=150, y=300, width=500, height=160)

        # 所有含font的控件
        self.fonts = [self.text1, self.text2, self.button1, self.button2, self.button3, self.button4]
        # 所有frame组件
        self.frames = [self.tab1, self.tab2, self.tab3]
        # 所有login组件
        self.log_in = [self.label2, self.entry4, self.entry5, self.button5, self.label3]
        # 所有变换颜色
        self.colors = ['Red', 'OrangeRed', 'Yellow', 'Gold', 'Lime', 'Green', 'SeaGreen', 'ForestGreen', 'DarkGreen', 'DarkCyan', 'SkyBlue', 'Blue', 'MediumBlue', 'DarkBlue', 'Navy', 'DarkMagenta', 'Purple', 'Fuchsia', 'DeepPink', 'Crimson']

        self.resizable(0, 0)
        self.minsize(self.width, self.height)
        self.geometry(f'{self.width}x{self.height}+{int((self.winfo_screenwidth()-self.width-16)/2)}+{int((self.winfo_screenheight()-self.height-32)/2)}')

        self.window()
        self.trees_set()
        self.text1.configure(state=tk.DISABLED)
        self.bind('<Configure>', self.window_set)
        self.trees.bind('<Double-1>', self.double_tree)
        self.trees.bind('<ButtonRelease-1>', self.click1_tree)
        self.trees.bind('<ButtonRelease-3>', self.click3_tree)
        self.text2.bind('<Control-KeyRelease-Return>', self.enter_send)

        try:
            self.protocol("WM_DELETE_WINDOW", self.off)
        except _tkinter.TclError:
            pass

    def off(self):
        msg.showinfo(title='拜拜', message='欢迎下次使用 ~ ')
        self.destroy()
        self.quit()

    def login(self):
        # 登录
        for l in self.log_in:
            l.place_forget()
        self.configure(menu=self.menu)  # 登陆成功后启用
        self.tab.pack(expand=1, fill="both")  # 登录成功后启用
        self.resizable(1, 1)
        self.title(f'当前登录QQ：{self.entry4.get()}')
        self.bg_set()

    def logout(self):
        # 登出
        self.person = None
        self.label2.place(x=140, y=70, width=300, height=160)
        self.entry4.place(x=320, y=150, width=160, height=30)
        self.entry5.place(x=320, y=200, width=160, height=30)
        self.button5.place(x=320, y=250, width=160, height=30)
        self.label3.place(x=150, y=300, width=500, height=160)
        self.entry4.delete(0, tk.END)
        self.entry5.delete(0, tk.END)
        self.entry4.focus()
        self.config(menu=self.empty)
        self.tab.pack_forget()
        self.resizable(0, 0)
        self.title('GJJ')

    def online_states(self):
        # 在线状态调整
        self.focus = self.online.get()

    def window(self):
        # 窗口置顶
        self.attributes('-topmost', self.choice.get())

    def tou_ming_du(self, e):
        # 透明度设置
        self.attributes('-alpha', e)

    def font_set(self):
        # 字体设置
        try:
            if self.font_style.get() and 8 <= self.font_size.get() <= 16:
                for f in self.fonts:
                    f.configure(font=(self.font_style.get(), self.font_size.get()))
        except TclError:
            pass
        finally:
            pass

    def bg_set(self):
        # 背景变色
        self.flag.set(0)
        c = random.choice(self.colors)
        for f in self.frames:
            f.configure(bg=c)

    def chat_load(self):
        # 导入聊天记录
        pass

    def chat_save(self):
        # 导出聊天记录
        pass

    def chat_set(self):
        # 设置聊天记录
        pass

    def window_set(self, configure):
        # 窗口组件大小自动设置
        w = self.winfo_width()
        h = self.winfo_height()
        if configure and w >= self.width and h >= self.height:
            self.scrollbar1.place(x=w-200, y=10, width=10, height=h-110)
            self.text1.place(x=10, y=10, width=w-210, height=h-110)
            self.scrollbar2.place(x=w-260, y=h-95, width=10, height=60)
            self.text2.place(x=10, y=h-95, width=w-270, height=60)
            self.button1.place(x=w-240, y=h-95, width=50, height=60)
            self.scrollbar3.place(x=w-20, y=10, width=10, height=h-45)
            self.trees.place(x=w-180, y=10, width=160, height=h-45)

            self.entry1.place(x=0.3*w, y=0.2*h, width=0.4*w, height=30)
            self.box1.place(x=0.2*w, y=0.4*h, width=0.2*w, height=30)
            self.box2.place(x=0.6*w, y=0.4*h, width=0.2*w, height=30)
            self.button2.place(x=0.3*w-25, y=0.6*h, width=50, height=40)
            self.button3.place(x=0.7*w-25, y=0.6*h, width=50, height=40)

            self.scale.place(x=0.3*w, y=0.1*h, width=0.4*w, height=80)
            self.label1.place(x=0.1*w, y=0.4*h, width=0.8*w, height=30)
            self.entry2.place(x=0.2*w, y=0.4*h, width=0.2*w, height=30)
            self.entry3.place(x=0.6*w, y=0.4*h, width=0.2*w, height=30)
            self.button4.place(x=0.5*w - 50, y=0.6*h, width=50, height=40)

    def click1_tree(self, e):
        # 好友树形列表展开
        if e:
            self.trees.focus(self.trees.identify_row(e.y))
            self.trees.selection_set(self.trees.identify_row(e.y))
            item = self.trees.item(self.trees.focus())
            if (e.x <= 20 and item['text'] in self.tree) or (e.x <= 40 and item['text'] in self.tree['好友列表']) or (e.x <= 40 and item['text'] in self.tree['群组列表']):
                pass
            elif item['text']:
                try:
                    if item['open']:
                        self.trees.item(item['text'], open=0)
                    else:
                        self.trees.item(item['text'], open=1)
                except TclError:
                    pass
                finally:
                    pass

    def click3_tree(self, e):
        # 好友树形列表右击菜单
        if e:
            self.trees.focus(self.trees.identify_row(e.y))
            self.trees.selection_set(self.trees.identify_row(e.y))
            if self.trees.item(self.trees.focus())['text'] in list(self.tree.keys()):
                self.menu1.post(e.x_root, e.y_root)
            elif self.trees.item(self.trees.focus())['text'] in list(self.tree['好友列表'].keys()) + list(self.tree['群组列表'].keys()):
                self.menu2.post(e.x_root, e.y_root)
            elif self.trees.parent(self.trees.parent(self.trees.focus())) == '好友列表':
                self.menu3.post(e.x_root, e.y_root)
            elif self.trees.item(self.trees.focus())['text']:
                self.menu4.post(e.x_root, e.y_root)

    def add_group(self):
        # 添加分组
        self.focus = self.trees.item(self.trees.focus())['text']
        self.attributes("-disabled", 1)
        tip = TopWindow('add_group', '添加分组', list(self.tree[self.focus].keys()))
        self.attributes("-disabled", 0)
        if tip:
            self.t = tip.return_input()
            del tip
            if self.t:
                self.tree[self.trees.item(self.trees.focus())['text']][self.t] = []
                self.trees_set()

    def delete_group(self):
        # 删除分组
        self.focus = self.trees.item(self.trees.focus())['text']
        if self.focus in ['我的好友', '我的群聊']:
            msg.showerror('注意', '默认分组无法删除')
        else:
            if msg.askyesno('警告', '删除分组后将移至默认分组，是否继续？'):
                if self.trees.parent(self.trees.focus()) == '好友列表':
                    for f in self.tree['好友列表'][self.focus]:
                        self.tree['好友列表']['我的好友'].append(f)
                    del self.tree['好友列表'][self.focus]
                    self.trees_set()
                elif self.trees.parent(self.trees.focus()) == '群组列表':
                    for f in self.tree['群组列表'][self.focus]:
                        self.tree['群组列表']['我的群聊'].append(f)
                    del self.tree['群组列表'][self.focus]
                    self.trees_set()

    def rename_group(self):
        # 重命名分组
        self.focus = self.trees.item(self.trees.focus())['text']
        if self.focus in ['我的好友', '我的群聊']:
            msg.showerror('注意', '默认分组无法重命名')
        else:
            self.attributes("-disabled", 1)
            tip = TopWindow('rename_group', '重命名分组', list(self.tree['好友列表'].keys()) + list(self.tree['群组列表'].keys()), self.focus)
            self.attributes("-disabled", 0)
            if tip:
                self.t = tip.return_input()
                del tip
                if self.t:
                    if self.trees.parent(self.trees.focus()) == '好友列表':
                        self.tree['好友列表'][self.t] = []
                        for f in self.tree['好友列表'][self.focus]:
                            self.tree['好友列表'][self.t].append(f)
                        del self.tree['好友列表'][self.focus]
                        self.trees_set()
                    elif self.trees.parent(self.trees.focus()) == '群组列表':
                        self.tree['群组列表'][self.t] = []
                        for f in self.tree['群组列表'][self.focus]:
                            self.tree['群组列表'][self.t].append(f)
                        del self.tree['群组列表'][self.focus]
                        self.trees_set()

    def delete_friend(self):
        # 删除好友
        self.focus = self.trees.item(self.trees.focus())['text'].replace("[on]", "").replace("[off]", "")
        if msg.askyesno('警告', f'是否删除好友 {self.focus} ？'):
            self.tree['好友列表'][self.trees.parent(self.trees.focus())].remove(self.focus)
            self.trees_set()

    def move_friend(self):
        # 移动好友分组
        self.focus = self.trees.item(self.trees.focus())['text']
        self.attributes("-disabled", 1)
        tip = TopWindow('move_friend', '移动好友', list(self.tree['好友列表'].keys()), self.focus)
        self.attributes("-disabled", 0)
        if tip:
            self.t = tip.return_input()
            del tip
            if self.t:
                self.tree['好友列表'][self.trees.parent(self.trees.focus())].remove(self.focus.replace("[on]", "").replace("[off]", ""))
                self.tree['好友列表'][self.t].append(self.focus.replace("[on]", "").replace("[off]", ""))
                self.trees_set()

    def quit_groups(self):
        # 退出群聊
        self.focus = self.trees.item(self.trees.focus())['text']
        if msg.askyesno('警告', f'是否退出群聊 {self.focus} ？'):
            self.tree['群组列表'][self.trees.parent(self.trees.focus())].remove(self.focus)
            self.trees_set()

    def move_groups(self):
        # 移动群聊分组
        self.focus = self.trees.item(self.trees.focus())['text']
        self.attributes("-disabled", 1)
        tip = TopWindow('move_group', '移动群聊', list(self.tree['群组列表'].keys()), self.focus)
        self.attributes("-disabled", 0)
        if tip:
            self.t = tip.return_input()
            del tip
            if self.t:
                self.tree['群组列表'][self.trees.parent(self.trees.focus())].remove(self.focus)
                self.tree['群组列表'][self.t].append(self.focus)
                self.trees_set()

    def double_tree(self, e):
        # 双击好友进入聊天
        item = self.trees.item(self.trees.focus())['text']
        if e and self.trees.focus() != item:
            self.person = item.replace('[on]', '').replace('[off]', '')
            self.title(f'与{self.person}')

    def insert_message(self, message):
        # 插入聊天框
        self.text1.configure(state=tk.NORMAL)
        self.text1.insert(tk.END, message)
        self.text1.see(tk.END)
        self.text1.configure(state=tk.DISABLED)

    def clear_message(self):
        # 清除聊天框
        self.text1.configure(state=tk.NORMAL)
        self.text1.delete(tk.START, tk.END)
        self.text1.configure(state=tk.DISABLED)

    def enter_send(self, e):
        # 绑定Ctrl+Enter发送消息
        if e:
            self.send_message()

    def send_message(self, e=None):
        # 发送消息
        # print(self.text2.get(tk.START, tk.END).rstrip('\n\n'))
        self.text2.delete(tk.START, tk.END)

    def trees_set(self):
        # 好友树形列表更新
        for c in self.trees.get_children():
            self.trees.delete(c)
        if isinstance(self.tree, dict):
            for t in self.tree:
                self.trees.insert('', index=tk.END, iid=t, text=t)
                self.trees.item(t, open=True)
                for c in self.tree[t]:
                    self.trees.insert(t, index=tk.END, iid=c, text=c)
                    for f in self.tree[t][c]:
                        if f in self.on:
                            f += '[on]'
                        elif t == '好友列表':
                            f += '[off]'
                        self.trees.insert(c, index=tk.END, text=f)
        self.box1['values'] = list(self.tree['好友列表'].keys())
        self.box1.set('选择好友分组')
        self.box2['values'] = list(self.tree['群组列表'].keys())
        self.box2.set('选择群聊分组')

    def add_person(self):
        # 添加好友
        self.t = None
        self.focus = None
        if re.match(r'^[0-9]{6,10}$', self.entry1.get()) and self.box1.get() != '选择好友分组':
            self.t = self.box1.get()
            self.focus = self.entry1.get()
            if self.focus == self.m.user:
                msg.showerror(title='错误', message='您不能添加自己为好友！')
                self.focus = None
        else:
            msg.showerror(title='错误', message='好友号码或分组信息不正确！')
            self.focus = None

    def add_groups(self):
        # 添加群聊
        self.t = None
        self.focus = None
        if re.match(r'^[0-9]{6,10}$', self.entry1.get()) and self.box2.get() != '选择群聊分组':
            self.t = self.box2.get()
            self.focus = self.entry1.get()

    @staticmethod
    def threads(func, *args):
        # 启动线程
        t = Th(target=func, args=args)
        t.daemon = True
        t.start()


class TopWindow(tk.Tk):
    # 弹出窗口界面类
    def __init__(self, action, title, groups, old_name=None):
        super(TopWindow, self).__init__()
        self.title(title)
        self.flag = False  # 返回控制标志
        self.result = ''  # 返回内容
        self.groups = groups  # 分组信息
        self.action = action  # 行为
        self.old_name = old_name  # 如果重命名，则为之前的名称
        self.entry = tk.Entry(self)
        self.button1 = tk.Button(self, text='确定', command=self.true)
        self.button2 = tk.Button(self, text='取消', command=self.false)
        self.box = ttk.Combobox(self, values=groups, state='readonly')
        self.box.set(groups[0])
        if action in ['add_group', 'rename_group']:
            self.entry.place(x=75, y=20, width=100, height=20)
        elif action in ['move_friend', 'move_group']:
            self.box.place(x=75, y=20, width=100, height=20)
        self.button1.place(x=50, y=60, width=50, height=20)
        self.button2.place(x=150, y=60, width=50, height=20)
        self.resizable(0, 0)
        self.attributes('-topmost', 1)
        self.geometry(f'250x100+{int((self.winfo_screenwidth()-366)/2)}+{int((self.winfo_screenheight()-132)/2)}')
        try:
            self.protocol("WM_DELETE_WINDOW", self.false)
        except _tkinter.TclError:
            pass
        self.mainloop()

    def true(self):
        # 确认更改
        if self.action in ['add_group', 'rename_group']:
            entry = self.entry.get()
        else:
            entry = self.box.get()
        if entry:
            if entry in self.groups and self.action in ['add_group', 'rename_group']:
                msg.showerror('抱歉', '您输入的分组名已存在')
            else:
                self.destroy()
                self.quit()
                self.result = entry
                self.flag = True
        else:
            msg.showerror('注意', '未检测到分组名')

    def false(self):
        # 取消更改
        self.destroy()
        self.quit()
        self.result = False
        self.flag = True

    def return_input(self):
        # 返回结果
        if self.flag:
            return self.result

    # def __new__(cls, *args, **kwargs):
    #     # 单例模式，确保每次改动只有一个窗口
    #     if not hasattr(cls, '_instance'):
    #         with ThLock():
    #             if not hasattr(cls, '_instance'):
    #                 TopWindow._instance = super().__new__(cls)
    #         return TopWindow._instance


if __name__ == '__main__':
    width = 800
    height = 500

    trees = {
        '好友列表': {
            '我的好友': ["1930502098", "2832561754", "2717057684"],
            '特别': ["1332848443", "1696085768", "1835609982"],
        },
        '群组列表': {
            '我的群聊': ["645289967", "864663886"],
            '个人群': ["536640287", "415107147"],
        }
    }

    online = ['1930502098', '1332848443', '1835609982']

    GUI(width, height, trees, online).mainloop()
