# -*- coding: utf-8 -*-

import os

# Compatibility win <> lnx
try:
    import Tkinter as tk
    import Tkinter.filedialog as dialog
    import Tkinter.ttk as ttk
    print('using big tkinter (linux way)')
except ImportError:
    import tkinter as tk
    import tkinter.filedialog as dialog
    import tkinter.ttk as ttk
    print('using small tkinter (windows way)')

# Matplotlib for viewing
try:
    import matplotlib.pyplot as plt
    print('graphing can be done')
    can_graph = True
except ImportError:
    print('no graphing')
    can_graph = False

from ASE_Content import SysMon, ErrLog  # , ResultSet
#from ToolTip import ToolTip

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.active_sel = {
            'contact': '',
            'count': '',
            'index': 0,
            'location': '',
            'name': '',
            'number': '',
            'stats': '',
            'various': ''
        }
        self.await_load = False
        self.btn = {}
        self.curr_loc = ''
        self.form = {}
        self.mode = tk.IntVar(value=0)  # errorlog value active
        self.mode_opts = {}
        self.content = {}
        
        # ===================== (Main Menu + controls)
        self.active_sel['location'] = tk.Label(self.master, text='Location : {0}'.format(self.curr_loc))
        self.mode_opts['mode1'] = tk.Radiobutton(self.master, text='ASE Errorlog viewer', value=0, variable=self.mode, command=self.sm)
        self.mode_opts['mode2'] = tk.Radiobutton(self.master, text='ASE Sysmon file viewer', value=1, variable=self.mode, command=self.sm)
        self.mode_opts['mode3'] = tk.Radiobutton(self.master, text='ASE Sysmon directory viewer', value=2, variable=self.mode, command=self.sm)
        self.mode_opts['mode4'] = tk.Radiobutton(self.master, text='ASE Resultset viewer', value=3, variable=self.mode, command=self.sm)
        
        self.active_sel['location'].grid(row=0, column=0, columnspan=2, sticky='w')
        self.mode_opts['mode1'].grid(row=0, column=2)
        self.mode_opts['mode2'].grid(row=0, column=3)
        self.mode_opts['mode3'].grid(row=0, column=4)
        self.mode_opts['mode4'].grid(row=0, column=5)
        
        # ===================== (Button Menu)
        self.btn['open'] = tk.Button(self.master, text='open', command=self.sm)
        self.btn['expt'] = tk.Button(self.master, text='export', command=self.export)
        self.btn['prev'] = tk.Button(self.master, text='<', command=self.prev)
        self.btn['save'] = tk.Button(self.master, text='save')  # editing not yet implemented
        self.btn['next'] = tk.Button(self.master, text='>', command=self.next)
        self.btn['exit'] = tk.Button(self.master, text='quit', command=self.quit)
        self.btn['open'].grid(row=1, column=1, pady=5, sticky='nsew')
        self.btn['expt'].grid(row=1, column=2, pady=5, sticky='nsew')
        self.btn['prev'].grid(row=1, column=3, pady=5, sticky='nsew')
        self.btn['save'].grid(row=1, column=4, pady=5, sticky='nsew')
        self.btn['next'].grid(row=1, column=5, pady=5, sticky='nsew')
        self.btn['exit'].grid(row=1, column=6, pady=5, sticky='nsew')

        # ===================== (Fields list)
        self.form['content'] = ttk.Treeview(master, show='headings', selectmode='browse', height=4)
        self.form['content'].grid(row=2, column=0, columnspan=7, rowspan=3)

        # self.form['content'].bind("<Return>", lambda e: self.on_select)
        # self.form['content'].bind("<Double-1>", self.on_select)
        self.form['content'].bind("<<TreeViewSelect>>", self.on_select)
        # ToolTip(widget = self.form['content'], text = "Hover text!")
        # ===================== (Comment line)
        self.active_sel['stats'] = tk.Label(self.master, text='Total : {0} records'.format(self.active_sel['count']))
        self.active_sel['stats'].grid(row=5, column=0, columnspan=7, sticky='w')
        self.refresh()
        
    def sm(self):
        backup = self.curr_loc
        if self.mode.get() == 2:
            self.curr_loc = dialog.askdirectory()
        else:
            self.curr_loc = dialog.askopenfilename()
        if self.curr_loc:
            self.await_load = True
        else:
            if backup:
                self.curr_loc = backup  # reverting to previous value
        self.refresh()            

    def refresh(self):
        if self.await_load:
            self.form['content'].delete(*self.form['content'].get_children())
            if self.mode.get() == 3:
                print('will join')
            elif self.mode.get() == 2:
                no_files = 0
                for dir_path, dir_names, file_names in os.walk(os.path.abspath(self.curr_loc)):
                    for current in file_names:
                        self.content = SysMon()
                        self.content.load(os.path.join(dir_path, current))
                        # self.content.report()
                        no_files += 1
                        print('processed', current)  # represents just one row in csv
                print('Processed', no_files, 'files...')
            elif self.mode.get() == 1:
                self.form['content']['columns'] = ('section', 'statistic', 'current', 'measured')
                self.content = SysMon()
                self.content.load(self.curr_loc)
                self.form['content'].heading("section", text='Main section', anchor='w')
                self.form['content'].column("section", stretch="no")
                self.form['content'].heading("statistic", text='Main statistic', anchor='center')
                self.form['content'].column("statistic", stretch="yes")
                self.form['content'].heading("current", text='Current statistic', anchor='center')
                self.form['content'].column("current", stretch="yes")
                filename = self.content.source.split('/')[-1]
                self.form['content'].heading("measured", text='Measured value @' + filename, anchor='center')
                self.form['content'].column("measured", stretch="yes")
                for section, reported in self.content.dict.items():
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
            elif self.mode.get() == 0:
                self.content = ErrLog(self.curr_loc).content
                self.form['content']['columns'] = ('time', 'logged')
                self.form['content'].heading("time", text='Log Time', anchor='w')
                self.form['content'].column("time", stretch="no")
                self.form['content'].heading("logged", text='Message', anchor='center')
                self.form['content'].column("logged", stretch="yes")
                for timestamp, row in self.content.items():
                    self.form['content'].insert("", "end", values=[timestamp, row])

    def on_select(self, evt):
        w = evt.widget
        if w == self.form['content']:  # click in content box
            if w.selection():
                index = w.selection()[0]
                print(dir(w))
                print('you clicked', w.item(index)["text"])
                self.active_sel['index'] = value
                # TODO: need to change a lot more
        self.refresh()

    def prev(self):
        if self.contacts_lib:
            if self.active_sel['index'] > 1:
                self.active_sel['index'] -= 1

    def next(self):
        if self.contacts_lib:
            if self.active_sel['index'] < len(self.contacts_lib.dic):
                self.active_sel['index'] += 1

    def control(self):
        if (self.contacts_list.curselection()[0]+1) < len(self.contacts_lib.dic):
            self.active_sel['contact'] = self.contacts_lib.dic[int(self.active_sel['index'])]['FN']
            self.active_sel['number'] = self.contacts_lib.dic[int(self.active_sel['index'])]['TEL']
            self.form['f1_inp'].delete(0, 'end')
            self.form['f2_inp'].delete(0, 'end')
            self.form['f1_inp'].insert(20, self.active_sel['contact'])
            self.form['f2_inp'].insert(20, self.active_sel['number'])
            print('Setting', str(self.contacts_list.curselection()[0]+1), '>', str(self.active_sel['index']), 'record')
            self.contacts_list.selection_clear(0, "end")
            self.contacts_list.selection_set(int(self.active_sel['index'])-1)
            self.contacts_list.see(int(self.active_sel['index'])-1)
            self.contacts_list.activate(int(self.active_sel['index'])-1)
            self.contacts_list.selection_anchor(int(self.active_sel['index'])-1)
            # self.contacts_list.select_set(int(self.active_sel['index'])-1)
            # self.contacts_list.event_generate("<<ListboxSelect>>")

    def export(self):
        if self.contacts_lib:
            if self.mode.get():  # file mode, export to directory
                final_loc = dialog.askdirectory()
            else:
                final_loc = dialog.asksaveasfile(mode='w', defaultextension=".txt")
            if self.curr_loc != final_loc and final_loc:
                if self.mode.get():
                    self.contacts_lib.dic.export(final_loc)
                else:
                    self.contacts_lib.dic.merge(final_loc)

    def quit(self):
        self.master.destroy()


def data_collector():
    root = tk.Tk()
    root.title('SYBASE Collector')
    root.resizable(7, 5)
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
