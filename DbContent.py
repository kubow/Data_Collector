import csv
from datetime import datetime
import os.path
from os import walk
import sys
try:
    from pandas import read_csv, read_excel, read_fwf, DataFrame
except ImportError:
    print('!!! pandas library not found, cannot read csv and excel')


# import sqlite3
# import matplotlib.pyplot as mplt

class ErrLog:
    """ASA/ASE/IQ(TODO: MSSQL,PgSQL,MySQL) errorlog holder
    %err_log: path to the errorlog file
    output is aggregated by timestamps:
    # dic[key]: date-time stamp
    # dic[value]: multi-line connected in one string
    # application_type: TODO: sniff type of errorlog file
    # server_name: TODO: sniff running server name
    # license: TODO: sniff type of license and number of cores/seats"""
    def __init__(self, err_log=''):
        self.application_type = ''
        self.dic = {}
        self.enc = ''
        # TODO: add more encodings and make UnicodeDecodeError logic automatic
        self.encodings = ('utf-8', 'ISO-8859-1', 'ISO-8859-15')
        self.extensions = ('.txt', '.log', '.err')
        self.license = ''
        self.server_name = ''
        if err_log and any(ext in err_log for ext in self.extensions):
            self.process_lines(err_log) if not self.enc else self.process_lines(err_log, encoding=self.enc)
        else:
            print('not an error log file:', err_log)

    def plot():
        # TODO: make display categories
        print('errorlog cannot be plotted now')

    def process_lines(self, file, encoding=None):
        timestamp, backup = '', ''
        try:
            with open(file, 'r', encoding=encoding) as err_file:
                for line in err_file:
                    if timestamp:
                        backup = timestamp
                    line = line.strip().split(' ')
                    if 'I.' in line[0]:
                        line.pop(0)
                    timestamp = build_ts(line[0].split(':')[-1]+" "+line[1].split('.')[0])
                    if backup and backup == timestamp:
                        self.dic[timestamp] += '\n'+' '.join(line[2:])
                    else:
                        self.dic[timestamp] = ' '.join(line[2:]) 
        except IndexError:
            self.dic[timestamp] += '\n'+' '.join(line)  # this case appending to content
        except UnicodeDecodeError:
            err_file.close()  #re-run with different encoding
            if not self.enc:
                self.enc = self.encodings[0]
                print('... trying encoding:', self.encodings[0])
                self.process_lines(file, self.encodings[0])
            elif self.enc == self.encodings[0]:
                self.enc = self.encodings[1]
                print('... trying encoding:', self.encodings[1])
                self.process_lines(file, self.encodings[1])
            elif self.enc == self.encodings[1]:
                self.enc = self.encodings[2]
                print('... trying encoding:', self.encodings[2])
                self.process_lines(file, self.encodings[2])
            else:
                print('no other values for encoding')
        except:
            print(sys.exc_info()[0])  # exception add out of index


class ResultSet:
    """universal loader for text files using pandas dataframes
    %filename: full path to exported resultset
    %sep: fields sparator (default is >,<)
    """
    def __init__(self, filename='', sep=',', header=True):
        if filename:
            self.file_size = os.path.getsize(filename)
            self.file_name = os.path.basename(filename)
            self.columns = 1
            self.path = os.path.abspath(filename)
            if any(chr.isdigit() for chr in self.file_name.split('.')[0]):
                # TODO: SQL Anywhere specific ? Must be more conditions
                self.time_stamp = build_ts(self.file_name.split('.')[0])
                self.data_frame = read_csv(filename, sep=sep, header=None, quotechar="'", na_filter=False)
                # self.data_frame.iloc[0] = self.time_stamp
                # self.data_frame = self.data_frame.transpose()
                # self.data_frame.loc[:,-1]
                self.columns = len(self.data_frame.columns)
                # TODO: another types of datasets fits in here
            elif '.xls' in filename:
                self.data_frame = read_excel(filename)
            elif '.csv' in filename:
                self.data_frame = read_csv(filename, sep=sep, header=0, na_filter=False)
                self.columns = len(self.data_frame.columns)
            else:
                self.data_frame = read_fwf(filename)
        else:
            print('please provide a path to result set file')

    def plot(self, index_row):
        if isinstance(self.data_frame, DataFrame) and isinstance(index_row, int):
            self.data_frame.plot(x=self.data_frame.iloc[0], y=self.data_frame.iloc[index_row])

    def write_csv(self, csv=''):
        if csv:
            if os.path.isfile(csv):  # do not append header in case file exist
                self.data_frame.tail(1).to_csv(csv, mode='a', encoding='utf-8', header=False)
            else:
                self.data_frame.tail(3).head(1).to_csv(csv, mode='w', encoding='utf-8', header=False)
                self.data_frame.tail(1).to_csv(csv, mode='a', encoding='utf-8', header=False)
        else:
            self.data_frame.to_csv(self.file_name+'.csv', mode='w', encoding='utf-8')


class SysMon:
    """holds all symon sections in dict variable
    expects headered parameter - true writes columns and data - false just data"""
    def __init__(self, headered=False):
        self.source = ''
        self.ts = ''  # date time value
        self.wh = headered  # with header data
        self.server_name = ''  # main data server name (###_DS, ###_BS, ...)
        self.report_name = ''  # ### System Performance Report
        self.version = ''  # ###/(16.X, 15.X, ...)
        self.counter = {'columns': 0, 'items': 0, 'internal': 0, 'lines': 0, 'section_lines': 0}
        self.dic = {}
        self.valid = ['Kernel Utilization', 'Worker Process Management', 'Parallel Query Management', 'Task Management',
                      'Application Management', 'Transaction Profile', 'Transaction Management', 'Lock Management',
                      'Data Cache Management', 'NV Cache Management', 'Disk I/O Management', 'Network I/O Management']

    def load(self, filename):
        flag = {'subsection': False, 'next_line': False}
        self.source = filename
        with open(filename, 'r', encoding='utf-8') as sysmon_file:
            sec = Section()
            for line in sysmon_file:
                line = line.strip()
                if len(line) == 0:  # not interested in blank line
                    continue  # not eve counting them
                if '===' in line:  # this is section divider - re-init object
                    if self.counter['lines'] > 12:
                        if sec.finalize():
                            self.dic[sec.name[0]] = sec.stat  # backup to sysmon variable
                        self.counter['section_lines'] = 0
                        flag['subsection'] = False
                        sec = Section()
                    self.counter['lines'] += 1
                else:  # load everything in between
                    self.counter['section_lines'] += 1  # secondary section counter in advance
                    if self.counter['lines'] == 1:
                        self.counter['lines'] += 1
                        self.report_name = line
                    elif self.counter['lines'] < 14:
                        if 'Server Version' in line:
                            self.version = line.split('   ')[-1]
                        elif 'Sampling Started' in line:
                            self.ts = build_ts(line.split('   ')[-1])
                        elif 'Server Name' in line:
                            self.server_name = line.split('   ')[-1]
                    else:
                        sec.content[self.counter['section_lines']] = {'line': [x.strip() for x in line.split('  ') if x]}
                    self.counter['lines'] += 1
    
    def plot():
        print('not implemented yet')

    def report(self, file_type='csv'):
        print('*********', self.report_name, '(', self.server_name, '@', self.ts, ')', '***********')
        omit_sections = ['Worker Process Management', 'Task Management', 'Transaction Profile']
        if file_type == 'csv':
            # TODO: not always same count of columns, need to sort out!
            with open(os.path.join(self.source, 'report.csv'), 'a', newline='') as file:
                cswrt = csv.writer(file, delimiter=';')
                if self.wh:
                    header = ['timestamp', ]
                    for section, stats in self.dic.items():  # column name reporter
                        if not any(s in section for s in omit_sections):
                            for statistic, stat_detail in stats.items():
                                self.counter['items'] = 1
                                for stat_value, data_value in stat_detail.items():
                                    if self.counter['items'] > 1:
                                        header.append(section + ' ' + statistic + ' ' + stat_value)
                                    self.counter['items'] += 1
                    self.counter['columns'] = len(header)
                    cswrt.writerow(header)
                data = [self.ts, ]
                for section, stats in self.dic.items():
                    if not any(s in section for s in omit_sections):
                        for statistic, stat_detail in stats.items():
                            self.counter['items'] = 1
                            for stat_value, data_value in stat_detail.items():
                                if self.counter['items'] > 1:
                                    data.append(data_value.replace('% ', '').replace('.', ','))
                                self.counter['items'] += 1
                print(str(len(data)), 'items in row / vs', str(self.counter['columns']), 'column names')
                cswrt.writerow(data)
        elif file_type == 'json':
            # this is desired structure: [{'date': 'YYYY-mm-dd HH:MM:SS', 'var1': 'var1', ...}, {...}, ...]
            with open(os.path.join(self.source, 'report.json'), 'a') as stream:
                self.counter['items'] = 1
                item = '"{0}": "{1}"'
                if self.counter['items'] > 2:
                    stream.write('}}, {{' + item.format('date', self.ts))
                else:
                    stream.write('[{{' + item.format('date', self.ts))
                for section, stats in self.dic.items():
                    if not any(s in section for s in omit_sections):
                        for statistic, stat_detail in stats.items():
                            self.counter['internal'] = 1
                            for stat_value, data_value in stat_detail.items():
                                if self.counter['internal'] == 1:
                                    self.counter['internal'] += 1
                                    continue
                                if self.counter['items'] > 1:
                                    stream.write(', ' + item.format(statistic + ' ' + stat_value, data_value))
                                self.counter['items'] += 1
                                self.counter['internal'] += 1

                stream.write('}}]')
        else:
            print('no other mode implemented')


class Section:
    def __init__(self):
        self.content = {}
        self.name = ''  # as the Section name
        self.header = ()
        self.i_list = ()
        self.stat = {}

    def add_to_i_list(self, num):
        self.i_list = self.i_list + (num, )

    def finalize(self):
        flag = {'header': False, 'summary': False}  # in sense of expecting value
        for i, suspect in self.content.items():
            if i == 1:
                self.name = suspect['line']
                self.content[i]['indicate'] = 'section_name'
                self.add_to_i_list(i)
            elif i > 2 and '---' in suspect['line'][0]:
                if not flag['header']:
                    if 'Device Activity Detail' in self.content[i-1]['line']:
                        continue
                    elif 'CtlibController Activity' in self.content[i-1]['line']:
                        continue
                    elif 'Nonclustered Maintenance' in self.content[i-1]['line']:
                        continue
                    elif 'Statistics Summary' in self.content[i-1]['line'][0]:
                        continue
                    elif 'Tuning Recommendations' in self.content[i-1]['line'][0]:
                        continue
                    flag['header'] = True
                    self.content[i-1]['indicate'] = 'header'
                    self.add_to_i_list(i-1)
                    if (i+1) <= list(self.content)[-1]:
                        if 'Total' in self.content[i+1]['line'][0] or 'Committed' in self.content[i+1]['line'][0]:
                            self.content[i+1]['indicate'] = 'summary'  # +1 immediate summary
                            self.add_to_i_list(i+1)
                            flag['header'] = False
                    elif (i+4) <= list(self.content)[-1] and 'Total' in self.content[i+4]['line'][0]:
                        self.content[i+4]['indicate'] = 'summary'  # +1 immediate summary
                        self.add_to_i_list(i+4)
                        flag['header'] = False
                else:
                    if i == list(self.content)[-1]:
                        continue
                    if 'Server Summary' in self.content[i+1]['line']:
                        self.content[i+2]['indicate'] = 'summary'  # +2 is average
                        self.add_to_i_list(i+2)
                        flag['header'] = False
                    elif 'Pool Summary' in self.content[i + 1]['line']:
                        continue
                    elif 'Total' in self.content[i+1]['line'][0] or 'Committed' in self.content[i+1]['line'][0]:
                        self.content[i+1]['indicate'] = 'summary'  # +1 is actual total
                        self.add_to_i_list(i+1)
                        flag['header'] = False
        for i in self.i_list:
            if self.content[i]['indicate'] == 'header':
                if self.content[i]['line'][0] == 'per sec':
                    self.header = [self.content[i-2]['line'][0], ] + self.content[i]['line']
                else:
                    self.header = self.content[i]['line']
            elif self.content[i]['indicate'] == 'summary':
                self.stat[self.header[0]] = dict(zip(self.header, map(str, self.content[i]['line'])))
        if len(self.stat) > 0:
            return True
        else:
            return False


def contains_vals(variable):
    """universal finder for any values
    returns true if at least one value exist
    input can be:
    - panda's data frame
    - dictionary
    TODO: check also simple variables in last step
    """   
    if isinstance(variable, DataFrame):  
        if variable.empty:
            return False
        else:
            return True
    elif variable:
        return True
    else:
        return False

def move_record(variable, active, up=True):
    if isinstance(variable, DataFrame) and not variable.empty:
        if up:
            return True
        else:
            return False
    else:  # all other variable types
        if up:
            if active < len(variable):
                return True
        else:
            if len(variable) < active:
                return True

def build_ts(ts_value=None):
    """build timestamp value from a given string ts_value
    expects > < >_< or no date time separator
    TODO: watch for more exotic separators
    """ 
    try:
        ts_format = ''
        if ' ' in ts_value:
            sep = ' '
        elif '_' in ts_value:
            sep = '_'
        else:
            print('what is divider between date and time here?', ts_value)
        if sep=='_' and not isinstance(ts_value.split(sep)[0], int):
            ts_value = sep.join(ts_value.split(sep)[1:])  # cut-off forst part of string
        med = ts_value.split(sep)
        if len(med) == 2:
            ts_format = sep.join((fmt_ts(f_val=med[0]), fmt_ts(f_type='time', f_val=med[1])))
        elif len(med) > 2:
            ts_value = sep.join(med.split(sep)[-2:])
            ts_format = sep.join((fmt_ts(f_val=med[0]), fmt_ts(f_type='time', f_val=med[1]))) 
    except:
        # print(sys.exc_info()[1])
        return ts_value
    finally:
        if ts_format:
            return datetime.strptime(ts_value, ts_format)
        else:
            return ts_value


def fmt_ts(f_type='date', f_val=''):
    """get format of a time/date given by:
    f_type : input value type
    f_val  : input value
    """
    if f_type == 'date':
        if '/' in f_val:
            f_val = f_val.split('/')
            if len(f_val) == 3:
                return '%Y/%m/%d'
            elif len(f_val) == 2:
                return '%m/%d'
        elif '-' in f_val:
            f_val = f_val.split('-')
            if len(f_val) == 3:
                return '%Y-%m-%d'
            elif len(f_val) == 2:
                return '%m-%d'
        elif ',' in f_val:
            return '%b %d, %Y'
        else:
            return '%Y%m%d'
    elif f_type == 'time':
        if ':' in f_val:
            f_val = f_val.split(':')
            if len(f_val) == 3:
                return '%H:%M:%S'
            elif len(f_val) == 2:
                return '%H:%M'
        else:
            return '%H%M'

