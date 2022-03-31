#!/usr/bin/env python3
#
# Copyright 2022 Albino Aveleda <albino@bino.eng.br>
# summary report spooky2
#
import tkinter as Tkinter
import tkinter.font as tkFont
from tkinter import ttk
from tkinter import filedialog as fd
import os.path as path
import re

# global variables
tree_columns = ("match", "value", "database")
tree_data = []
tree = None
match = {}
matchFirst = {}
fileGlobal = ""
version = "1.0.1"


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


def setup_widgets():
    #global fileGlobal
    #msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
    #    padding=(10, 2, 10, 6),
    #    text="File: " + path.basename(fileGlobal))
    #msg.pack(fill='x')

    container = ttk.Frame()
    container.pack(fill='both', expand=True)

    # treeview with scrollbars
    tree = ttk.Treeview(columns=tree_columns, show="headings")
    vsb = ttk.Scrollbar(orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    #tree.tag_configure('rowFolder', background='orange')
    tree.tag_configure('rowFolder', background='#EFCFB8')
    tree.tag_configure('rowInsideFolder', background='#6FCACB')
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
        if auxFirst[-1] == ",":
            auxFirst = auxFirst[:-1]
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


def delete_tree():
    global tree
    tree.delete(*tree.get_children())
    # for i in tree.get_children():
    #     tree.delete(i)


def clearAll(parentWindow):
    global match, matchFirst, fileGlobal, tree_data
    match.clear()
    matchFirst.clear()
    tree_data.clear()
    fileGlobal = ""
    delete_tree()
    parentWindow.wm_title("Report Spooky2")


def readfile(filename):
    with open(filename, encoding="ISO-8859-1") as f:
        lines = (line.rstrip() for line in f)
        lines = (line for line in lines if line)
#        lines = (line.replace(":", "") for line in lines)
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


def openFile(parentWindow):
    global fileGlobal, match

    filetypes = (('text files', '*.txt'), ('All files', '*.*'))
    filename = fd.askopenfilename(title='Open a report', filetypes=filetypes)
    if filename == '':
        return
    fileGlobal = filename[:]
    lines = readfile(filename)
    createDict(lines)
    if tree != None:
        delete_tree()
    loadTree(match)
    build_tree(tree)
    file = path.basename(filename)
    parentWindow.wm_title(file)


def exportCsv():
    global fileGlobal, match

    if fileGlobal == '':
        return
    filename = fileGlobal[:-3] + "csv"
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

def searchStr(parentWindow):
    answer = Tkinter.simpledialog.askstring("Search", "Find what:",
                                parent=parentWindow)
    noFind(answer)
    return

def noFind(msg):
    Tkinter.messagebox.showerror("Search", "Can't find the text:\n\"" + msg + "\"")

def clearSearch():
    return

def about():
    msg = "Reverse Lookup from Spooky2\nEnergia & Amor\nVersion: " + version
    Tkinter.messagebox.showinfo(title="About", message=msg)
    return

def main():
    global tree

    root = Tkinter.Tk()
    root.wm_title("Report Spooky2")
    root.geometry("800x600")

    menubar = Tkinter.Menu(root)
    root.config(menu=menubar)

    filemenu = Tkinter.Menu(menubar)
    menubar.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Open", command=lambda: openFile(root))
    filemenu.add_command(label="Export as CSV", command=lambda: exportCsv())
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)

    editmenu = Tkinter.Menu(menubar)
    menubar.add_cascade(label="Edit", menu=editmenu)
    editmenu.add_command(label="Search", command=lambda: searchStr(root))
    editmenu.add_command(label="Reset search", command=lambda: clearSearch())
    editmenu.add_command(label="Clean", command=lambda: clearAll(root))

    helpmenu = Tkinter.Menu(menubar)
    menubar.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="About", command=lambda: about())
    
    #root.wm_iconname("mclist")

    tree = setup_widgets()
    root.mainloop()

if __name__ == "__main__":
    main()
