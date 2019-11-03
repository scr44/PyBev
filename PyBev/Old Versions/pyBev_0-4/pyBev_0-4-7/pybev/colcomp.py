"""Functions to update weekly data from the volatile column and identify issues.
The syntax may be a little confusing: A & B are column headers in the code, but
the comments treat them as A(i) & B(i) etc. for brevity's sake."""


from . import mapping
from . import datecheck
import numpy as np
import pandas as pd
import datetime as dtt
import warnings


def shorthand_names(metrics):
    A = metrics.week_date
    B = metrics.volatile_column
    C = 'Exp. Date'
    D = 'Exp. Lag'
    cutdt = metrics.cutoff_date
    
    return A,B,C,D,cutdt
    
def silence_index_warning():
    pd.options.mode.chained_assignment = None # default='warn', this shuts down the
                                              # "use df.loc[x,y]" warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

def colcomp_update(mcap,metrics,ROP=False):
    """Performs naive updates on the week_date metrics column. This function will
    update any items that are present and not already flagged as problems, and
    then it will flag missing ads and overdue pending ads for troubleshooting."""
    
    silence_index_warning()
    
    metrics.cutoff_date = datecheck.date_from_str()
    
    A,B,C,D,cutdt = shorthand_names(metrics)
    
    new_items(mcap,metrics,A,B,C,D,cutdt)
    
    pending_items(mcap,metrics,A,B,C,D,cutdt)
    
    # nonweekly_items(mcap,metrics,A,B,C,D,cutdt)

    ad_hoc_items(mcap,metrics,A,B,C,D,cutdt)
    
    OOB_items(metrics,A,C)
    
    late_added_items(mcap,metrics,A,B,ROP)
    
    end_date_update(mcap,metrics)
    
    # if (input('Filter-safe write y/n? ') or 0) == 'n':
    metrics.update_file_column(A,filter_safe=0)
    metrics.update_file_column(C,filter_safe=0)
    # else:
    #     metrics.update_file_column(A,filter_safe=1)
    #     metrics.update_file_column(C,filter_safe=1)
    return


#=============================== item functions ===============================


def new_items(mcap,metrics,A,B,C,D,cutdt):
    """Examines all the items that have no identified issues."""
    
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff, A, status='int')
    
    naive_update(dff,A,B) # if B > A: A = B
    pending_check(dff,A,C,D,cutdt) # if A = 0 and cutoff <= C + D: A = 'Pending'
    weekly_non_drop_check(dff,A,C) # if A = 0 and C >= weekdt + 7 days, A = 'ND'
    
    identify_problems(dff,A,C,D,cutdt) # if A = 0: A = '?'
    
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return
    
def pending_items(mcap,metrics,A,B,C,D,cutdt):
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff,A,status='Pending')
    if len(dff.index) == 0:
        return
    
    naive_pending_update(dff,A,B)
    identify_problems(dff,A,C,D,cutdt) # if Pending overdue: A = '?'
    
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return
    
def nonweekly_items(mcap,metrics,A,B,C,D,cutdt):
    dff = irregular_filter(metrics.df)
    dff = status_filter(dff,A,status='ND') # what's going on with this?
    for x in range(0,len(dff[A])):
        i = dff.index.values[x]
        expdt = datecheck.date_stripper(dff.loc[i,C].date())
        freq = dff.loc[i,'Freq']
        
        if (expdt >= A + dtt.timedelta(days=7)
            and cutdt > expdt + dtt.timedelta(days=2)): # 2-day padding to allow QCing
            
            if (freq == 'Monthly') or (freq == 'Bimonthly') or (freq == 'Biweekly'):
                dff.loc[i,A] = 'ND'
                
            else:
                dff.loc[i,A] = '?'
                
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return
    
def ad_hoc_items(mcap,metrics,A,B,C,D,cutdt):
    dff = status_filter(metrics.df,C,status='#N/A') # filters on ExpDt = '#N/A'
    for x in range(0,len(dff[A])):
        i = dff.index.values[x]
        
        if (dff.loc[i,B] == 0
            # a week, padded by three days to allow QCing
            and cutdt > (A + dtt.timedelta(days=10))):
            if mcap.ROP is False:
                dff.loc[i,A] = 'ND'
            else:
                dff.loc[i,A] = 0
        elif dff.loc[i,B] > 0:
            dff.loc[i,A] = dff.loc[i,B]
        
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return
    
def OOB_items(metrics,A,C):
    dff = status_filter(metrics.df,C,status='None') # filters on ExpDt = 'None'
    for x in range(0,len(dff[A])):
        i = dff.index.values[x]
        if dff.loc[i,A] == 0:
            dff.loc[i,A] = 'DRM'
        else:
            dff.loc[i,metrics.volatile_column] == '?'
            
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return
    
def late_added_items(mcap,metrics,A,B,ROP=False):
    """Sometimes retailers update later on after data has been frozen in. This 
    function runs a check on the active week date column to naively update any
    A<B ads regardless of Exp. Date."""
    
    dff = status_filter(metrics.df,A,status='int')
    for x in range(0,len(dff[A])):
        RetMkt = dff.index.values[x]
        if dff.loc[RetMkt,A] < dff.loc[RetMkt,B]:
            dff.loc[RetMkt,A] = dff.loc[RetMkt,B]
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    
    dff = status_filter(metrics.df,A,status='ND')
    for x in range(0,len(dff[A])):
        RetMkt = dff.index.values[x]
        if dff.loc[RetMkt,B] != 0:
            dff.loc[RetMkt,A] = dff.loc[RetMkt,B]
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    
    dff = status_filter(metrics.df,A,status='Miss')
    for x in range(0,len(dff[A])):
        RetMkt = dff.index.values[x]
        if dff.loc[RetMkt,B] != 0:
            dff.loc[RetMkt,A] = 111
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    
    if ROP is True: # Fixes any ? that were found in weekly audit
        dff = status_filter(metrics.df,A,status='?')
        for x in range(0,len(dff[A])):
            RetMkt = dff.index.values[x]
            if dff.loc[RetMkt,B] != 0:
                dff.loc[RetMkt,A] = dff.loc[RetMkt,B]
        mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    
    return
    
def late_removed_items(mcap,metrics,A,B):
    """Sometimes an ad is removed from MCAP after the data is frozen in. This
    function checks the active week date column to naively update any A>B ads
    as long as B != 0. If B == 0, then the week is marked for review with the
    999 error code."""
    
    dff = status_filter(metrics.df,A,status='int>0')
    for x in range(0,len(dff[A])):
        RetMkt = dff.index.values[x]
        if dff.loc[RetMkt,A] > dff.loc[RetMkt,B]:
            
            # Ad count went down to int>0
            if dff.loc[RetMkt,B] != 0:
                dff.loc[RetMkt,A] = dff.loc[RetMkt,B]
                
            # Error code handling
            elif dff.loc[RetMkt,A] == 999:
                if dff.loc[RetMkt,B] != 0:
                    dff.loc[RetMkt,A] = dff.loc[RetMkt,B]
                    
            # Ad count went down to 0
            else:
                dff.loc[RetMkt,A] = 999
                
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    
    return

        
#============================= filter functions ===============================

def irregular_filter(df):
    """Filters out all the retailers with irregular drop days."""
    dff = df[
            (df['Exp. Date'] != 'None') &
            (df['Exp. Date'].fillna('NaN') != 'NaN')
            ]
    return dff
    
def cutoff_filter(df,A,cutdt):
    """Creates a new dataframe that contains only Metrics data from the active
    week up to the cutoff date."""
    
    lowbound = A
    hibound = cutdt
        # gotta handle the 'None' and blank exp dates before the comparison
    dff = irregular_filter(df)
    dff = dff[
            (dff['Exp. Date'] >= lowbound) &
            (dff['Exp. Date'] < hibound)
            ]
    return dff
    
def cutoff_filter_2(df,A,cutdt):
    """Similar to cutoff_filter(), but using the BreakDt instead of the ExpDt
    so that it can check MCAP data instead of Metrics."""
    
    lo = A
    hi = cutdt
    
    dff = df[
            (df['BreakDt'] >= lo) &
            (df['BreakDt'] < hi)
            ]
    
    return dff

def status_filter(dff, col, status='all'):
    """Filters the given dataframe column by status.
    
    status: 'all', 'Pending', 'Indexed', 'Review', 'Scraped', 'AC QC', 'Published', '?',
    'Duplicate', 'Wrong Version', 'Backup Sender',
    'int', 'int>0', '0', '#N/A', 'ND', 'not_int', 'None', 'Miss'
    """
    
    allowed_status = ['all',
    # Metrics Statuses
    'Pending', 'Indexed', 'Review', 'Scraped', 'AC QC', 'Published','?',
    # MCAP Statuses
    'Duplicate', 'Wrong Version', 'Backup Sender',
    # Special Cases
    'int','int>0','0','not_zero','#N/A','ND','not_int','None', 'Miss']
    
    if status == 'all':
        return dff
    elif status == '0':
        dff = dff[dff[col] == 0]
        return dff
    elif status == 'not_zero':
        dff = dff[dff[col] != 0]
        return dff
    elif status == 'int' or status == 'int>0':
        if dff[col].dtype == 'object':
            try:
                dff = dff[
                        pd.to_numeric(dff[col],errors='coerce').fillna('NaN') != 'NaN'
                        ]
            except: # This occurs if the entire dff[A] is already numeric (no NDs or issues)
                dff = dff
        if status == 'int>0':
            dff = dff[dff[col] != 0]
        return dff
    elif status == 'not_int':
        try:
            dff = dff[
                    pd.to_numeric(dff[col],errors='coerce').fillna('NaN') == 'NaN'
                    ]
        except TypeError:
            print('Error: no non-integers found in dff')
            return dff
    elif status == '#N/A':
        dff = dff[
                dff[col].isnull()
                ]
    elif status in allowed_status:
        dff = dff[dff[col].astype(object) == status]
    else:
        print('Invalid status, please run the filter again.')
    return dff
    
def duplicate_filter(df, A, B):
    
    dff = status_filter(df, A, status='int')
    dff = dff[dff[A] > dff[B]]
    
    return dff
    


#============================== update functions ==============================


def naive_update(df,A,B): 
    for x in range(0,len(df[A])):
        i = df.index.values[x]
        
        # if B > A: A = B
        if df.loc[i,B] > df.loc[i,A]:
            df.loc[i,A] = df.loc[i,B]

def naive_pending_update(df,A,B):
    for x in range(0,len(df[A])):
        i = df.index.values[x]
        
        # if Pending has come in, update
        if ((df.loc[i,B] > 0)
            and (df.loc[i,A] == 'Pending')):
            df.loc[i,A] = df.loc[i,B]
    return

def pending_check(df,A,C,D,cutoff):
    
    # if A = 0 and cutoff <= C + D: A = 'Pending'
    for x in range(0,len(df[A])):
        i = df.index.values[x]
        
        if np.isnan(df.loc[i,D]) == True:
            lag = dtt.timedelta(days=0)
        else:
            lag = dtt.timedelta(days=df.loc[i,D])
            
        if (df.loc[i,A] == 0
            and cutoff.date() <= (df.loc[i,C].date() + lag)):
            df.loc[i,A] = 'Pending'
    return
    
def weekly_non_drop_check(df,A,C):
    for x in range(0,len(df[A])):
        i = df.index.values[x]
        
        # if A = 0 and C > weekdt + 7 days, A = ND
        if (df.loc[i,A] == 0
            and df.loc[i,C] >= (A + dtt.timedelta(days=7))):
            df.loc[i,A] = 'ND'
    return
    
def identify_problems(df,A,C,D,cutoff):
    for x in range(0,len(df[A])):
        i = df.index.values[x]
        
        # if A is missing: A = '?'
        if df.loc[i,A] == 0:
            df.loc[i,A] = '?'
        
        # set value from lag column D
        if np.isnan(df.loc[i,D]) == True:
            lag = dtt.timedelta(days=0)
        else:
            lag = dtt.timedelta(days=df.loc[i,D])
        
        # if A is Pending and overdue: A = '?'
        if (df.loc[i,A] == 'Pending'
            and cutoff.date() > (df.loc[i,C].date() + lag)):
            df.loc[i,A] = '?'
    return
    
def end_date_update(mcap,metrics):
    A = metrics.week_date
    C = 'Exp. Date'
    # D = 'Exp. Lag'
    # E = 'EndDt'
    F = 'Freq'
    cutdt = metrics.cutoff_date
    
    # Integers greater than 0
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff, A, status='int>0')
    
    for x in range(0,len(dff.index)):
        i = dff.index.values[x]
        end_date_freq(dff,A,C,F,i)
            
    mapping.map_small_to_big(C,dff,metrics.df,agg_func=None)
    
    # Non-Drops
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff, A, status='ND')
    
    for x in range(0,len(dff.index)):
        i = dff.index.values[x]
    
        if dff.loc[i,C] < (A + dtt.timedelta(days=7)):
            end_date_freq(dff,A,C,F,i)
    
    mapping.map_small_to_big(C,dff,metrics.df,agg_func=None)
    
    # Misses
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff, A, status='Miss')
    
    for x in range(0,len(dff.index)):
        i = dff.index.values[x]
    
        if dff.loc[i,C] < (A + dtt.timedelta(days=7)):
            end_date_freq(dff,A,C,F,i)
    
    mapping.map_small_to_big(C,dff,metrics.df,agg_func=None)
    
    return
    
def end_date_freq(dff,A,C,F,i):
    expdt = dff.loc[i,C]
    freq = dff.loc[i,F]
    
    if freq == 'Weekly':
        if expdt < (A + dtt.timedelta(days=7)):
            dff.loc[i,C] += dtt.timedelta(days=7)
            
    if freq == 'Biweekly':
        if expdt < (A + dtt.timedelta(days=7)):
            dff.loc[i,C] += dtt.timedelta(days=14)
    
    # the following convoluted behavior is designed to avoid date creep stemming from
    # February and the accumulation of 30-day vs 31-day month differences
    if freq == 'Bimonthly':
        if expdt < (A + dtt.timedelta(days=7)):
            
            if (expdt.day >= 1 and expdt.day < 15):
                dff.loc[i,C] = dtt.datetime(
                                            year=expdt.year,
                                            month=expdt.month,
                                            day=15
                                            )
                
                
            elif expdt.day >= 15:
                if expdt.month == 12:
                    month = 1
                    year = expdt.year + 1
                else:
                    month = expdt.month + 1
                    year = expdt.year
                
                dff.loc[i,C] = dtt.datetime(
                                            year=year,
                                            month=month,
                                            day=1
                                            )
            
    if freq == 'Monthly':
        if expdt < (A + dtt.timedelta(days=7)):
        
            if expdt.month == 12:
                month = 1
                year = expdt.year + 1
            else:
                month = expdt.month + 1
                year = expdt.year
            
            dff.loc[i,C] = dtt.datetime(
                                    year=year,
                                    month=month,
                                    day=1
                                    )
    return