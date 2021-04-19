# -*- coding: utf-8 -*-

import os
from textwrap import wrap

# Compatibility win <> lnx
try:
    import Tkinter as tk
    import Tkinter.filedialog as dialog
    import Tkinter.ttk as ttk
    print('... using big tkinter (linux way)')
except ImportError:
    import tkinter as tk
    import tkinter.filedialog as dialog
    import tkinter.ttk as ttk
    print('... using small tkinter (windows way)')

# Matplotlib for viewing
try:
    import matplotlib.pyplot as plt
    print('... matplotlib imported, graphing can be done')
    can_graph = True
except ImportError:
    print('... matplotlib not found, no graphing')
    can_graph = False

from DbContent import SysMon, ErrLog, ResultSet
# from ToolTip import ToolTip


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.active = {
            'apply': '',  # applied filter
            'filter': tk.StringVar(value=''),  # filter mode
            'index': 0,
            'location': '',
            'mode': tk.IntVar(value=0),  # main mode: error log value active
            'records': 0,  # total record count
            'stats': '',  # bottom line information label
        }
        self.await_load = False  # flag for preparing content
        self.btn = {}  # collection of buttons (one fake is input field)
        self.form = {}  # collection of main content
        self.mode_opts = {}  # collection of radio buttons
        self.content = {}  # this is main content in the form (searchable and exportable)
        self.original = {}
        # self.active['filter'].trace('w', self.filter)  # bind filter input with callback 
        
        # ===================== (Main Menu + controls) same for every layout
        self.form['location'] = tk.Label(self.master, text=f'Location : {self.active["location"]}')
        self.mode_opts['mode1'] = tk.Radiobutton(self.master, text='ASE/IQ/ASA Errorlog viewer', value=0, variable=self.active['mode'], command=self.sm)
        self.mode_opts['mode2'] = tk.Radiobutton(self.master, text='ASE Sysmon file viewer', value=1, variable=self.active['mode'], command=self.sm)
        self.mode_opts['mode3'] = tk.Radiobutton(self.master, text='ASE Sysmon directory viewer', value=2, variable=self.active['mode'], command=self.sm)
        self.mode_opts['mode4'] = tk.Radiobutton(self.master, text='ASE/IQ/ASA Resultset viewer', value=3, variable=self.active['mode'], command=self.sm)
        
        self.form['location'].grid(row=0, column=0, columnspan=3, sticky='we')
        self.mode_opts['mode1'].grid(row=0, column=3)
        self.mode_opts['mode2'].grid(row=0, column=4)
        self.mode_opts['mode3'].grid(row=0, column=5)
        self.mode_opts['mode4'].grid(row=0, column=6)
        
        # ===================== (Button Menu) same for every layout
        self.btn['inpt'] = tk.Entry(self.master, width=1, textvariable=self.active['filter'], justify='center')
        self.btn['open'] = tk.Button(self.master, text='open', command=self.sm)
        self.btn['expt'] = tk.Button(self.master, text='magic', command=self.export)
        self.btn['prev'] = tk.Button(self.master, text='<', command=self.prev)
        self.btn['save'] = tk.Button(self.master, text='save')  # editing not yet implemented
        self.btn['next'] = tk.Button(self.master, text='>', command=self.next)
        self.btn['exit'] = tk.Button(self.master, text='quit', command=self.quit)
        self.btn['inpt'].grid(row=1, column=0, pady=5, sticky='nsew')
        self.btn['open'].grid(row=1, column=1, pady=5, sticky='nsew')
        self.btn['expt'].grid(row=1, column=2, pady=5, sticky='nsew')
        self.btn['prev'].grid(row=1, column=3, pady=5, sticky='nsew')
        self.btn['save'].grid(row=1, column=4, pady=5, sticky='nsew')
        self.btn['next'].grid(row=1, column=5, pady=5, sticky='nsew')
        self.btn['exit'].grid(row=1, column=6, pady=5, sticky='nsew')
        self.btn['inpt'].bind('<Key>',self.on_select)

        # ===================== (Fields list) differs with each mode
        self.form['content'] = ttk.Treeview(master, show='headings', selectmode='browse', height=4)
        self.form['content'].grid(row=2, column=0, columnspan=7, rowspan=11, sticky='nsew')
        s = ttk.Style()
        s.configure('Treeview', rowheight=40)
        # self.form['content'].bind("<Return>", lambda e: self.on_select)
        # self.form['content'].bind("<Double-1>", self.on_select)
        self.form['content'].bind("<<TreeViewSelect>>", self.on_select)
        # ToolTip(widget = self.form['content'], text = "Hover text!")
        # ===================== (Comment line) same for every layout
        self.active['stats'] = tk.Label(self.master, text=f'Total : {self.active["records"]} records')
        self.active['stats'].grid(row=14, column=0, columnspan=7, sticky='we')
        self.refresh()
        
    def sm(self):  # sWITCH mODE
        backup = self.active['location']
        if self.active['mode'].get() == 2:
            self.active['location'] = dialog.askdirectory()
        else:
            self.active['location'] = dialog.askopenfilename()
        if self.active['location']:
            self.await_load = True
        else:
            if backup:
                self.active['location'] = backup  # reverting to previous value
        self.refresh()            

    def refresh(self):
        if self.await_load:
            self.form['location']['text'] = f'Location : {self.active["location"]}'
            self.form['content'].delete(*self.form['content'].get_children())
            if self.active['mode'].get() == 3:
                self.load_content(ResultSet(self.active['location']))
                self.form['content']['columns'] = self.content.data_frame.columns.to_list()
                #self.content.data_frame.fillna('', inplace=True)
                for column in self.content.data_frame.columns:
                    if 'id' in column.lower():
                        self.form['content'].heading(column, text=column, anchor='center')
                        self.form['content'].column(column, stretch="no")
                    else:
                        self.form['content'].heading(column, text=column, anchor='center')
                        self.form['content'].column(column, stretch="yes")
                for index, row in self.content.data_frame.iterrows():
                    self.form['content'].insert("", "end", values=row.to_list())
                self.active["records"] = len(self.content.data_frame)
                self.await_load = False
            elif self.active['mode'].get() == 2:
                no_files = 0
                for dir_path, dir_names, file_names in os.walk(os.path.abspath(self.active['location'])):
                    for current in file_names:
                        self.load_content(SysMon())
                        self.content.load(os.path.join(dir_path, current))
                        # self.content.report()
                        no_files += 1
                        print('process', current)  # represents just one row in csv
                print('Processed', no_files, 'files...')
                self.active["records"] = no_files
                self.await_load = False
            elif self.active['mode'].get() == 1:
                self.form['content']['columns'] = ('section', 'statistic', 'current', 'measured')
                self.load_content(SysMon())
                self.content.load(self.active['location'])
                self.form['content'].heading("section", text='Main section', anchor='w')
                self.form['content'].column("section", stretch="no")
                self.form['content'].heading("statistic", text='Main statistic', anchor='center')
                self.form['content'].column("statistic", stretch="yes")
                self.form['content'].heading("current", text='Current statistic', anchor='center')
                self.form['content'].column("current", stretch="yes")
                filename = self.content.source.split('/')[-1]
                self.form['content'].heading("measured", text='Measured value @' + filename, anchor='center')
                self.form['content'].column("measured", stretch="yes")
                for section, reported in self.content.dic.items():
                    for stat, sub in reported.items():
                        i = 0
                        definition = ''
                        for key, measured in sub.items():
                            if i == 0:
                                definition = measured
                                i += 1
                                continue
                            self.form['content'].insert("", "end", values=[section, stat, definition + ' ' + key, measured])
                            i += 1
                self.active["records"] = len(self.content.dic)
                self.await_load = False
            elif self.active['mode'].get() == 0:
                self.load_content(ErrLog(self.active['location']).dic)
                self.form['content']['columns'] = ('time', 'logged')
                self.form['content'].heading("time", text='Log Time', anchor='w')
                self.form['content'].column("time", stretch="no")
                self.form['content'].heading("logged", text='Message', anchor='ne')
                self.form['content'].column("logged", stretch="yes")
                for timestamp, row in self.content.items():
                    self.form['content'].insert("", "end", values=[timestamp, '\n'.join(wrap(row, 150))])
                self.active["records"] = len(self.content)
                self.await_load = False
            self.active['stats']['text'] = f'Total : {self.active["records"]} records'

    def load_content(self, object_content):
        if object_content:
            self.content = object_content
            self.original = {}

    def filter(self, string):
        if string != self.active['apply']:
            self.active['apply'] = string
            print('limit result set with', string, '/ previous value was', self.active['apply'])
            self.form['content'].delete(*self.form['content'].get_children())
            if not self.original:
                self.original = self.content
            if self.active['mode'].get() == 3:
                if any(self.content.data_frame.columns) in string:
                    print('column filter mdoe')
                else:
                    for index, row in self.content.data_frame.iterrows():
                        if string in row:
                            self.form['content'].insert("", "end", values=row.to_list())
            elif self.active['mode'].get() == 2:
                print('this mode not implemented for filtering')
            elif self.active['mode'].get() == 1:
                print('this mode not implemented for filtering')
            elif self.active['mode'].get() == 0:
                if not string:
                    self.content = self.original
                else:
                    self.content = {key:value for (key,value) in self.content.items() if string in value}
                for timestamp, row in self.content.items():
                    self.form['content'].insert("", "end", values=[timestamp, '\n'.join(wrap(row, 150))])
            self.active["records"] = len(self.content)
            self.active['stats']['text'] = f'Total : {self.active["records"]} records'

    def on_select(self, evt):
        w = evt.widget
        if w == self.form['content']:  # click in content box
            if w.selection():
                index = w.selection()[0]
                print(dir(w))
                print('you clicked', w.item(index)["text"])
                self.active['index'] = w.item(index)["text"]
                # TODO: need to change a lot more
        elif w == self.btn['inpt']:  # type in the input box
            if self.btn['inpt'].get():
                self.master.after(1000,lambda: self.filter(self.btn['inpt'].get()))
        self.refresh()

    def prev(self):
        if self.content:
            if self.active['index'] > 1:
                self.active['index'] -= 1

    def next(self):
        if self.content:
            if self.active['index'] < len(self.content.dic):
                self.active['index'] += 1

    def control(self):
        if (self.contacts_list.curselection()[0]+1) < len(self.content.dic):

            self.form['f1_inp'].delete(0, 'end')
            self.form['f2_inp'].delete(0, 'end')
            print('Setting', str(self.contacts_list.curselection()[0]+1), '>', str(self.active['index']), 'record')
            self.contacts_list.selection_clear(0, "end")
            self.contacts_list.selection_set(int(self.active['index'])-1)
            self.contacts_list.see(int(self.active['index'])-1)
            self.contacts_list.activate(int(self.active['index'])-1)
            self.contacts_list.selection_anchor(int(self.active['index'])-1)
            # self.contacts_list.select_set(int(self.active['index'])-1)
            # self.contacts_list.event_generate("<<ListboxSelect>>")

    def export(self):
        if self.content:
            if self.active['mode'].get():  # file mode, export to directory
                final_loc = dialog.askdirectory()
            else:
                final_loc = dialog.asksaveasfile(mode='w', defaultextension=".txt")
            if self.active['location'] != final_loc and final_loc:
                if self.active['mode'].get():
                    self.content.dic.export(final_loc)
                else:
                    self.content.dic.merge(final_loc)

    def quit(self):
        self.master.destroy()


def data_collector():
    root = tk.Tk()
    root.title('SYBASE Collector')
    root.resizable(7, 15)
    # root.geometry('1200x900')
    root.columnconfigure(0, weight=2)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.columnconfigure(3, weight=1)
    root.columnconfigure(4, weight=1)
    root.columnconfigure(5, weight=1)
    root.columnconfigure(6, weight=1)
    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=2)
    root.rowconfigure(3, weight=6)
    root.rowconfigure(4, weight=1)
    MainWindow(root)
    root['bg'] = '#49A'
    root.mainloop()

if __name__ == '__main__':
    data_collector()
