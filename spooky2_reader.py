#!/usr/bin/env python3
#
# Copyright (c) 2022 Albino Aveleda <albino@skybion.com.br> <albino@bino.eng.br>
# Spooky2 RL Reader
# License: GPLv3
#
#from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
from tkinter import Frame, Label
from tkinter import HORIZONTAL, ttk
from tkinter import filedialog as fd
#from tkinter.ttk import Progressbar
from tkinter.tix import Balloon
import os.path as path
import re
#from tktooltip import ToolTip

VERSION = "2.0.0"

# Classes

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


class Menu_Funcs():
    def readfile(self, filename):
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

    def build_tree(self):
        #delete_tree()
        for col in self.tree_columns:
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


    def build_tree_search(self):
        #delete_tree()
        for col in self.tree_columns:
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


    def createDict(self, lines):
        match = {}
        matchFirst = {}
        matchSecond = {}
        for line in lines:
            indice = line.rfind("(")
            if (indice > 0) and (line.rfind("(SD)") == -1) and (line.rfind("(MW)") == -1):
                if line.rfind("Hz") > 0:
                    line = line[:indice-1]
                previousCount = match.get(line, 0)
                match[line] = previousCount + 1
                # first name
                lineFirst = line.split()[0]
                lineSecond = line.split()[1]
                if lineFirst[-1] == ",":
                    lineFirst = lineFirst[:-1]
                previousCount = matchFirst.get(lineFirst, 0)
                matchFirst[lineFirst] = previousCount + 1
                if len(line.split()) > 3:
                    lineSecond = lineFirst + " " + lineSecond
                    previousCount = matchSecond.get(lineSecond, 0)
                    matchSecond[lineSecond] = previousCount + 1
        self.match_list.append(match)
        return matchFirst, matchSecond


    def loadTree(self):
        #tree_data.clear()
        tree_data = []
        for key, value in sorted(self.match_list[-1].items()):
            ind = key.rfind("(")
            database = key[ind + 1:-1]
            line = key[:ind - 1]
            reg = (line, str(value), database)
            tree_data.append(reg)
        return tree_data


    def openFile(self):
        filetypes = (('text files', '*.txt'), ('All files', '*.*'))
        full_filenames = fd.askopenfilenames(title='Open a report', filetypes=filetypes)
        if full_filenames == '':
            return
        #pb = Progressbar(parentWindow, orient=HORIZONTAL, length=200, mode='indeterminate')
        #pb.place(x=100, y=100)
        #pb.start()
        self.root.config(cursor="watch")
        for file_name in full_filenames:
            file = path.basename(file_name)
            self.file_list.append(file)
            self.full_filename_list.append(file_name)
            file = file[:file.rfind('.')]
            file = file[:6] + '...' if len(file) > 6 else file
            #parentWindow.wm_title("SRL Reader: " + file)
            #self.frame_abas.append(Frame(self.abas))
            #self.abas.add(self.frame_abas[-1], text=file)
            frame_abas = Frame(self.abas)
            self.abas.add(frame_abas, text=file)
            #self.frame_abas[-1].bind('Activate', parentWindow.wm_title(file))
            lines = self.readfile(file_name)
            match1, match2 = self.createDict(lines)
            tree_reg = self.loadTree()
            #self.build_tree(tree)
        #pb.destroy()
        self.root.config(cursor="arrow")
        return


    def exportCsv(self):
        if self.abas.index("end") == 0:
            return
        idx = self.abas.index("current")
        filename = self.full_filename_list[idx][:-3] + "csv"
        initial_path = path.dirname(filename)
        file = path.basename(filename)
        filetypes = (('CSV files', '*.csv'), ('text files', '*.txt'), ('All files', '*.*'))
        filename = fd.asksaveasfilename(title='Export CSV', filetypes=filetypes,
                                    initialfile=file, initialdir=initial_path)
        if filename == "":
            return

        with open(filename, 'w') as f:
            for key, value in sorted(self.match.items()):
                ind = key.rfind("(")
                database = key[ind + 1:-1]
                line = key[:ind - 1]
                f.writelines(line + ";" + str(value) + ";" + database + "\n")


    def change_state(self, *args):
        #t_nos=str(my_tabs.index(my_tabs.select()))
        idx = self.abas.index("current")
        self.root.title(self.file_list[idx])
    

    def close_state(self, *args):
        #t_nos=str(my_tabs.index(my_tabs.select()))
        idx = self.abas.index("current")
        del self.file_list[idx]
        self.root.title(self.file_list[idx])

    # def on_enter(self, event):
    #     self.l2.configure(text="Hello world")

    # def on_leave(self, event):
    #     self.l2.configure(text="")


    def about(self):
        msg = "Spooky2 Reverse Lookup Reader\n\nVersion: " + VERSION 
        msg = msg + "\n\nEnergia e Amor\n"
        msg = msg + "http://www.energiaeamor.com\n\nCopyright (C) 2022 Skybion"
        tk.messagebox.showinfo(title="About", message=msg)
        return


class App(Menu_Funcs):
    def __init__(self):
        #self.frame_abas = []
        self.file_list = []
        self.full_filename_list = []
        self.match_list = []
        self.root = root
        self.tree_columns = ("match", "value", "database")
        #self.abas = ttk.Notebook(self.root)
        self.abas = CustomNotebook(self.root)
        self.abas.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Cria evento TabChange
        self.abas.bind("<<NotebookTabChanged>>", self.change_state)
        self.abas.bind("<<NotebookTabClosed>>", self.close_state)
        #Create a tooltip
        #tip = Balloon(self.root)
        #Bind the tooltip with button
        #tip.bind_widget(self.abas,balloonmsg="test")
        #self.abas.bind("<<Enter>>", self.on_enter)
        #self.abas.bind("<<Leave>>", self.on_leave)
        #self.abas.pack()
        self.ws()
        #self.frames_ws()
        #self.widgets_frame()
        self.Menus()
        # create Loop
        root.mainloop()


    def ws(self):
        self.root.title("Spooky2 RL Reader")
        self.root.configure(background='#1e3743')
        self.root.geometry("800x640")
        self.root.resizable(True, True)
        #self.root.maxsize(width=800, height=700)
        self.root.minsize(width=500, height=300)


    def frames_ws(self):
        container = ttk.Frame()
        container.pack(fill='both', expand=True)


    def widgets_frame(self):
        #self.abas = ttk.Notebook(self.root);
        self.frame_aba1 = Frame(self.abas)
        self.frame_aba2 = Frame(self.abas)

        self.frame_aba1.configure(background= "gray")
        self.frame_aba2.configure(background= "lightgray")
        
        self.abas.add(self.frame_aba1, text= "Aba 1");
        self.abas.add(self.frame_aba2, text= "Aba 2")
        self.abas.place(relx = 0, rely= 0, relwidth = 0.98, relheight = 0.98)
        #self.abas.pack(side="bottom")

        self.label1 = Label(self.frame_aba1, text="trtrta");
        self.label1.pack(side = "top")


    def Menus(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        def Quit(): self.root.destroy()

        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open (Ctrl+O)", command=lambda: self.openFile())
        filemenu.add_command(label="Export as CSV", command=lambda: self.exportCsv())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)

        editmenu = tk.Menu(menubar)
        menubar.add_cascade(label="Edit", menu=editmenu)
        #editmenu.add_command(label="Copy (Ctrl+C)", command=lambda: copy_from_treeview(root))
        editmenu.add_separator()
        #editmenu.add_command(label="Find (Ctrl+F)", command=lambda: searchStr(root))
        #editmenu.add_command(label="Reset Find (Ctrl+R)", command=lambda: clearSearch())
        editmenu.add_separator()
        #editmenu.add_command(label="Clean", command=lambda: clearAll(root))

        root.bind("<Control-Key-o>", lambda x: self.openFile())
        #root.bind("<Control-Key-c>", lambda x: copy_from_treeview(root))
        #root.bind("<Control-Key-f>", lambda x: searchStr(root))
        #root.bind("<Control-Key-r>", lambda x: clearSearch())

        helpmenu = tk.Menu(menubar)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=lambda: self.about())

        self.root.option_add('*Dialog.msg.font', 'Helvica 11')


# Criando uma variavel para identificar a janela
root = tk.Tk()
App()