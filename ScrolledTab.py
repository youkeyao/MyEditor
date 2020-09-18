import tkinter as tk

class ScrolledTab(tk.Frame):
    tabs = [] #存放标签
    current = -1 #当前页
    func_click = None #点击回调函数
    func_remove = None #移除回调函数
    func_end = None #无标签回调函数
    func_add = None #增加回调函数
    def __init__(self, *args):
        super().__init__(*args)
        #框架
        self.tabcanvas = tk.Canvas(self, height = 20, bd = 0, highlightthickness = 0)
        self.tabcanvas.pack(fill = tk.X)
        self.tabframe = tk.Frame(self.tabcanvas, bg = 'white')
        self.tabframe.place(relx = 0, rely = 0, anchor = tk.NW)
        #绑定
        self.tabcanvas.bind('<Double-Button-1>', lambda event:self.tabadd())

    #滚动
    def __tabscroll(self, event):
        if self.tabcanvas.winfo_width() > self.tabframe.winfo_reqwidth():
            return
        movex = self.tabframe.winfo_x() + event.delta/6
        if movex > 0:
            movex = 0
        elif movex < self.tabcanvas.winfo_width() - self.tabframe.winfo_reqwidth():
            movex = self.tabcanvas.winfo_width() - self.tabframe.winfo_reqwidth()
        self.tabframe.place(x = movex)

    #增加标签
    def tabadd(self, text = ''):
        if self.func_add:
            self.func_add()
        self.tabs.append(tk.Label(self.tabframe, text = text, bg = 'dark grey', padx = 15))
        self.tabs[-1].pack(side = tk.LEFT, padx = 1)
        self.tabclick(self.tabs[-1])
        #绑定
        self.tabs[-1].bind('<Button-1>', lambda event:self.tabclick(event.widget))
        self.tabs[-1].bind('<Button-3>', lambda event:self.tabremove(event.widget))
        self.tabs[-1].bind('<MouseWheel>', self.__tabscroll)
        self.tabs[-1].bind('<Enter>', lambda event:event.widget.config(cursor = 'hand2'))
        self.tabs[-1].bind('<Leave>', lambda event:event.widget.config(cursor = 'arrow'))

    #点击标签
    def tabclick(self, tab):
        old = self.current
        n = self.tabs.index(tab)
        if self.current != -1:
            self.tabs[self.current].config(bg = 'dark grey')
        self.current = n
        if self.func_click:
            self.func_click(old)
        self.tabs[self.current].config(bg = 'white')

    #移除标签
    def tabremove(self, tab):
        n = self.tabs.index(tab)
        old = self.current
        self.tabclick(self.tabs[n])
        if self.func_remove:
            choice = self.func_remove()
            if not choice:
                return False
        self.tabs[n].pack_forget()
        del self.tabs[n]
        self.current = -1
        if n == old:
            if old == len(self.tabs):
                old = len(self.tabs) - 1
        elif n < old:
            old -= 1
        if old != -1:
            self.tabclick(self.tabs[old])
            return True
        elif self.func_end:
            self.func_end()

    #绑定
    def bindfunc(self, func_add, func_click, func_remove, func_end):
        self.func_add = func_add
        self.func_click = func_click
        self.func_remove = func_remove
        self.func_end = func_end

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('400x30')
    l = ScrolledTab(root)
    l.pack(fill = tk.BOTH)
    for i in range(1,5):
        l.tabadd(i)
    root.mainloop()
