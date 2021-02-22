import tkinter as tk
import tkinter.filedialog as tf
import tkinter.messagebox as tm
import LabelText
import ScrolledTab
import FileTree
import threading
import hashlib

class editorgui:
    content = [] #文本内容
    path = [] #文件路径
    change = [] #文本内容是否改变
    sig = [] #签名
    mark = [] #光标位置
    workspace = '' #文件夹路径

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('MyEditor')
        self.root.geometry('800x700')
        self.root.protocol('WM_DELETE_WINDOW', self.__editorquit)

        self.__initcontrol()

        self.__initmenu()

        self.tab.tabadd()

    def __initmenu(self):
        rootmenu = tk.Menu(self.root)

        filemenu = tk.Menu(rootmenu, tearoff = False)
        filemenu.add_command(label = 'New', command = self.tab.tabadd)
        filemenu.add_separator()
        filemenu.add_command(label = 'Open', command = self.__openfile)
        filemenu.add_separator()
        filemenu.add_command(label = 'Save', command = self.__savefile)
        filemenu.add_command(label = 'Save as', command = self.__saveasfile)

        editmenu = tk.Menu(rootmenu, tearoff = False)
        editmenu.add_command(label = 'Find', command = self.__findwindow)
        editmenu.add_separator()
        editmenu.add_command(label = 'Replace', command = self.__replacewindow)

        rightmenu = tk.Menu(self.root, tearoff = False)
        rightmenu.add_command(label = 'Undo', command = self.text.textwin.edit_undo)
        rightmenu.add_separator()
        rightmenu.add_command(label = 'Redo', command = self.text.textwin.edit_redo)

        rootmenu.add_cascade(label = 'File', menu = filemenu)
        rootmenu.add_cascade(label = 'Edit', menu = editmenu)

        self.text.textwin.bind('<Button-3>', lambda event:rightmenu.post(event.x_root, event.y_root))

        self.root.config(menu = rootmenu)

    #初始化组件
    def __initcontrol(self):
        #窗口
        win = tk.PanedWindow(self.root, opaqueresize = False, bd = 0, sashwidth = 1.5, bg = 'black')
        win.pack(fill = tk.BOTH, expand = True)

        #左框架
        lframe = tk.Frame(win, bg = "#D3D3D3")
        win.add(lframe)

        #文件列表和按钮
        self.ftree = FileTree.FileTree(lframe)
        folderbutton = tk.Button(lframe, text = 'open folder', font = ("Verdana", 10), padx = 10, pady = 5, command = lambda:self.threadfunc(self.__openfolder))
        folderbutton.pack()
        self.ftree.pack(fill = tk.BOTH, expand = True)
        self.ftree.bindtree(self.__openfile)

        #右框架
        rframe = tk.Frame(win)
        win.add(rframe)

        #标签栏
        self.tab = ScrolledTab.ScrolledTab(rframe)
        self.tab.pack(fill = tk.X)
        self.tab.bindfunc(self.__newfile, self.__changefile, self.__closefile, self.__editorquit)

        #文本框
        self.text = LabelText.LabelText(rframe)
        self.text.pack(fill = tk.BOTH, expand = True)
        self.text.bindcheck(self.__checktext)

    #打开文件
    def __openfile(self, path = ""):
        if path == '':
            path = tf.askopenfilename()
        try:
            with open(path, 'rb') as f:
                data = f.read().decode('utf-8')
                self.tab.tabadd()
                self.path[self.tab.current] = path
                self.content[self.tab.current] = data
                self.sig[self.tab.current] = hashlib.md5(data.encode('utf-8')).digest()
                #显示新文件
                self.text.settext(self.content[self.tab.current])
                self.__settitle()
        except:
            tm.showwarning('Warning', 'File open error')
            print('file open error')

    #保存文件
    def __savefile(self):
        if self.path[self.tab.current] == "":
            path = tf.asksaveasfilename(filetypes = [('TXT', '.txt'), ('Python', '.py')])
            if path != '':
                self.path[self.tab.current] = path
        try:
            with open(self.path[self.tab.current], 'wb') as f:
                data = self.text.gettext().encode('utf-8')
                f.write(data)
                #更新
                self.content[self.tab.current] = data
                self.sig[self.tab.current] = hashlib.md5(data).digest()
                self.change[self.tab.current] = False
                self.__settitle()
        except:
            tm.showwarning('Warning', 'File save error')
            print('file save error')

    #另存文件
    def __saveasfile(self):
        path = tf.asksaveasfilename(filetypes = [('TXT', '.txt'), ('Python', '.py')])
        if path != "":
            self.path[self.tab.current] = path
            self.__savefile()

    #新文件
    def __newfile(self):
        self.content.append('')
        self.path.append('')
        self.change.append(False)
        self.sig.append(hashlib.md5(''.encode('utf-8')).digest())
        self.mark.append('1.0')

    #切换文件
    def __changefile(self, old):
        if old != -1:
            self.content[old] = self.text.gettext()
            self.mark[old] = self.text.getinsert()
        self.text.settext(self.content[self.tab.current])
        self.text.setinsert(self.mark[self.tab.current])
        self.__settitle()

    #关闭文件
    def __closefile(self):
        if self.change[self.tab.current]:
            choice = tm.askyesnocancel('提示', '要保存吗？')
            if choice == True:
                self.__savefile()
            elif choice == None:
                return False
        del self.content[self.tab.current]
        del self.path[self.tab.current]
        del self.sig[self.tab.current]
        del self.change[self.tab.current]
        del self.mark[self.tab.current]
        return True

    #更换显示文件夹
    def __openfolder(self):
        path = tf.askdirectory()
        if path != '':
            self.workspace = path
            self.ftree.setTree(path)

    #查找文本
    def __findwindow(self):
        #新窗口
        findwin = tk.Toplevel(self.root)
        findwin.title('Find')
        findwin.attributes('-toolwindow', True)
        findwin.attributes('-topmost', True)
        findwin.resizable(0, 0)
        findwin.focus()
        findwin.bind('<Destroy>', lambda event:self.text.textwin.tag_remove('found', '1.0', 'end'))
        #输入框
        targettext = tk.Entry(findwin)
        targettext.pack()
        #查找按钮
        findbutton = tk.Button(findwin, text = 'find', command = lambda:self.text.findtext(targettext.get(), 'found'))
        findbutton.pack()

    #替换文本
    def __replacewindow(self):
        #新窗口
        replacewin = tk.Toplevel()
        replacewin.title('Replace')
        replacewin.attributes('-toolwindow', True)
        replacewin.attributes('-topmost', True)
        replacewin.resizable(0, 0)
        replacewin.focus()
        replacewin.bind('<Destroy>', lambda event:self.text.textwin.tag_remove('found', '1.0', 'end'))
        #查找内容
        targettext = tk.Entry(replacewin)
        targettext.pack()
        tk.Label(replacewin, text = '↓').pack()
        #替换内容
        replacetext = tk.Entry(replacewin)
        replacetext.pack()
        #查找按钮
        replacebutton = tk.Button(replacewin, text = 'replace', command = lambda:self.text.replacetext(targettext.get(), replacetext.get()))
        replacebutton.pack()

    #设置标签和窗口标题
    def __settitle(self):
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
    def __checktext(self):
        if self.change[self.tab.current] or self.tab.current == -1:
            return
        sig = hashlib.md5(self.text.gettext().encode('utf-8')).digest()
        if sig != self.sig[self.tab.current]:
            self.change[self.tab.current] = True
            self.__settitle()

    #退出
    def __editorquit(self):
        flag = True
        while len(self.tab.tabs) != 0:
            if not self.tab.tabremove(self.tab.tabs[0]):
                flag = False
                break
        if flag:
            self.root.quit()

    #多线程
    def threadfunc(self, func, *args):
        t = threading.Thread(target = func, args = args)
        t.setDaemon(True)
        t.start()

if __name__ == '__main__':
    editorgui().root.mainloop()