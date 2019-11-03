"""Class definitions for the MCAP and Metrics objects."""

import numpy as np
import pandas as pd
import xlwings as xw
import datetime as dtt
from . import colcomp as cc
import time


class MCAPData:
    """An MCAP Data object.
    Attributes:
        file_path: the file location of the most recently pulled data or the
            location to save a new pull to
        df: a dataframe containing the information in the data file
        pivot_df: a pivot table df with the agg_func 'len', providing a
            count of unique VIDs
        
    Methods:
        .extract(): creates dataframe from the data file
        .fpivot(): creates a pivot table of mcap_df with agg_func 'len'
    """
    
    def __init__(self,mcap_path):
        self.file_path = mcap_path[0] #this replaces sdpath
        self.panel = mcap_path[1]
        self.df = 'blank' #this replaces sd
        self.pivot_df = 'blank' #used in indexcheck.mapping_loop()
        
    
    def extract(self):
        
        print('Extracting MCAP data... ',end=''),
        # with open(self.file_path,encoding='UTF-16') as f: #must call object attribute from within the object
        with open(self.file_path,encoding='UTF-8') as f: #must call object attribute from within the object
            
            #make sure to use parse_dates, or you'll get strings instead of sortable datetimes!
            # self.df = pd.read_csv(f,delimiter='\t',parse_dates=['WeekOf','BreakDt','EndDt','QCDt'], index_col=0)
            self.df = pd.read_csv(f,delimiter='\t',parse_dates=['WeekOf','BreakDt','EndDt','QCDt'], index_col=3)
        print('Done')
        return
        
    def fpivot(self):
        
        print('Creating pivot table (Count of VIDs)... ',end=''),
        # self.pivot_df = pd.pivot_table(self.df,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])
        self.pivot_df = pd.pivot_table(self.df,index=self.df.index,columns='WeekOf',values='Vehicleid', aggfunc=[len])
        print('Done')
        return


class PanelMetrics:
    """A Metrics object. 
    Attributes:
        file_path: the file location of the metrics spreadsheet
        df: a dataframe of the spreadsheet constructed after using .extract()
        volatile_column: the column header on the spreadsheet, default 'Spotfire Data'
        
    Methods:
        .extract(): creates a dataframe from the file path
        .connect_book(): connects to the metrics file for live editing
        .update_file(): updates the metrics file to match the information
            contained within the dataframe
    """
    
    def __init__(self, metrics_path):
        self.file_path = metrics_path
        self.df = 'blank'
        self.volatile_column = 'MCAP Data'
        self.book = 'blank'
        self.sheet = 'Sheet1'
        self.week_date = 'blank'
        self.cutoff_date = 0
        
    def extract(self):
        """Creates a dataframe self.df from the file path."""
        
        print('Extracting Metrics data... ',end=''),
        self.df = pd.read_excel(self.file_path, index_col=0)
        print('Done')
    
    def connect_book(self):
        """Connects to the metrics file for live editing."""
        
        print('Connecting to excel workbook... ',end=''),
        self.book = xw.Book(self.file_path)
        
        try: self.sheet = self.book.sheets[self.sheet]
        except:
            while True:
                sheet_name = input("""\tSheet name: """) or 'Sheet1'
                try:
                    self.sheet = self.book.sheets[sheet_name]
                    break
                except: #forgive me, Guido, for I have sinned
                    print('\tNo matching sheet name, please try again.')
                    continue
                    
        print('Connected')
        
    def update_file_column(self,col,filter_safe=0):
        """Updates the metrics file to match the information contained within
        the dataframe. If you are updating the document live with filters, use
        the filter-safe option, but be aware that this takes several orders of 
        magnitude longer than the unsafe option."""
        
        # invalid sheet catcher
        if self.sheet == 'blank':
            print('Error: please connect to an excel document first.')
            return
        
        # (x1,y1) are excel coordinates, (x2,y2) are dataframe coordinates
        # +2: numpy starts at 0 (+1), dataframe uses 1st column/row as indices (+1)
        y1 = int(np.where(self.df.columns == col)[0][0] + 2)
        y2 = col
        n = len(self.df.index)
        
        if filter_safe == 0: # vastly faster, but doesn't work if there are filters in the xl
            # newaxis because we need a 2D array to transpose it
            self.sheet.range((2,y1),(int(n),y1)).value = self.df[y2].fillna('#N/A').values[np.newaxis].T
            
        else: # 381x slower, but filling elementwise is filter-safe
            print('\tWriting filter-safe data, please be patient... ',end=''),
            
            for x1 in range(2,n,1):
                x2 = self.sheet.range((x1,1)).value
                data = self.df.loc[x2][y2]
                
                if np.isnan(data):
                    self.sheet.range((x1,y1)).value = '#N/A'
                else:
                    self.sheet.range((x1,y1)).value = data
            print('Done')
        
        #save the changes so that read_excel can pull the current metrics data
        self.book.save()
        if type(col) == dtt.datetime:
            print('\tWeek data updated.')
        elif type(col) == str:
            print('\tColumn %s updated.' % col)
        else:
            print('\tData updated.')
            
    def xl_col_sort(self,col):
        """https://msdn.microsoft.com/VBA/Excel-VBA/articles/range-sort-method-excel"""
        
        # +2 for index & 1-based excel arrays
        week_col = int(np.where(self.df.columns == self.week_date)[0][0] + 2)
        col_num = int(np.where(self.df.columns == col)[0][0] + 2)
        max_row = int(len(self.df.index) + 2)
        max_col = int(len(self.df.columns) + 2)
        
        self.sheet.range((2,1),(max_row,max_col)).api.Sort(
                                    Key1 = self.sheet.range((2,col_num)).api,
                                    Order1 = 1,
                                    Key2 = self.sheet.range((2,week_col)).api,
                                    Order2 = 1,
                                    Header = 1
                                    )
        return
    
class Troubleshooter:
    """Contains a dataframe and several functions related to generating a
    report of problems and missing ads, calculating expected ad dates, and
    troubleshooting with calls to the MCAP and AC databases."""
    
    def __init__(self, metrics):
        self.week_date = metrics.week_date
        self.cutoff_date = metrics.cutoff_date
        self.volatile_column = metrics.volatile_column
        self.resolved_count = 0
        self.unresolved_count = 0
        self.df = self.get_ts_subframe(metrics.df)
        
    def get_ts_subframe(self,df):
        """Takes the subset of the metrics dataframe that will be used for
        column comparison and troubleshooting."""
        
        dff = df[self.week_date,self.volatile_column,'Issue','Exp. Date','Exp. Lag','Phase']
        dff = cc.cutoff_filter(dff,self.week_date,self.cutoff_date)
        
        subframe = cc.status_filter(dff,self.week_date, status='not_int')
        
        return subframe
        
    def check_duplicates(self, metrics, df, A, B): # if B < A: A = B, report in Duplicates section
        cc.duplicate_items(metrics,A,B)
        return
        
    def check_resolved(self):
    
        status = ['Indexed', 'Review', 'Scraped', 'AC QC', 'Published', '?'] # #N/A is its own thing
        
        A = self.week_date
        B = self.volatile_column
        
        for i in range(0,len(status)):
            dff = cc.cutoff_filter(self.df)
            dff = cc.status_filter(dff, A, status[i])
            
        return
            
    def check_unresolved(self):
    
        status = ['Indexed', 'Review', 'Scraped', 'AC QC', 'Published', '?'] # #N/A is its own thing
        
        A = self.week_date
        B = self.volatile_column
        
        for i in range(0,len(status)):
            dff = cc.cutoff_filter(ts)
            dff = cc.status_filter(dff, A, status[i])
            
        return

class MetricsReport:
    """Turns information from a Troubleshooter object into a formatted, human-
    readable report and outputs it in a txt file."""
    
    def __init__(self, ts):
        self.panel = 'BevAl' # make this dependent on the initial MCAP read
        self.rundate = dtt.datetime.today()
        self.resolved_count = ts.resolved_count
        self.unresolved_count = ts.unresolved_count
        self.resolved = 0 # dictionary containing duplicates, insert/paper, etc
        self.unresolved = 0 # same as above but for unresolved issues
        self.header = self.mk_header(ts)
        self.contents = self.mk_contents(ts)
        self.detail_view = self.mk_detail_view(ts)
        
    def mk_header(self, ts):
        return
    
    def mk_contents(self, ts):
        return
        
    def mk_detail_view(self, ts):
        return
        
    def write_to_file(self):
        return