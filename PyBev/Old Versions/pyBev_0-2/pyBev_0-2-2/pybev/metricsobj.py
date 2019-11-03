"""Class definitions for the MCAP and Metrics objects."""

import numpy as np
import pandas as pd
import xlwings as xw
from . import colcomp as cc
from . import datecheck

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
        self.file_path = mcap_path #this replaces sdpath
        self.df = 'blank' #this replaces sd
        self.pivot_df = 'blank' #used in indexcheck.mapping_loop()
    
    def extract(self):
        with open(self.file_path,encoding='UTF-16') as f: #must call object attribute from within the object
            #make sure to use parse_dates, or you'll get strings instead of sortable datetimes!
            self.df = pd.read_csv(f,delimiter='\t',parse_dates=['WeekOf','BreakDt','EndDt','QCDt'], index_col=0)
        
        return
        
    def fpivot(self):
        self.pivot_df = pd.pivot_table(self.df,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])
        
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
        self.volatile_column = 'Spotfire Data' #used in indexcheck.map_to_metrics
        self.book = 'blank'
        self.sheet = 'blank'
        self.week_date = 'blank'
        
    def extract(self):
        """Creates a dataframe self.df from the file path."""
        
        self.df = pd.read_excel(self.file_path, index_col=0)
    
    def connect_book(self):
        """Connects to the metrics file for live editing."""

        self.book = xw.Book(self.file_path)
        while True:
            sheet_name = input("""\tSheet name (press enter for 'Sheet1'): """) or 'Sheet1'
            try:
                self.sheet = self.book.sheets[sheet_name]
                break
            except: #forgive me, Guido, for I have sinned
                print('\tNo matching sheet name, please try again.')
                continue
        print('\tConnected to excel workbook.')
        
    def update_file(self,filter_safe=0):
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
        y1 = int(np.where(self.df.columns == self.volatile_column)[0][0] + 2)
        y2 = self.volatile_column
        n = len(self.df.index)
        
        if filter_safe == 0: # vastly faster, but doesn't work if there are filters in the xl
            # newaxis because we need a 2D array to transpose it
            self.sheet.range((2,y1),(int(n),y1)).value = self.df[y2].fillna('#N/A').values[np.newaxis].T
            
        else: # 10x slower, but filling elementwise is filter-safe
            for x1 in range(2,n,1):
                x2 = self.sheet.range((x1,1)).value
                data = self.df.loc[x2][y2]
                
                if np.isnan(data):
                    self.sheet.range((x1,y1)).value = '#N/A'
                else:
                    self.sheet.range((x1,y1)).value = data
        
        #save the changes so that read_excel can pull the current metrics data
        self.book.save()
        print('\tFile updated.')
        
    # def monday_backup(self):
    #     if date = monday:
    #         save book to .Archive/ as datestring.xlsx
    
# class Troubleshooter:
#     """Contains a dataframe and several functions related to generating a
#     report of problems and missing ads, calculating expected ad dates, and
#     troubleshooting with calls to the MCAP and AC databases."""
#     
#     def __init__(self, metrics):
#         self.df = self.get_ts_subframe(metrics.df) # consider incorporating self.df assignment into method
#         self.week_date = metrics.week_date
#         self.vol_col = metrics.volatile_column
#         self.cutoff_date = datecheck.check_before_input()
#         self.resolved_count = 0
#         self.unresolved_count = 0
#         
#     def get_ts_subframe(self,df):
#         """Takes the subset of the metrics dataframe that will be used for
#         column comparison and troubleshooting."""
#         #need to slice horizontally to get only type(df[week_date]) is not int
#         subframe = df[self.week_date,self.vol_col,'Issue','Exp. Date','Exp. Lag','Phase']
#         return subframe
#         
#     def resolved_issues(self):
#         for i in range(0,x):
#             self.resolved_count += 1
#         return