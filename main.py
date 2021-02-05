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

from ASE_Content import SysMon  #, ErrLog, ResultSet

# Main logic and layout
class MainWindow:
    def __init__(self, master):
        self.master = master
        self.active_sel = {
            'contact': '',
            'index': 0,
            'location': '',
            'name': '',
            'number': '',
            'various': ''
        }
        self.await_load = False
        self.btn = {}
        self.curr_loc = ''
        self.form = {}
        self.mode = tk.IntVar(value=0)  # folder value active
        self.mode_opts = {}
        self.contacts_lib = ''
        
        # ===================== (Main Menu + controls)
        self.active_sel['location'] = tk.Label(self.master, text='Location : {0}'.format(self.curr_loc))
        self.mode_opts['mode1'] = tk.Radiobutton(self.master, text='ASE Errorlog viewer', value=True, variable=self.mode, command=self.set_err)
        self.mode_opts['mode2'] = tk.Radiobutton(self.master, text='ASE Sysmon file viewer', value=False, variable=self.mode, command=self.set_syf)
        self.mode_opts['mode3'] = tk.Radiobutton(self.master, text='ASE Sysmon directory viewer', value=False, variable=self.mode, command=self.set_syd)
        self.mode_opts['mode4'] = tk.Radiobutton(self.master, text='ASE Resultset viewer', value=False, variable=self.mode, command=self.set_res)
        
        self.active_sel['location'].grid(row=0, column=0, columnspan=2, sticky='w')
        self.mode_opts['mode1'].grid(row=0, column=2)
        self.mode_opts['mode2'].grid(row=0, column=3)
        self.mode_opts['mode3'].grid(row=0, column=4)
        self.mode_opts['mode4'].grid(row=0, column=5)
        
        # ===================== (Button Menu)
        self.btn['open'] = tk.Button(self.master, text='open', command=self.browse_dir)
        self.btn['expt'] = tk.Button(self.master, text='export', command=self.export)
        self.btn['prev'] = tk.Button(self.master, text='<', command=self.prev)
        self.btn['save'] = tk.Button(self.master, text='save')  # editing not yet implemented
        self.btn['next'] = tk.Button(self.master, text='>', command=self.next)
        self.btn['exit'] = tk.Button(self.master, text='quit', command=self.quit)
        self.btn['open'].grid(row=1, column=0, pady=5, sticky='nsew')
        self.btn['expt'].grid(row=1, column=1, pady=5, sticky='nsew')
        self.btn['prev'].grid(row=1, column=2, pady=5, sticky='nsew')
        self.btn['save'].grid(row=1, column=3, pady=5, sticky='nsew')
        self.btn['next'].grid(row=1, column=4, pady=5, sticky='nsew')
        self.btn['exit'].grid(row=1, column=5, pady=5, sticky='nsew')

        # ===================== (Contacts list)
        
        # ===================== (Fields list)
        self.form['content'] = ttk.Treeview(master, columns=('1', '2', '3'), show='headings')
        self.form['content'].grid(row=2, column=0, columnspan=6, rowspan=6)
        
        self.form['content'].heading('#1', text='blabla', anchor='w')
        self.form['content'].column('#1', stretch='yes')
        
        
        # TODO: 1. Switcher between folder and file mode still not working
        # TODO: 2. Exporting / Merging

        # self.set_dir()  # first app init is hardcoded to folder

    def set_err(self):
        if self.curr_loc:
            print('browsing folder', self.curr_loc)
        self.browse_dir()
        self.refresh()

    def set_syf(self):
        if self.curr_loc:
            print('setting file', self.curr_loc)
        self.browse_dir()
        self.refresh()
        
    def set_syd(self):
        if self.curr_loc:
            print('setting sysmon directory', self.curr_loc)
        self.browse_dir()
        self.refresh()
        
    def set_res(self):
        if self.curr_loc:
            print('setting general result file', self.curr_loc)
        self.browse_dir()
        self.refresh()    
        
    def browse_dir(self):
        backup = self.curr_loc
        if self.mode.get() == 2:
            self.curr_loc = dialog.askdirectory()
        else:
            self.curr_loc = dialog.askopenfilename()
        if self.curr_loc:
            self.await_load = False  #True
        else:
            self.curr_loc = backup  # reverting to previous value

    def refresh(self):
        try:
            if self.await_load:
                self.contacts_list.delete(0, 'end')
                for record in self.contacts_lib.dic.keys():
                    self.contacts_list.insert('end', str(record) + '. ' + self.contacts_lib.dic[record]['FN'])
                self.aait_load = False
            self.active_sel['location']['text'] = 'Location : {0}'.format(self.curr_loc)
        except AttributeError:
            print('no contacts library loaded')

    def on_select(self, evt):
        w = evt.widget
        if w == self.contacts_list:  # click in contact list
            if w.curselection():
                self.form['f1_inp'].delete(0, 'end')
                self.form['f2_inp'].delete(0, 'end')
                index = int(w.curselection()[0])
                value = int(w.get(index).split('.')[0])
                self.active_sel['index'] = value
                # TODO: need to change a lot more
        self.refresh()

    def which_mode(self):
        return False if self.mode.get() else True

    def prev(self):
        if self.contacts_lib:
            if self.active_sel['index'] > 1:
                self.active_sel['index'] -= 1
            self.control()

    def next(self):
        if self.contacts_lib:
            if self.active_sel['index'] < len(self.contacts_lib.dic):
                self.active_sel['index'] += 1
            self.control()

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


def diabled():
    directory = 'C:\\_Run\\Project\\CRa\\2021_w1'
    for dir_path, dir_names, file_names in os.walk(os.path.abspath(directory)):
        for sys_mon_file in file_names:
            if sys_mon_file.endswith('.out'):
                sys_mon_content = SysMon()
                sys_mon_content.load(os.path.join(dir_path, sys_mon_file))
                print('processed', sys_mon_file)  # represents just one row in csv
                # break # just one round now
    print('Processed', no_files, 'files...')
    
    
def data_collector():
    root = tk.Tk()

    root.title('Analyzátor SYBASE dat')
    root.resizable(10, 10)
    # root.geometry('1200x900')
    #root.columnconfigure(0, weight=2)
    #root.columnconfigure(1, weight=1)
    MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    data_collector()
