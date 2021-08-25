import tkinter as tk

class LabelText(tk.Frame):
    rowlabel = [] #存放所有Label
    func = None #文本改变回调函数
    sel_first = '' #选中文字index
    sel_last = '' #选中文字index
    flag_tab = False #是否输入tab
    flag_enter = False #是否输入enter
    flag_wrap = False #是否输入{, [, (, ", '
    language = "C" #语言
    def __init__(self, *args):
        super().__init__(*args)
        #上框架
        frame = tk.Frame(self)
        frame.pack(fill = tk.BOTH, expand = True)
        frame.pack_propagate(False)
        #Label
        self.canvas = tk.Canvas(frame, bd = 2, width = 50, height = 0, bg = '#F5F5F5', highlightthickness = 0)
        self.canvas.pack(side = tk.LEFT, fill = tk.Y)
        self.labelframe = tk.Frame(self.canvas, height = 0)
        self.canvas.create_window(0, 0, anchor = tk.NW, window = self.labelframe)
        self.__updateLabel(1)
        #文本框
        self.textwin = tk.Text(frame, wrap = tk.NONE, width = 0, height = 0, font = ('Consolas', 11), undo = True, relief = tk.FLAT)
        self.textwin.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        #滚动条
        yscroll = tk.Scrollbar(frame, command = self.__scrollCommand)
        yscroll.pack(side = tk.RIGHT, fill = tk.Y)
        xscroll = tk.Scrollbar(self, orient = tk.HORIZONTAL, command = self.textwin.xview)
        xscroll.pack(fill = tk.X)
        #设置及绑定
        self.textwin.config(xscrollcommand = xscroll.set, yscrollcommand = lambda *args:self.__scrollSet(yscroll, *args))
        self.textwin.bind('<<Modified>>', self.__checkText)
        self.textwin.bind('<KeyPress>', self.__keyPress)
        #高亮
        self.textwin.tag_config('sel', background = "#00FFFF", foreground = "#000000")
        self.textwin.tag_config('found', background = '#40E0D0')
        self.textwin.tag_config('special', foreground = "#4D3B8B")
        self.textwin.tag_config('function', foreground = '#FF4500')
        self.textwin.tag_config('num', foreground = '#FF4500')
        self.textwin.tag_config('string', foreground = '#008B8B')
        self.textwin.tag_config('annotation', foreground = '#8FBC8F')

    #Text改变时设置竖直滚动条和Label
    def __scrollSet(self, yscroll, *args):
        yscroll.set(*args)
        self.canvas.yview_moveto(format(yscroll.get()[0], '.5f'))

    #竖直滚动条控制Text和Label
    def __scrollCommand(self, *x):
        self.textwin.yview(*x)
        self.canvas.yview(*x)

    #文本改变
    def __checkText(self, event):
        if not self.textwin.edit_modified():
            return
        self.textwin.edit_modified(False)
        lines = len(self.getText().split('\n'))
        self.__updateLabel(lines)
        if self.func:
            self.func()
        self.__keyFeature()
        self.__highLight()

    #按键事件
    def __keyPress(self, key):
        c = key.char
        if c == '\t':
            self.textwin.config(autoseparators = False)
            self.flag_tab = True
        if c == '\r':
            self.textwin.config(autoseparators = False)
            self.textwin.edit_separator()
            self.flag_enter = True
        if c == '{' or c == '[' or c == '(' or c == '\'' or c == '\"':
            self.flag_wrap = True
            try:
                self.sel_first = self.textwin.index('sel.first')
                self.sel_last = self.textwin.index('sel.last')
            except:
                self.sel_first = self.textwin.index('insert')
                self.sel_last = self.sel_first
            self.textwin.edit_separator()

    #计算文字前空格
    def __countBlank(self, idx):
        ans = 0
        while self.textwin.get(idx, '%s+%dc' % (idx, 1)) == ' ':
            ans += 1
            idx = '%s+%dc' % (idx, 1)
        return ans

    #更新Label
    def __updateLabel(self, lines):
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
                        bg = '#F5F5F5', font = ('Consolas', 11), bd = 0, pady = 0, padx = 6, anchor = 'e'))
                    self.rowlabel[-1].pack()
            elif lines < n:
                for i in range(n - 1, lines - 1, -1):
                    self.rowlabel[i].pack_forget()
                    del self.rowlabel[i]

    #特殊键入
    def __keyFeature(self):
        c = self.textwin.get('insert-1c', 'insert')
        if c == '\t' and self.flag_tab:
            self.textwin.delete('insert-1c', 'insert')
            self.textwin.edit_separator()
            idx = self.textwin.index('insert').split('.')[1]
            for i in range(4 - int(idx) % 4):
                self.textwin.insert('insert', ' ')
            self.textwin.edit_separator()
            self.textwin.config(autoseparators = True)
            self.flag_tab = False
        elif c == '\n' and self.flag_enter:
            count = 0
            c = self.textwin.get('insert-2c', 'insert-1c')
            if c == ':' or c == '{':
                count += 4
            idx = self.textwin.index('insert') + '-1l'
            count += self.__countBlank(idx)
            for i in range(count):
                self.textwin.insert('insert', ' ')
            if self.textwin.get('insert', 'insert+1c') == '}':
                idx = self.textwin.search('{', 'insert', stopindex = '1.0', backwards = True)
                if idx:
                    count = self.__countBlank(idx + ' linestart')
                    idx = self.textwin.index('insert')
                    self.textwin.insert('insert', '\n')
                    for i in range(count):
                        self.textwin.insert('insert', ' ')
                    self.textwin.mark_set('insert', idx)
            self.textwin.edit_separator()
            self.textwin.config(autoseparators = True)
            self.flag_enter = False
        elif self.flag_wrap and (c == '{' or c == '[' or c == '(' or c == '\'' or c == '\"'):
            if c == '{':
                wrap = '}'
            elif c == '[':
                wrap = ']'
            elif c == '(':
                wrap = ')'
            else:
                wrap = c
            self.textwin.edit_undo()
            self.textwin.edit_separator()
            self.textwin.insert(self.sel_last, wrap)
            self.textwin.insert(self.sel_first, c)
            self.textwin.mark_set('insert', self.sel_last + '+1c')
            self.flag_wrap = False
            self.textwin.edit_separator()

    #高亮
    def __highLight(self):
        if self.language == 'C':
            match = r'(^|\W)int($|\W)|(^|\W)short($|\W)|(^|\W)long($|\W)|(^|\W)float($|\W)|(^|\W)double($|\W)|'
            match += r'(^|\W)char($|\W)|(^|\W)void($|\W)|(^|\W)unsigned($|\W)|(^|\W)signed($|\W)|(^|\W)enum($|\W)|'
            match += r'(^|\W)struct($|\W)|(^|\W)union($|\W)|(^|\W)return($|\W)|'
            match += r'(^|\W)if($|\W)|(^|\W)else($|\W)|(^|\W)for($|\W)|(^|\W)while($|\W)|(^|\W)do($|\W)|(^|\W)break($|\W)|(^|\W)continue($|\W)|'
            match += r'(^|\W)goto($|\W)|(^|\W)switch($|\W)|(^|\W)case($|\W)|(^|\W)default($|\W)|'
            match += r'(^|\W)auto($|\W)|(^|\W)extern($|\W)|(^|\W)register($|\W)|(^|\W)static($|\W)|'
            match += r'(^|\W)const($|\W)|(^|\W)sizeof($|\W)|(^|\W)typedef($|\W)|(^|\W)volatile($|\W)|'
            match += r'(^|\W)bool($|\W)|(^|\W)true($|\W)|(^|\W)false($|\W)|(^|\W)#include($|\W)|(^|\W)#define($|\W)'
        elif self.language == 'C++':
            match = r'(^|\W)int($|\W)|(^|\W)short($|\W)|(^|\W)long($|\W)|(^|\W)float($|\W)|(^|\W)double($|\W)|'
            match += r'(^|\W)char($|\W)|(^|\W)void($|\W)|(^|\W)unsigned($|\W)|(^|\W)signed($|\W)|(^|\W)enum($|\W)|'
            match += r'(^|\W)class($|\W)|(^|\W)struct($|\W)|(^|\W)union($|\W)|(^|\W)return($|\W)|(^|\W)new($|\W)|(^|\W)delete($|\W)|'
            match += r'(^|\W)if($|\W)|(^|\W)else($|\W)|(^|\W)for($|\W)|(^|\W)while($|\W)|(^|\W)do($|\W)|(^|\W)break($|\W)|(^|\W)continue($|\W)|'
            match += r'(^|\W)goto($|\W)|(^|\W)switch($|\W)|(^|\W)case($|\W)|(^|\W)default($|\W)|'
            match += r'(^|\W)auto($|\W)|(^|\W)extern($|\W)|(^|\W)register($|\W)|(^|\W)static($|\W)|(^|\W)inline($|\W)|'
            match += r'(^|\W)throw($|\W)|(^|\W)this($|\W)|(^|\W)virtual($|\W)|(^|\W)operator($|\W)|(^|\W)friend($|\W)|(^|\W)template($|\W)|'
            match += r'(^|\W)try($|\W)|(^|\W)public($|\W)|(^|\W)private($|\W)|(^|\W)protected($|\W)|(^|\W)asm($|\W)|(^|\W)catch($|\W)|'
            match += r'(^|\W)const($|\W)|(^|\W)sizeof($|\W)|(^|\W)typedef($|\W)|(^|\W)volatile($|\W)|'
            match += r'(^|\W)typename($|\W)|(^|\W)using($|\W)|(^|\W)namespace($|\W)|(^|\W)explicit($|\W)|'
            match += r'(^|\W)bool($|\W)|(^|\W)true($|\W)|(^|\W)false($|\W)|(^|\W)#include($|\W)|(^|\W)#define($|\W)'
        elif self.language == 'Java':
            match = r'(^|\W)byte($|\W)|(^|\W)int($|\W)|(^|\W)short($|\W)|(^|\W)long($|\W)|(^|\W)float($|\W)|'
            match += r'(^|\W)double($|\W)|(^|\W)boolean($|\W)|(^|\W)char($|\W)|(^|\W)void($|\W)|'
            match += r'(^|\W)static($|\W)|(^|\W)final($|\W)|(^|\W)const($|\W)|(^|\W)this($|\W)|(^|\W)class($|\W)|(^|\W)new($|\W)|'
            match += r'(^|\W)public($|\W)|(^|\W)private($|\W)|(^|\W)protected($|\W)|(^|\W)return($|\W)|'
            match += r'(^|\W)if($|\W)|(^|\W)else($|\W)|(^|\W)for($|\W)|(^|\W)while($|\W)|(^|\W)do($|\W)|(^|\W)break($|\W)|(^|\W)continue($|\W)|'
            match += r'(^|\W)import($|\W)|(^|\W)package($|\W)|(^|\W)implements($|\W)|(^|\W)interface($|\W)|'
            match += r'(^|\W)abstract($|\W)|(^|\W)assert($|\W)|(^|\W)case($|\W)|(^|\W)catch($|\W)|(^|\W)default($|\W)|'
            match += r'(^|\W)enum($|\W)|(^|\W)extends($|\W)|(^|\W)finally($|\W)|(^|\W)goto($|\W)|(^|\W)instanceof($|\W)|'
            match += r'(^|\W)native($|\W)|(^|\W)strictfp($|\W)|(^|\W)super($|\W)|(^|\W)switch($|\W)|(^|\W)synchronized($|\W)|'
            match += r'(^|\W)throw($|\W)|(^|\W)throws($|\W)|(^|\W)transient($|\W)|(^|\W)try($|\W)|(^|\W)volatile($|\W)|'
            match += r'(^|\W)true($|\W)|(^|\W)false($|\W)|(^|\W)null($|\W)'
        elif self.language == 'Python':
            match = r'(^|\W)True($|\W)|(^|\W)False($|\W)|(^|\W)None($|\W)|(^|\W)and($|\W)|(^|\W)or($|\W)|(^|\W)not($|\W)|'
            match += r'(^|\W)if($|\W)|(^|\W)else($|\W)|(^|\W)elif($|\W)|(^|\W)for($|\W)|(^|\W)while($|\W)|(^|\W)break($|\W)|(^|\W)continue($|\W)|'
            match += r'(^|\W)class($|\W)|(^|\W)def($|\W)|(^|\W)lambda($|\W)|(^|\W)pass($|\W)|(^|\W)return($|\W)|'
            match += r'(^|\W)raise($|\W)|(^|\W)try($|\W)|(^|\W)with($|\W)|(^|\W)except($|\W)|(^|\W)finally($|\W)|'
            match += r'(^|\W)assert($|\W)|(^|\W)as($|\W)|(^|\W)del($|\W)|(^|\W)global($|\W)|(^|\W)nonlocal($|\W)|'
            match += r'(^|\W)from($|\W)|(^|\W)import($|\W)|(^|\W)is($|\W)|(^|\W)in($|\W)|(^|\W)yield($|\W)|'
        else:
            return
        #函数
        match = r'(^|\W)\w+\(.*\)(.|\n)'
        self.findText(match, 'function', True)
        #数字
        match = r'(^|\W)-?\d+(\.\d+)?'
        self.findText(match, 'num', True)
        #字符串
        match = r'\'.*\'|\".*\"'
        self.findText(match, 'string')
        #注释
        if self.language == "C" or self.language == "C++" or self.language == "Java":
            match = r'//.*|/\*(.|\n)*\*/'
        elif self.language == "Python":
            match = r'\#.*|\'\'\'(.|\n)*\'\'\''
        self.findText(match, 'annotation')

    #获得文本
    def getText(self):
        return self.textwin.get('1.0', 'end')[:-1]

    #设置文本
    def setText(self, str):
        self.textwin.delete('1.0', 'end')
        self.textwin.insert('1.0', str)

    #改变语言
    def changeLan(self, lan):
        self.language = lan

    #获得光标位置，pos为偏移量
    def getInsert(self, pos = 0):
        if pos > 0:
            pos = '+' + str(pos) + 'c'
        elif pos < 0:
            pos = str(pos) + 'c'
        else:
            pos = ''
        return self.textwin.index('insert' + pos)

    #设置光标位置
    def setInsert(self, pos):
        self.textwin.mark_set('insert', pos)
        self.textwin.see('insert')

    #绑定文本改变事件
    def bindCheck(self, func):
        self.func = func

    #查找并设置tag
    def findText(self, str, tag, shrink = False):
        self.textwin.tag_remove(tag, '1.0', 'end')
        if str:
            idx = '1.0'
            while True:
                strCount = tk.StringVar()
                idx = self.textwin.search(str, idx, stopindex = 'end', regexp = True, count = strCount)
                if not idx:
                    break
                lastidx = '%s+%sc' % (idx, strCount.get())
                if shrink:
                    idx = self.textwin.search(r'\w', idx, stopindex = lastidx, regexp = True)
                    lastidx = self.textwin.search(r'[\w)]', lastidx, stopindex = idx, regexp = True, backwards = True) + '+1c'
                if tag == 'function':
                    lastidx = self.textwin.search('(', idx, stopindex = lastidx)
                self.textwin.tag_add(tag, idx, lastidx)
                idx = lastidx

    #替换
    def replaceText(self, str1, str2):
        self.textwin.tag_remove('found', '1.0', 'end')
        self.setText(self.getText().replace(str1, str2))

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x700')
    l = LabelText(root)
    l.pack(fill = tk.BOTH, expand = True)
    root.mainloop()
