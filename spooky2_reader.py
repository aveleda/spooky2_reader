#!/usr/bin/env python3
#
# Copyright (c) 2022 Albino Aveleda <albino@skybion.com.br> <albino@bino.eng.br>
# Spooky2 RL Reader
# License: GPLv3
#
import tkinter as Tkinter
import tkinter.font as tkFont
from tkinter import ttk
from tkinter import filedialog as fd
import os.path as path
import re

# global variables
# tree_columns = ("match", "value", "database")
# tree_data = []
# tree_search = []
# tree = None
# match = {}
# matchFirst = {}
# fileGlobal = ""
VERSION = "1.4.0"

# Classes
class BfbClass():
    """ BFB class """

    def __init__(self) -> None:
        self.tree_columns = ("match", "value", "database")
        self.tree_data = []
        self.tree_search = []
        self.tree = None
        self.match = {}
        self.match_list = []
        self.matchFirst = {}
        self.file_list = []
        self.full_filename_list = []
        self.fileGlobal = ""


class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
            return "break"

    def on_close_release(self, event):
        """Called when the button is released"""
        if not self.instate(['pressed']):
            return

        element =  self.identify(event.x, event.y)
        if "close" not in element:
            # user moved the mouse off of the close button
            return

        index = self.index("@%d,%d" % (event.x, event.y))

        if self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                            ("active", "pressed", "!disabled", "img_closepressed"),
                            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                        })
                    ]
                })
            ]
        })
    ])


class MenuFuncs():
    """ Menu functions class"""
    
    def __init__(self, menubar, parent, bfb) -> None:
        self.parent = parent
        self.bfb = bfb
        # File menu
        filemenu = Tkinter.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open (Ctrl+O)", command=lambda: self.open_file())
        filemenu.add_command(label="Export as CSV", command=lambda: self.export_csv())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=parent.quit)
        # Edit Menu
        editmenu = Tkinter.Menu(menubar)
        menubar.add_cascade(label="Edit", menu=editmenu)
        editmenu.add_command(label="Copy (Ctrl+C)", command=lambda: self.copy_from_treeview())
        editmenu.add_separator()
        editmenu.add_command(label="Find (Ctrl+F)", command=lambda: self.search_str())
        editmenu.add_command(label="Reset Find (Ctrl+R)", command=lambda: self.clear_search())
        editmenu.add_separator()
        editmenu.add_command(label="Clean", command=lambda: self.clear_all())
        # Help menu
        helpmenu = Tkinter.Menu(menubar)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=lambda: self.about())
        # bind
        parent.bind("<Control-Key-o>", lambda x: self.open_file())
        parent.bind("<Control-Key-c>", lambda x: self.copy_from_treeview())
        parent.bind("<Control-Key-f>", lambda x: self.search_str())
        parent.bind("<Control-Key-r>", lambda x: self.clear_search())

    def open_file(self):
        #global fileGlobal, match

        filetypes = (('text files', '*.txt'), ('All files', '*.*'))

        filename = fd.askopenfilename(title='Open a report', filetypes=filetypes)
        if filename == '':
             return

        # full_filenames = fd.askopenfilenames(title='Open a report', filetypes=filetypes)
        # if full_filenames == '':
        #     return
        #parentWindow.config(cursor="watch")
        # for file_name in full_filenames:
        #     file = path.basename(file_name)
        #     bfb.file_list.append(file)
        #     bfb.full_filename_list.append(file_name)
        #     file = file[:file.rfind('.')]
        #     file = file[:6] + '...' if len(file) > 6 else file
        #     #parentWindow.wm_title("SRL Reader: " + file)
        #     #self.frame_abas.append(Frame(self.abas))
        #     #self.abas.add(self.frame_abas[-1], text=file)
        #     frame_abas = Frame(self.abas)
        #     parentWindow.abas.add(frame_abas, text=file)
        #     #self.frame_abas[-1].bind('Activate', parentWindow.wm_title(file))
        #     lines = bfb.readfile(file_name)
        #     match1, match2 = bfb.createDict(lines)
        #     tree_reg = bfb.loadTree()
        #     #self.build_tree(tree)
        # #pb.destroy()
        # parentWindow.config(cursor="arrow")
            
        self.bfb.fileGlobal = filename[:]
        lines = readfile(filename)
        createDict(lines)
        if tree != None:
            delete_tree()
        loadTree(match)
        build_tree(tree)
        file = path.basename(filename)
        self.parent.wm_title("SRL Reader: " + file)

    def export_csv(self):
        #global fileGlobal, match

        if self.bfb.fileGlobal == '':
            return
        filename = self.bfb.fileGlobal[:-3] + "csv"
        initial_path = path.dirname(filename)
        file = path.basename(filename)
        filetypes = (('CSV files', '*.csv'), ('text files', '*.txt'), ('All files', '*.*'))
        filename = fd.asksaveasfilename(title='Export CSV', filetypes=filetypes,
                                        initialfile=file, initialdir=initial_path)
        if filename == '':
            return
        with open(filename, 'w') as f:
            for key, value in sorted(match.items()):
                ind = key.rfind("(")
                database = key[ind + 1:-1]
                line = key[:ind - 1]
                f.writelines(line + ";" + str(value) + ";" + database + "\n")

    def copy_from_treeview(self):
        if self.bfb.fileGlobal == '':
            return
            
        curItem = tree.focus()
        #curItem = tree.selection()[0]
        
        self.parent.clipboard_clear()
        aux = list(tree.item(curItem).values())
        #seld.parent.clipboard_append(aux[2][0])
        aux = aux[2][0].lstrip()
        self.parent.clipboard_append(aux)
        self.parent.update()

    def search_str(self):
        if self.bfb.fileGlobal == '':
            return
        ctl = True
        while ctl:
            answer = Tkinter.simpledialog.askstring("Search", "Find what:",
                                    parent=self.parent)
            if (answer is None):
                return
            answer = answer.strip()
            if loadTreeSearch(answer):
                ctl = False
                build_tree_search(tree)
            else:
                noFind(answer)

    def clear_search(self):
        global fileGlobal

        if fileGlobal == '':
            return
        build_tree(tree)
 
    def clear_all(self):
        #global match, matchFirst, fileGlobal, tree_data
        match.clear()
        matchFirst.clear()
        self.bfb.tree_data.clear()
        self.fileGlobal = ""
        delete_tree()
        self.parent.wm_title("Spooky2 RL Reader")

    def about(self):
        msg = "Spooky2 Reverse Lookup Reader\n\nVersion: " + VERSION 
        msg = msg + "\n\nEnergia e Amor\nhttp://www.energiaeamor.com\n\nCopyright (C) 2022 Skybion"
        Tkinter.messagebox.showinfo(title="About", message=msg)

# Functions
def sortby(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    if col == "value":
        data = [(int(tree.set(child, col)), child) for child in tree.get_children('')]
    else:
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # reorder data
    data.sort(reverse=descending)
    for indx, item in enumerate(data):
        tree.move(item[1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
        command=lambda col=col: sortby(tree, col, int(not descending)))


def setup_widgets(columns):
    container = ttk.Frame()
    container.pack(fill='both', expand=True)

    # treeview with scrollbars
    tree = ttk.Treeview(columns=columns, show="headings")
    vsb = ttk.Scrollbar(orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    #tree.tag_configure('rowFolder', background='orange')
    #tree.tag_configure('rowFolder', background='#2C8BA9', foreground='#ffffff')
    tree.tag_configure('rowFolder', background='#49B1CC')
    tree.tag_configure('rowInsideFolder', background='#6FCACB')
    tree.tag_configure('rowOutsideFolder', background='#EFCFB8')
    tree.grid(column=0, row=0, sticky='nsew', in_=container)
    vsb.grid(column=1, row=0, sticky='ns', in_=container)
    hsb.grid(column=0, row=1, sticky='ew', in_=container)

    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)

    return tree


def build_tree(tree):
    delete_tree()
    for col in tree_columns:
        tree.heading(col, text=col.title(),
            command=lambda c=col: sortby(tree, c, 0))
        # tkFont.Font().measure expected args are incorrect according
        #     to the Tk docs
        tree.column(col, width=tkFont.Font().measure(col.title()))

    last = ""
    for item in tree_data:
        aux = item[0]
        auxFull = aux + " (" + item[2] + ")"
        auxFirst = aux.split()[0]
        #if auxFirst[-1] == ",":
        #    auxFirst = auxFirst[:-1]
        if int(matchFirst[auxFirst]) > int(match[auxFull]):
            if last == auxFirst:
                aux = item[0]
                aux = "     " + aux
                reg = (aux, item[1], item[2])
                tree.insert(folder, 'end', open=False, values=reg, tags='rowInsideFolder')
            else:
                last = auxFirst
                reg = (auxFirst, str(matchFirst[auxFirst]), '')
                folder = tree.insert('', 'end', open=False, values=reg, tags='rowFolder')
                aux = item[0]
                aux = "     " + aux
                reg = (aux, item[1], item[2])
                tree.insert(folder, 'end', open=False, values=reg, tags='rowInsideFolder')
        else:
            tree.insert('', 'end', open=False, values=item)

        # adjust columns lenghts if necessary
        for indx, val in enumerate(item):
            ilen = tkFont.Font().measure(val)
            if tree.column(tree_columns[indx], width=None) < ilen:
                tree.column(tree_columns[indx], width=ilen)


def build_tree_search(tree):
    delete_tree()
    for col in tree_columns:
        tree.heading(col, text=col.title(),
            command=lambda c=col: sortby(tree, c, 0))
        # tkFont.Font().measure expected args are incorrect according
        #     to the Tk docs
        tree.column(col, width=tkFont.Font().measure(col.title()))

    last = ""
    for item in tree_search:
        aux = item[0]
        auxFull = aux + " (" + item[2] + ")"
        auxFirst = aux.split()[0]
        if auxFirst[-1] == ",":
            auxFirst = auxFirst[:-1]
        tree.insert('', 'end', open=False, values=item, tags='rowOutsideFolder')

        # adjust columns lenghts if necessary
        for indx, val in enumerate(item):
            ilen = tkFont.Font().measure(val)
            if tree.column(tree_columns[indx], width=None) < ilen:
                tree.column(tree_columns[indx], width=ilen)


def delete_tree():
    global tree
    tree.delete(*tree.get_children())
    # for i in tree.get_children():
    #     tree.delete(i)



def readfile(filename):
    with open(filename, encoding="ISO-8859-1") as f:
        lines = (line.rstrip() for line in f)
        lines = (line for line in lines if line)
#       lines = (line.replace(":", "") for line in lines)
        lines = (re.sub('[,:]', "", line) for line in lines)
        lines = list(line for line in lines if line[:3] != "BFB")
    # remove header
    line = lines[0]
    while line[:5] != "-----":
        lines.pop(0)
        line = lines[0]
    lines.pop(0)
    return lines


def createDict(lines):
    global match, matchFirst

    match.clear()
    matchFirst.clear()
    for line in lines:
        indice = line.rfind("(")
        if (indice > 0) and (line.rfind("(SD)") == -1) and (line.rfind("(MW)") == -1):
            if line.rfind("Hz") > 0:
                line = line[:indice-1]
            previousCount = match.get(line, 0)
            match[line] = previousCount + 1
            # first name
            lineFirst = line.split()[0]
            if lineFirst[-1] == ",":
                lineFirst = lineFirst[:-1]
            previousCount = matchFirst.get(lineFirst, 0)
            matchFirst[lineFirst] = previousCount + 1
    return


def loadTree(varDict):
    tree_data.clear()
    for key, value in sorted(varDict.items()):
        ind = key.rfind("(")
        database = key[ind + 1:-1]
        line = key[:ind - 1]
        reg = (line, str(value), database)
        tree_data.append(reg)


def loadTreeSearch(word):
    global match

    tree_search.clear()
    aux = False
    for key, value in sorted(match.items()):
        ind = key.rfind("(")
        database = key[ind + 1:-1]
        line = key[:ind - 1]
        if word.lower() in key.lower(): 
            reg = (line, str(value), database)
            tree_search.append(reg)
            aux = True
    return aux


def noFind(msg):
    Tkinter.messagebox.showerror("Search", "Can't find the text:\n\"" + msg + "\"")


# Main
def main():

    bfb = BfbClass()
    
    root = Tkinter.Tk()
    root.wm_title("Spooky2 RL Reader")
    root.geometry("800x600")

    menubar = Tkinter.Menu(root)
    root.config(menu=menubar)
    root.option_add('*Dialog.msg.font', 'Helvica 11')
    menu = MenuFuncs(menubar, root, bfb)
    
    # filemenu = Tkinter.Menu(menubar)
    # menubar.add_cascade(label="File", menu=filemenu)
    # filemenu.add_command(label="Open (Ctrl+O)", command=lambda: openFile(root))
    # filemenu.add_command(label="Export as CSV", command=lambda: exportCsv())
    # filemenu.add_separator()
    # filemenu.add_command(label="Exit", command=root.quit)

    # editmenu = Tkinter.Menu(menubar)
    # menubar.add_cascade(label="Edit", menu=editmenu)
    # editmenu.add_command(label="Copy (Ctrl+C)", command=lambda: copy_from_treeview(root))
    # editmenu.add_separator()
    # editmenu.add_command(label="Find (Ctrl+F)", command=lambda: searchStr(root))
    # editmenu.add_command(label="Reset Find (Ctrl+R)", command=lambda: clearSearch())
    # editmenu.add_separator()
    # editmenu.add_command(label="Clean", command=lambda: clearAll(root))

    # root.bind("<Control-Key-o>", lambda x: openFile(root))
    # root.bind("<Control-Key-c>", lambda x: copy_from_treeview(root))
    # root.bind("<Control-Key-f>", lambda x: searchStr(root))
    # root.bind("<Control-Key-r>", lambda x: clearSearch())

    # helpmenu = Tkinter.Menu(menubar)
    # menubar.add_cascade(label="Help", menu=helpmenu)
    # helpmenu.add_command(label="About", command=lambda: about())

    #root.wm_iconname("mclist")

    bfb.tree = setup_widgets(bfb.tree_columns)
    root.mainloop()

if __name__ == "__main__":
    main()
