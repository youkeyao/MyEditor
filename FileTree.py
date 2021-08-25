import tkinter as tk
import tkinter.ttk as ttk
import os

class FileTree(tk.Frame):
    func_open = None
    def __init__(self, *args):
        super().__init__(*args)
        self.ftree = ttk.Treeview(self, show = 'tree')
        self.ftree.pack(fill = tk.BOTH, expand = True)
        self.ftree.bind('<Double-Button-1>', lambda event:self.treeClick())
        #样式
        style_ftree = ttk.Style()
        style_ftree.theme_use("clam")
        style_ftree.layout("Treeview.Item",
            [('Treeitem.padding', {'sticky': 'nswe', 'children': 
                [('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
                    ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                    ('Treeitem.text', {'side': 'left', 'sticky': ''}),
                ],
            })]
        )
        style_ftree.configure("Treeview", font = ("Verdana", 10))

    #显示文件夹内文件
    def __findFile(self, parent, rootpath):
        allpath = os.listdir(rootpath)
        file_path = []
        dir_path = []
        for f in allpath:
            f = rootpath + '/' + f
            if os.path.isfile(f):
                file_path.append(f)
            elif os.path.isdir(f):
                dir_path.append(f)
        for f in dir_path:
            p = self.ftree.insert(parent, len(self.ftree.get_children(parent)), text = f.split('/')[-1])
            self.__findFile(p, f)
        for f in file_path:
            p = self.ftree.insert(parent, len(self.ftree.get_children(parent)), text = f.split('/')[-1], values = f)

    def setTree(self, path):
        self.ftree.delete(*self.ftree.get_children())
        r = self.ftree.insert('', 0, text = path.split('/')[-1])
        self.__findFile(r, path)

    #选择文件
    def treeClick(self):
        item = self.ftree.selection()[0]
        path = self.ftree.item(item)['values']
        if path != '':
            if self.func_open:
                self.func_open(path[0])

    #绑定
    def bindTree(self, func_open):
        self.func_open = func_open

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('800x700')
    l = FileTree(root)
    l.pack(fill = tk.BOTH, expand = True)
    root.mainloop()