"""Class definitions for the MCAP and Metrics objects."""

import numpy as np
import pandas as pd
import xlwings as xw
import datetime as dtt
import time
from . import colcomp as cc
from . import datecheck as dc


class MCAPData:
    """An MCAP Data object.
    Attributes:
        file_path: the file location of the most recently pulled data or the
            location to save a new pull to
        panel: BevAl, NonFlash, etc.
        df: a dataframe containing the information in the data file
        pivot_df: a pivot table df with the agg_func 'len', providing a
            count of unique VIDs
        
    Methods:
        .extract(): creates dataframe from the data file
        .fpivot(): creates a pivot table of mcap_df with agg_func 'len'
        .fpivot_status(): filters data on Vehicle_Status and pivots
    """
    
    def __init__(self,mcap_path,ROP=False):
        self.file_path = mcap_path[0]
        self.panel = mcap_path[1]
        self.df = None
        self.pivot_df = None
        self.status_pivot_df = None
        self.ROP = ROP
        
    
    def extract(self):
        
        # with open(self.file_path,encoding='UTF-16') as f: #must call object attribute from within the object
        with open(self.file_path,encoding='UTF-8') as f: #must call object attribute from within the object
            
        #make sure to use parse_dates, or you'll get strings instead of sortable datetimes!
            self.df = pd.read_csv(f,delimiter='\t',parse_dates=['WeekOf','BreakDt','EndDt','QCDt'], index_col=3)
        
        return
        
    def fpivot(self):
        if self.ROP is False:
            print('Creating pivot table (Count of VIDs)... '),
            # self.pivot_df = pd.pivot_table(self.df,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])
            self.pivot_df = pd.pivot_table(self.df,index=self.df.index,columns='WeekOf',values='Vehicleid', aggfunc=[len])
            print(' Done')
        elif self.ROP is True:
            print('Creating pivot table (Count of FIDs)... '),
            # self.pivot_df = pd.pivot_table(self.df,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])
            self.pivot_df = pd.pivot_table(self.df,index=self.df.index,columns='WeekOf',values='flyerid', aggfunc=[len])
            print(' Done')
        return
        
    def fpivot_status(self,status):
        print('Creating pivot table (Count of %s ads)...' % status, end=''),
        
        #not_QCC data has no WeekOf, need to construct it manually
        weekof_i = np.where(self.df.columns == 'WeekOf')[0][0]
        breakdt_i = np.where(self.df.columns == 'BreakDt')[0][0]
        for x in range(0,len(self.df.index)):
            self.df.iloc[x,weekof_i] = dc.sunday_date(self.df.iloc[x,breakdt_i])
            
        dff = self.df[self.df['Vehicle_Status'] == status]
        
        if self.ROP is False:
            self.status_pivot_df = pd.pivot_table(dff,index=dff.index,columns='WeekOf',values='Vehicleid',aggfunc=[len])
        if self.ROP is True:
            self.status_pivot_df = pd.pivot_table(dff,index=dff.index,columns='WeekOf',values='flyerid',aggfunc=[len])
        self.status_pivot_df = self.status_pivot_df.fillna(0)
        print(' Done')
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
        .update_file_column(): updates the metrics file to match the information
            contained within the dataframe
        .xl_col_sort(): sorts the sheet by a given column ascending
        .wipe_volatile_data(): sets volatile column data to 0s
    """
    
    def __init__(self, metrics_path,panel):
        self.file_path = metrics_path
        self.df = None
        self.week_date = None
        self.volatile_column = 'MCAP Data'
        self.cutoff_date = None
        self.book = None
        self.sheet = None
        self.panel = panel
        self.sheet_name = None
    
    def connect_book(self,default_sheet=None):
        """Connects to the metrics file for live editing."""
        print('Connecting to excel workbook...')
        self.book = xw.Book(self.file_path)
        
        if default_sheet is not None:
            self.sheet_name = default_sheet
            self.sheet = self.book.sheets[self.sheet_name]
            return
        
        try: self.sheet = self.book.sheets['Sheet1']
        except:
            while True:
                self.sheet_name = input("""\n\tSheet name: """) or 'Sheet1'
                try:
                    self.sheet = self.book.sheets[self.sheet_name]
                    break
                except: #forgive me, Guido, for I have sinned
                    print('\tNo matching sheet name, please try again.')
                    continue
                    
        print(' Done')
        
            
    def extract(self):
        """Creates a dataframe self.df from the file path."""
        try:
            self.df = pd.read_excel(self.file_path, sheet_name=self.sheet_name, index_col=0)
            self.df = self.df[self.df.index.fillna('NaN') != 'NaN']
        except AttributeError:
            print('No sheet name selected, please run stage 1 again.')
        
    def update_file_column(self,col,filter_safe=0):
        """Updates the metrics file to match the information contained within
        the dataframe. If you are updating the document live with filters, use
        the filter-safe option, but be aware that this takes several orders of 
        magnitude longer than the unsafe option."""
        
        # invalid sheet catcher
        if self.sheet == None:
            print('Error: please connect to an excel document first.')
            return
        
        # (x1,y1) are excel coordinates, (x2,y2) are dataframe coordinates
        # (+2): numpy starts at 0 (+1), dataframe uses 1st column/row as indices (+1)
        y1 = int(np.where(self.df.columns == col)[0][0] + 2)
        y2 = col
        n = len(self.df.index)
        
        if filter_safe == 0: # vastly faster, but doesn't work if there are filters in the xl
            # call newaxis because we need a 2D array to transpose it
            self.sheet.range((2,y1),(int(n),y1)).value = self.df[y2].fillna('#N/A').values[np.newaxis].T
            
        else: # 381x slower, but filling elementwise is filter-safe
            print('\tWriting filter-safe data, please be patient... ')
            
            for x1 in range(2,n,1):
                x2 = self.sheet.range((x1,1)).value
                data = self.df.loc[x2,y2]
                
                try:
                    if np.isnan(data):
                        self.sheet.range((x1,y1)).value = '#N/A'
                    else:
                        self.sheet.range((x1,y1)).value = data
                except TypeError:
                    self.sheet.range((x1,y1)).value = data
                    
            print(' Done')
        
        #save the changes so that read_excel can pull the current metrics data
        self.book.save()
        if type(col) == dtt.datetime:
            print('\tWeek data updated.')
        elif type(col) == str:
            print('\tColumn "%s" updated.' % col)
        else:
            print('\tData updated.')
            
    def wipe_volatile_data(self):
        col_num = int(np.where(self.df.columns == self.volatile_column)[0][0] + 2)
        max_row = int(len(self.df.index) + 1)
        self.sheet.range((2,col_num),(max_row,col_num)).api.value = 0
    
        self.book.save()
        return
            
    def xl_col_sort(self,key1='Exp. Date',key2='Media',key3=None):
        """Sorts the Metrics document by 3 columns, all ascending. Defaults to
        sorting Exp Date, Media, and Active Week (ie the ad count) in that order.
        
        VBA documentation:
        https://msdn.microsoft.com/VBA/Excel-VBA/articles/range-sort-method-excel"""
        
        if key3 is None: # workaround for default method kwarg using attribute
            key3 = self.week_date
        
        # +2 due to df index & 1-based excel arrays
        key1_col_num = int(np.where(self.df.columns == key1)[0][0] + 2)
        key2_col_num = int(np.where(self.df.columns == key2)[0][0] + 2)
        key3_col_num = int(np.where(self.df.columns == key3)[0][0] + 2)
        max_row = int(len(self.df.index) + 2)
        max_col = int(len(self.df.columns) + 2)
        
        self.sheet.range((2,1),(max_row,max_col)).api.Sort(
                                    Key1 = self.sheet.range((2,key1_col_num)).api,
                                    Order1 = 1,
                                    Key2 = self.sheet.range((2,key2_col_num)).api,
                                    Order2 = 1,
                                    Key3 = self.sheet.range((2,key3_col_num)).api,
                                    Order3 = 2,
                                    Header = 1
                                    )
        return
    
class Ticket:
    """A troubleshooting ticket that will be printed out with the report in
    stage 5. Contains all automatable information about a given issue, including
    relevant troubleshooting attempts and suggested actions."""
    
    def __init__(self,mcap,metrics,RetMkt,status):
        # Metrics details
        self.RetMkt = RetMkt
        self.retailer = mcap.df.loc[RetMkt]['Retailer'].values[-1]
        self.market = mcap.df.loc[RetMkt]['Market'].values[-1]
        self.status = status
        self.exp_date = metrics.df.loc[RetMkt]['Exp. Date']
        self.sender = mcap.df.loc[RetMkt]['Sender'].values[-1]
        self.media = metrics.df.loc[RetMkt]['Media']
        self.ret_website = metrics.df.loc[RetMkt]['Website Link']
        
        # Ticket ID
        self.RU = None
        self.media_abbv = None
        self.tick_name = None
        self.tick_num = None
        self.tick_ID = None
        self.abbv_func()
        self.name_gen()
        
        # Duplicate Information
        self.original_ad_count = None
        self.revised_ad_count = None
        
        # MCAP Information
        self.ads_present = None
        self.ads_expected = None
        self.days_overdue = None
        self.VID_status_count = {}
        self.VID_list = {}
        self.last_package_dt = None
        self.last_package_EID = None
        
        # AC Information
        self.AC_Retailer = None
        self.AC_Market = None
        self.storeID = None
        self.last_scrape_dt = None
        self.circular_status = None
        self.last_scrape_path = None
        
        # Issue Information
        self.known_issue = metrics.df.loc[RetMkt]['Issue']
        self.recommended_action = None
        self.descrip = None
        
    def abbv_func(self):
        media = self.media
        
        if media == r'Client-1':
            self.media_abbv = 'P1C'
        elif media == r'Client-2':
            self.media_abbv = 'P2C'
        elif media == r'Scrape-1':
            self.media_abbv = 'P1S'
        elif media == r'Scrape-2':
            self.media_abbv = 'P2S'
        elif media == r'Insert/Paper':
            self.media_abbv = 'IP'
        elif media == r'JA DL':
            self.media_abbv = 'JADL'
        else:
            self.media_abbv == 'UKWN'
            print('\t %s has unknown media type.' % self.RetMkt)
        return
            
    def name_gen(self):
        self.tick_name = '%s - %s - %s' % (
            self.retailer,
            self.market,
            self.exp_date.strftime('%m/%d/%Y')
            )
    
    def ID_gen(self):
        self.tick_ID = '%s-%s-%d' % (
            self.RU,
            self.media_abbv,
            self.tick_num
            )
        
class Report:
    """Turns information from given tickets into a formatted, human-readable
    report and outputs it in a txt file."""
    
    def __init__(self,mcap,metrics):
        self.panel = mcap.panel
        self.rundate = dtt.datetime.today()
        self.duplicate_count = 0
        self.resolved_count = 0
        self.unresolved_count = 0
        self.ticket_list = {}
        self.header = None
        self.contents_dupe = {}
        self.contents_unres = {}
        self.contents_res = {}
        self.detail_view = None
        
    def mk_header(self):
        self.header = """
pyBev Metrics Report
Panel: %s
Scan initiated: %s
Items resolved: %d
Items unresolved: %d
""" % (self.panel, dtt.datetime.today().strftime('%m/%d/%Y %x'), self.resolved_count,
self.unresolved_count)
        return
    
    def mk_TOC(self):
        for i in range(0,len(self.ticket_list)):
            # do something
            x = 1
        return
        
    def mk_detail_view(self):
        return
        
    def write_to_file(self):
        return