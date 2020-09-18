import tkinter as tk

class LabelText(tk.Frame):
    rowlabel = [] #存放所有Label
    func = None #文本改变回调函数
    def __init__(self, *args):
        super().__init__(*args)
        #上框架
        frame = tk.Frame(self)
        frame.pack(fill = tk.BOTH, expand = True)
        frame.pack_propagate(False)
        #Label
        self.canvas = tk.Canvas(frame, bd = 2, width = 50, height = 0, bg = 'white', highlightthickness = 0)
        self.canvas.pack(side = tk.LEFT, fill = tk.Y)
        self.labelframe = tk.Frame(self.canvas, height = 0)
        self.canvas.create_window(0, 0, anchor = tk.NW, window = self.labelframe)
        self.__updatelabel(1)
        #文本框
        self.textwin = tk.Text(frame, wrap = tk.NONE, width = 0, height = 0, font = ('Consolas', 11), undo = True, relief = tk.FLAT)
        self.textwin.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        #滚动条
        yscroll = tk.Scrollbar(frame, command = self.__scrollcommand)
        yscroll.pack(side = tk.RIGHT, fill = tk.Y)
        xscroll = tk.Scrollbar(self, orient = tk.HORIZONTAL, command = self.textwin.xview)
        xscroll.pack(fill = tk.X)
        #设置及绑定
        self.textwin.config(xscrollcommand = xscroll.set, yscrollcommand = lambda *args:self.__scrollset(yscroll, *args))
        self.textwin.bind('<<Modified>>', self.__checktext)

    #Text改变时设置竖直滚动条和Label
    def __scrollset(self, yscroll, *args):
        yscroll.set(*args)
        self.canvas.yview_moveto(format(yscroll.get()[0], '.5f'))

    #竖直滚动条控制Text和Label
    def __scrollcommand(self, *x):
        self.textwin.yview(*x)
        self.canvas.yview(*x)

    #文本改变
    def __checktext(self, event):
        self.textwin.edit_modified(False)
        lines = len(self.gettext().split('\n'))
        self.__updatelabel(lines)
        if self.func:
            self.func()
        #c = self.textwin.get('insert-1c', 'insert')
        #print(c)

    #更新Label
    def __updatelabel(self, lines):
        n = len(self.rowlabel)
        if lines == n:
            return
        else:
            size = (50, lines * 18)
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if self.labelframe.winfo_reqheight() != lines * 18:
                self.canvas.config(height = lines * 18)
            if lines > n:
                for i in range(n + 1, lines + 1):
                    self.rowlabel.append(tk.Label(self.labelframe, text = i, width = 4,
                        bg = 'white', font = ('Consolas', 11), bd = 0, pady = 0, padx = 6, anchor = 'e'))
                    self.rowlabel[-1].pack()
            elif lines < n:
                for i in range(n - 1, lines - 1, -1):
                    self.rowlabel[i].pack_forget()
                    del self.rowlabel[i]

    #获得文本
    def gettext(self):
        return self.textwin.get('1.0', 'end')[:-1]

    #设置文本
    def settext(self, str):
        self.textwin.delete('1.0', 'end')
        self.textwin.insert('1.0', str)

    #获得光标位置，pos为偏移量
    def getinsert(self, pos = 0):
        if pos > 0:
            pos = '+' + str(pos) + 'c'
        elif pos < 0:
            pos = str(pos) + 'c'
        else:
            pos = ''
        return self.textwin.index('insert' + pos)

    #设置光标位置
    def setinsert(self, pos):
        self.textwin.mark_set('insert', pos)
        self.textwin.see('insert')

    #绑定文本改变事件
    def bindcheck(self, func):
        self.func = func

    def findtext(self, str):
        self.textwin.tag_remove('found', '1.0', 'end')
        if str:
            idx = '1.0'
            while 1:
                idx = self.textwin.search(str, idx, nocase = 1, stopindex='end')
                if not idx:
                    break
                lastidx = '%s+%dc' % (idx, len(str))
                self.textwin.tag_add('found', idx, lastidx)
                idx = lastidx
            self.textwin.tag_config('found', foreground = 'yellow', background = 'light blue')

    def replacetext(self, str1, str2):
        self.textwin.tag_remove('found', '1.0', 'end')
        if str:
            idx = '1.0'
            while 1:
                idx = self.textwin.search(str1, idx, nocase = 1, stopindex='end')
                if not idx:
                    break
                lastidx = '%s+%dc' % (idx, len(str1))
                self.textwin.delete(idx, lastidx)
                lastidx = '%s+%dc' % (idx, len(str2))
                self.textwin.insert(idx, str2)
                self.textwin.tag_add('found', idx, lastidx)
                idx = lastidx
            self.textwin.tag_config('found', foreground = 'yellow', background = 'light blue')

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x700')
    l = LabelText(root)
    l.pack(fill = tk.BOTH, expand = True)
    root.mainloop()
