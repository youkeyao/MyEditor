import tkinter as tk
import tkinter.filedialog as tf
import tkinter.messagebox as tm
import LabelText
import ScrolledTab
import FileTree
import threading
import hashlib

class editorgui:
    text = None #文本组件
    tab = None #标签组件
    content = [] #文本内容
    path = [] #文件路径
    change = [] #文本内容是否改变
    sig = [] #签名
    mark = [] #光标位置
    workspace = '' #文件夹路径
    language = None #语言

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('MyEditor')
        self.root.geometry('800x700')
        self.root.protocol('WM_DELETE_WINDOW', self.__editQuit)

        self.__initControl()

        self.__initMenu()

        self.tab.tabAdd()

    def __initMenu(self):
        rootmenu = tk.Menu(self.root)

        filemenu = tk.Menu(rootmenu, tearoff = False)
        filemenu.add_command(label = 'New', command = self.tab.tabAdd)
        filemenu.add_separator()
        filemenu.add_command(label = 'Open', command = self.__openFile)
        filemenu.add_separator()
        filemenu.add_command(label = 'Save', command = self.__saveFile)
        filemenu.add_command(label = 'Save as', command = self.__saveAsFile)

        editmenu = tk.Menu(rootmenu, tearoff = False)
        editmenu.add_command(label = 'Find', command = self.__findWindow)
        editmenu.add_separator()
        editmenu.add_command(label = 'Replace', command = self.__replaceWindow)

        settingmenu = tk.Menu(rootmenu, tearoff = False)
        languagemenu = tk.Menu(settingmenu, tearoff = False)
        self.language = tk.StringVar()
        self.language.set("C")
        languagemenu.add_radiobutton(label = 'C', variable = self.language, value = "C", command = lambda:self.__changeLanguage("C"))
        languagemenu.add_radiobutton(label = 'C++', variable = self.language, command = lambda:self.__changeLanguage("C++"))
        languagemenu.add_radiobutton(label = 'Java', variable = self.language, command = lambda:self.__changeLanguage("Java"))
        languagemenu.add_radiobutton(label = 'Python', variable = self.language, command = lambda:self.__changeLanguage("Python"))
        languagemenu.add_radiobutton(label = 'Other', variable = self.language, command = lambda:self.__changeLanguage("Other"))
        settingmenu.add_cascade(label = 'Language', menu = languagemenu)

        rightmenu = tk.Menu(self.root, tearoff = False)
        rightmenu.add_command(label = 'Undo', command = self.text.textwin.edit_undo)
        rightmenu.add_separator()
        rightmenu.add_command(label = 'Redo', command = self.text.textwin.edit_redo)

        rootmenu.add_cascade(label = 'File', menu = filemenu)
        rootmenu.add_cascade(label = 'Edit', menu = editmenu)
        rootmenu.add_cascade(label = 'Setting', menu = settingmenu)

        self.text.textwin.bind('<Button-3>', lambda event:rightmenu.post(event.x_root, event.y_root))

        self.root.config(menu = rootmenu)

    #初始化组件
    def __initControl(self):
        #窗口
        win = tk.PanedWindow(self.root, opaqueresize = False, bd = 0, sashwidth = 1.5, bg = 'black')
        win.pack(fill = tk.BOTH, expand = True)

        #左框架
        lframe = tk.Frame(win, bg = "#D3D3D3")
        win.add(lframe)

        #文件列表和按钮
        self.ftree = FileTree.FileTree(lframe)
        folderbutton = tk.Button(lframe, text = 'open folder', font = ("Verdana", 10), padx = 10, pady = 5, command = lambda:self.threadFunc(self.__openFolder))
        folderbutton.pack()
        self.ftree.pack(fill = tk.BOTH, expand = True)
        self.ftree.bindTree(self.__openFile)

        #右框架
        rframe = tk.Frame(win)
        win.add(rframe)

        #标签栏
        self.tab = ScrolledTab.ScrolledTab(rframe)
        self.tab.pack(fill = tk.X)
        self.tab.bindFunc(self.__newFile, self.__changeFile, self.__closeFile, self.__editQuit)

        #文本框
        self.text = LabelText.LabelText(rframe)
        self.text.pack(fill = tk.BOTH, expand = True)
        self.text.bindCheck(self.__checkText)

    #打开文件
    def __openFile(self, path = ""):
        if path == '':
            path = tf.askopenfilename()
        try:
            with open(path, 'rb') as f:
                data = f.read().decode('utf-8')
                self.tab.tabAdd()
                self.path[self.tab.current] = path
                self.content[self.tab.current] = data
                self.sig[self.tab.current] = hashlib.md5(data.encode('utf-8')).digest()
                #显示新文件
                self.text.setText(self.content[self.tab.current])
                self.__setTitle()
        except:
            tm.showwarning('Warning', 'File open error')
            print('file open error')

    #保存文件
    def __saveFile(self):
        if self.path[self.tab.current] == "":
            path = tf.asksaveasfilename(filetypes = [('TXT', '.txt'), ('Python', '.py')])
            if path != '':
                self.path[self.tab.current] = path
        try:
            with open(self.path[self.tab.current], 'wb') as f:
                data = self.text.getText().encode('utf-8')
                f.write(data)
                #更新
                self.content[self.tab.current] = data
                self.sig[self.tab.current] = hashlib.md5(data).digest()
                self.change[self.tab.current] = False
                self.__setTitle()
        except:
            tm.showwarning('Warning', 'File save error')
            print('file save error')

    #另存文件
    def __saveAsFile(self):
        path = tf.asksaveasfilename(filetypes = [('TXT', '.txt'), ('Python', '.py')])
        if path != "":
            self.path[self.tab.current] = path
            self.__saveFile()

    #新文件
    def __newFile(self):
        self.content.append('')
        self.path.append('')
        self.change.append(False)
        self.sig.append(hashlib.md5(''.encode('utf-8')).digest())
        self.mark.append('1.0')

    #切换文件
    def __changeFile(self, old):
        if old != -1:
            self.content[old] = self.text.getText()
            self.mark[old] = self.text.getInsert()
        self.text.setText(self.content[self.tab.current])
        self.text.setInsert(self.mark[self.tab.current])
        self.__setTitle()

    #关闭文件
    def __closeFile(self):
        if self.change[self.tab.current]:
            choice = tm.askyesnocancel('提示', '要保存吗？')
            if choice == True:
                self.__saveFile()
            elif choice == None:
                return False
        del self.content[self.tab.current]
        del self.path[self.tab.current]
        del self.sig[self.tab.current]
        del self.change[self.tab.current]
        del self.mark[self.tab.current]
        return True

    #更换显示文件夹
    def __openFolder(self):
        path = tf.askdirectory()
        if path != '':
            self.workspace = path
            self.ftree.setTree(path)

    #查找文本
    def __findWindow(self):
        #新窗口
        findwin = tk.Toplevel(self.root)
        findwin.title('Find')
        findwin.attributes('-toolwindow', True)
        findwin.attributes('-topmost', True)
        findwin.resizable(0, 0)
        findwin.focus()
        findwin.bind('<Destroy>', lambda event:self.text.textwin.tag_remove('found', '1.0', 'end'))
        #输入框
        targetText = tk.Entry(findwin)
        targetText.pack()
        #查找按钮
        findbutton = tk.Button(findwin, text = 'find', command = lambda:self.text.findText(targetText.get(), 'found'))
        findbutton.pack()

    #替换文本
    def __replaceWindow(self):
        #新窗口
        replacewin = tk.Toplevel()
        replacewin.title('Replace')
        replacewin.attributes('-toolwindow', True)
        replacewin.attributes('-topmost', True)
        replacewin.resizable(0, 0)
        replacewin.focus()
        replacewin.bind('<Destroy>', lambda event:self.text.textwin.tag_remove('found', '1.0', 'end'))
        #查找内容
        targetText = tk.Entry(replacewin)
        targetText.pack()
        tk.Label(replacewin, text = '↓').pack()
        #替换内容
        replaceText = tk.Entry(replacewin)
        replaceText.pack()
        #查找按钮
        replacebutton = tk.Button(replacewin, text = 'replace', command = lambda:self.text.replaceText(targetText.get(), replaceText.get()))
        replacebutton.pack()

    #选择语言
    def __changeLanguage(self, lan):
        self.language.set(lan)
        self.text.changeLan(lan)

    #设置标签和窗口标题
    def __setTitle(self):
        n = self.tab.current
        s = self.path[n]
        if s == "":
            s = 'Untitled'
        if self.change[n]:
            s = s + '*'
        self.root.title('MyEditor-'  + s)
        s = s.split('/')[-1]
        self.tab.tabs[n].config(text = s)

    #检查文本变动
    def __checkText(self):
        if self.change[self.tab.current] or self.tab.current == -1:
            return
        sig = hashlib.md5(self.text.getText().encode('utf-8')).digest()
        if sig != self.sig[self.tab.current]:
            self.change[self.tab.current] = True
            self.__setTitle()

    #退出
    def __editQuit(self):
        flag = True
        while len(self.tab.tabs) != 0:
            if not self.tab.tabRemove(self.tab.tabs[0]):
                flag = False
                break
        if flag:
            self.root.quit()

    #多线程
    def threadFunc(self, func, *args):
        t = threading.Thread(target = func, args = args)
        t.setDaemon(True)
        t.start()

if __name__ == '__main__':
    editorgui().root.mainloop()