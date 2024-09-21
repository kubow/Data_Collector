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
    import matplotlib.dates as mdates
    print('... matplotlib imported, graphing can be done')
    can_graph = True
except ImportError:
    print('... matplotlib not found, no graphing')
    can_graph = False

from DbContent import SysMon, ErrLog, ResultSet, contains_vals, move_record
# from ToolTip import ToolTip
x = '~.-:'  # special string for decorating

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
        self.mode_opts['mode1'] = tk.Radiobutton(self.master, text='Errorlog viewer', value=0, variable=self.active['mode'], command=self.sm)
        self.mode_opts['mode2'] = tk.Radiobutton(self.master, text='Sysmon file viewer', value=1, variable=self.active['mode'], command=self.sm)
        self.mode_opts['mode3'] = tk.Radiobutton(self.master, text='Sysmon directory viewer', value=2, variable=self.active['mode'], command=self.sm)
        self.mode_opts['mode4'] = tk.Radiobutton(self.master, text='Resultset viewer', value=3, variable=self.active['mode'], command=self.sm)
        self.mode_opts['mode5'] = tk.Radiobutton(self.master, text='Resultset directory viewer', value=4, variable=self.active['mode'], command=self.sm)
        
        self.form['location'].grid(row=0, column=0, columnspan=3, sticky='we')
        self.mode_opts['mode1'].grid(row=0, column=3)
        self.mode_opts['mode2'].grid(row=0, column=4)
        self.mode_opts['mode3'].grid(row=0, column=5)
        self.mode_opts['mode4'].grid(row=0, column=6)
        self.mode_opts['mode5'].grid(row=0, column=7)
        
        # ===================== (Button Menu) same for every layout
        self.btn['inpt'] = tk.Entry(self.master, width=1, textvariable=self.active['filter'], justify='center')
        self.btn['open'] = tk.Button(self.master, text='open', command=self.sm)
        self.btn['expt'] = tk.Button(self.master, text='magic', command=self.export)
        self.btn['prev'] = tk.Button(self.master, text='<', command=self.prev)
        self.btn['save'] = tk.Button(self.master, text='save', command=self.save)  # editing not yet implemented
        self.btn['next'] = tk.Button(self.master, text='>', command=self.next)
        self.btn['exit'] = tk.Button(self.master, text='quit', command=self.quit)
        self.btn['inpt'].grid(row=1, column=0, columnspan=2, pady=5, sticky='nsew')
        self.btn['open'].grid(row=1, column=2, pady=5, sticky='nsew')
        self.btn['expt'].grid(row=1, column=3, pady=5, sticky='nsew')
        self.btn['prev'].grid(row=1, column=4, pady=5, sticky='nsew')
        self.btn['save'].grid(row=1, column=5, pady=5, sticky='nsew')
        self.btn['next'].grid(row=1, column=6, pady=5, sticky='nsew')
        self.btn['exit'].grid(row=1, column=7, pady=5, sticky='nsew')
        self.btn['inpt'].bind('<Key>',self.on_select)

        # ===================== (Fields list) differs with each mode
        self.form['content'] = ttk.Treeview(master, show='headings', selectmode='browse', height=4)
        self.form['content'].grid(row=2, column=0, columnspan=8, rowspan=11, sticky='nsew')
        s = ttk.Style()
        s.configure('Treeview', rowheight=40)
        # self.form['content'].bind("<Return>", lambda e: self.on_select)
        # self.form['content'].bind("<Double-1>", self.on_select)
        self.form['content'].bind("<<TreeViewSelect>>", self.on_select)
        # ToolTip(widget = self.form['content'], text = "Hover text!")
        # ===================== (Comment line) same for every layout
        self.active['stats'] = tk.Label(self.master, text=f'Total : {self.active["records"]} records')
        self.active['stats'].grid(row=14, column=0, columnspan=8, sticky='we')
        self.refresh()
        
    def sm(self):  # sWITCH mODE
        backup = self.active['location']
        if self.active['mode'].get() in (2, 4):
            self.active['location'] = dialog.askdirectory()
        else:
            self.active['location'] = dialog.askopenfilename()
        if self.active['location']:
            self.await_load = True  # magic flag
        elif backup:
            self.active['location'] = backup  # reverting to previous value
        self.refresh()            

    def refresh(self):  # after every change in layout
        if not self.await_load:
            return
        self.form['location']['text'] = f'Location : {self.active["location"]}'
        self.form['content'].delete(*self.form['content'].get_children())  # clear the form
        self.load_content()  # load content based on mode
        try:
            self.active["records"] = len(self.content.df)  # count number of records in data frame
        except AttributeError:
            self.active["records"] = len(self.content)  # count number of records in data frame
        except:
            print('what goes here, need to debug')
        self.active['stats']['text'] = f'Total : {self.active["records"]} records'
        self.await_load = False  # flag for initialize

        #final step is to fill the values to the form - 1. columns, 2. content
        if self.active['mode'].get() in (2, 3, 4):
            self.form['content']['columns'] = self.content.df.columns.to_list()
            for column in self.content.df.columns:
                self.form['content'].heading(column, text=column, anchor='center')
                if 'id' in str(column).lower():
                    self.form['content'].column(column, stretch="no")
                else:
                    self.form['content'].column(column, stretch="yes")
            for index, row in self.content.df.iterrows():
                self.form['content'].insert("", "end", values=row.to_list())
        elif self.active['mode'].get() == 1:
            self.form['content']['columns'] = ('section', 'statistic', 'current', 'measured')
            self.form['content'].heading("section", text='Main section', anchor='w')
            self.form['content'].column("section", stretch="no")
            self.form['content'].heading("statistic", text='Main statistic', anchor='center')
            self.form['content'].column("statistic", stretch="yes")
            self.form['content'].heading("current", text='Current statistic', anchor='center')
            self.form['content'].column("current", stretch="yes")
            filename = self.active['location'].split('/')[-1]
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
        elif self.active['mode'].get() == 0:
            self.form['content']['columns'] = ('time', 'logged')
            self.form['content'].heading("time", text='Log Time', anchor='w')
            self.form['content'].column("time", stretch="no")
            self.form['content'].heading("logged", text='Message', anchor='ne')
            self.form['content'].column("logged", stretch="yes")
            for timestamp, row in self.content.dic.items():
                self.form['content'].insert("", "end", values=[timestamp, '\n'.join(wrap(row, 150))])

    def load_content(self, debug=True):
        if self.active['mode'].get() == 4:  # build result set
            no_files = 0
            for dir_path, dir_names, file_names in os.walk(os.path.abspath(self.active['location'])):
                for current in file_names:
                    a = ResultSet(os.path.join(dir_path, current))
                    if no_files < 1:
                        self.content = ResultSet(a.df.iloc[:,-3:-2].transpose().to_dict(), direct=True)
                        self.content.df.columns = ["description", ]
                    self.content.df[a.time_stamp] = a.df.iloc[:,-1:]
                    no_files += 1
                    print('process', current, '- represents just one row in dataset')   
            print('Processed', no_files, 'files...')
        elif self.active['mode'].get() == 2:  # build sysmon set
            no_files = 0
            for dir_path, dir_names, file_names in os.walk(os.path.abspath(self.active['location'])):
                for current in file_names:
                    a = SysMon(os.path.join(dir_path, current))
                    if no_files < 1:
                        self.content = ResultSet(a.dic, direct=True)  
                        self.content.columns = ["description",]
                    else:
                        print(self.content[current]) # = a.dic  # TODO: need to test .tail(1).transpose()
                    no_files += 1
                    print('process', current, '- represents just one row in dataset')  
            self.active["records"] = no_files
            print('Processed', no_files, 'files...')
        elif self.active['mode'].get() == 3:
            self.content = ResultSet(self.active['location'])
        elif self.active['mode'].get() == 1:
            self.content = SysMon(self.active['location'])
        elif self.active['mode'].get() == 0:
            self.content = ErrLog(self.active['location'])
        #self.content.df.fillna('', inplace=True)

    def filter(self, string):  # TODO: repeating, need to use functions
        if string == self.active['apply']:
            return

        print('limit result set with', string, '/ previous value was', self.active['apply'])
        self.active['apply'] = string
        self.form['content'].delete(*self.form['content'].get_children())  # clear the widget
            # prepare content (stored in variable f)
        if self.active['mode'].get() == 4:
            # TODO: dynamicaly load description - name may differ
            f = self.content.df[self.content.df['description'].str.lower().str.contains(string)]
        elif self.active['mode'].get() == 3:
            f = self.content if any(self.content.df.columns) in string else self.content.df
        elif self.active['mode'].get() == 2:
            f = self.content
        elif self.active['mode'].get() == 1:
            f = self.content
        elif self.active['mode'].get() == 0:
            f = {key:value for (key,value) in self.content.dic.items() if string in value}
        # fill the widget with filtered data
        if isinstance(f, dict):
            for timestamp, row in f.items():
                self.form['content'].insert("", "end", values=[timestamp, '\n'.join(wrap(row, 150))])
        elif len(string) < 1:
            for index, row in f.iterrows():
                self.form['content'].insert("", "end", values=row.to_list())
        else:
            for index, row in f.iterrows():
                if string in row:
                    self.form['content'].insert("", "end", values=row.to_list())
        # do a sum-up
        self.active["records"] = len(f)
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

    # move_record from DbContent is not ready
    def prev(self):
        if contains_vals(self.content):
            self.active['index'] = move_record(self.content, self.active['index'], up=False)
        elif self.active['index'] > 1:
            self.active['index'] -= 1

    def next(self):
        if self.content and not self.content.empty:
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
        if self.active['mode'].get() in (2, 4):  # folder mode , plotting
            if self.form['content'].selection():
                if can_graph:
                    # TODO: this is not working....
                    #sel = int(self.form['content'].selection()[0][1:], 16)  
                    sel = self.form['content'].item(self.form['content'].selection()[0])['values'][0]
                    #magic = self.content.df.iloc[sel -1].to_frame()
                    magic = ResultSet(sel).df
                    serie_name = magic.iloc[0][magic.columns[-1]]
                    magic = magic[1:].astype('float')
                    #magic.astype(float)
                    magic.index.name = 'date'
                    magic.reset_index(inplace=True)
                    magic.rename(columns = {magic.columns[-1] : serie_name})  #, inplace=True)
                    magic[magic.columns[-1]].astype('float')
                    #magic[magic.columns[-1]].plot()
                    fig, ax = plt.subplots()
                    ax.plot(magic['date'], magic.iloc[:,-1:])
                    ax.set_xticks(magic['date'])
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m/%d %H:%M'))
                    _=plt.xticks(rotation=90)
                    #magic.plot(x='date', y=magic.columns[-1], marker="*")
                    #magic.plot(x=magic['date'], y=magic[magic.columns[-1]])  #, kind='scatter')
                    #magic.plot.line(y=magic[1])  #, kind='scatter')
                    plt.show()  #x_compat=True
            else:
                print('please select a row')
        elif self.active['mode'].get() == 3:
            for i, group in enumerate(self.content.df[0].unique()):  # transforming it to a CUBE by first field
                if i < 1:
                    a = self.content.df[self.content.df[0]==group].iloc[:,1:]
                    c = {
                        a.iloc[:,-1].name:str(group),
                        a.iloc[:,-2].name:'description',
                        a.iloc[:,1].name:'metric',
                        a.iloc[:,0].name:'id'
                    }
                    a.rename(columns=c, inplace=True)
                else:
                    a[str(group)]=self.content.df[self.content.df[0]==group].iloc[:,-1].values
                    a.rename(columns={a.iloc[:,-1].name:str(group)}, inplace=True)
            self.form['content'].delete(*self.form['content'].get_children())  # clear the form
            self.form['content']['columns'] = tuple(a.columns)  #ititiate tree view with new column set
            for col in a.columns:
                self.form['content'].heading(f'{col}', text=f'{col}', anchor='center')
                self.form['content'].column(f'{col}', stretch="yes")
            for index, row in a.iterrows():  # fill it with transposed values
                self.form['content'].insert("", "end", values=row.to_list())
            print(f'{x[0]*3} transforming data ')
        else:
            print('file mode magic ... what can be done here? report only upon errorlog?')

    def save(self):
        if not contains_vals(self.content):
            return
        if self.active['mode'].get() in (0, 1, 3):  # file mode, export to directory
            final_loc = dialog.askdirectory()
        else:
            final_loc = dialog.asksaveasfile(mode='w', defaultextension=".csv")
        if self.active['location'] != final_loc and final_loc:
            if self.active['mode'].get() in (2, 4):
                final_dataset = self.content.df.transpose()  #.loc[1:,-1]
                #final_dataset.to_csv(final_loc, encoding='cp1252', header=False, index=True, line_terminator='\n', mode='w')
                final_dataset.to_csv(final_loc.name, encoding='utf-8', header=False, index=True, line_terminator='\n', mode='w')
            else:
                final_dict = {}
                helper_dict = {}
                for i, col in enumerate(self.form['content']['columns']):
                    final_dict[col] = []
                    helper_dict[i] = col
                for child in self.form['content'].get_children():
                    for i, val in enumerate(self.form['content'].item(child)['values']):
                        final_dict[helper_dict[i]].append(val)
                ResultSet(final_dict, direct=True).write_csv(loc=final_loc, fn=self.active['location'])
                    # self.content.dic.merge(final_loc)
                    # self.content.dic.export(final_loc)

    def quit(self):
        self.master.destroy()


def data_collector():
    root = tk.Tk()
    root.title('SYBASE Collector')
    root.resizable(8, 15)
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
    #os.environ['NLS_LANG'] = '.AL32UTF8'
    data_collector()
