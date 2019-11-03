"""Class definitions for the MCAP and Metrics objects."""

import numpy as np
import pandas as pd
import xlwings as xw

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
            except: #forgive me
                print('\tNo matching sheet name, please try again.')
                continue
        print('\tConnected to excel workbook.')
        
    def update_file(self):
        """Updates the metrics file to match the information
            contained within the dataframe."""
        
        if self.sheet == 'blank':
            print('Error: please connect to an excel document first.')
            return
        x = len(self.df.index)
        # +2 = numpy starts at 0 (+1), dataframe uses 1st column as index (+1)
        y = np.where(self.df.columns == self.volatile_column)[0][0] + 2
        
        #we have to turn the 1D array into a 2D in order to transpose it.
        self.sheet.range((2,int(y)),(int(x),int(y))).value = self.df[self.volatile_column].fillna('#N/A').values[np.newaxis].T
        
        #save the changes so that read_excel can pull the current metrics data
        self.book.save()
        print('\tFile updated.')