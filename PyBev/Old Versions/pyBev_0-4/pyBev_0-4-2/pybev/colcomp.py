"""Functions to update weekly data from the volatile column and identify issues.
The syntax may be a little confusing: A & B are column headers in the code, but
the comments treat them as A(i) & B(i) etc. for brevity's sake."""


from . import mapping
from . import datecheck
import numpy as np
import pandas as pd
import datetime as dtt


def shorthand_names(metrics):
    A = metrics.week_date
    B = metrics.volatile_column
    C = 'Exp. Date'
    D = 'Exp. Lag'
    cutdt = metrics.cutoff_date
    
    return A,B,C,D,cutdt
    

def preliminary_update(mcap,metrics):
    """Performs naive updates on the week_date metrics column. This function will
    update any items that are present and not already flagged as problems, and
    then it will flag missing ads and overdue pending ads for troubleshooting."""
    
    metrics.cutoff_date = datecheck.choose_cutoff()
    
    A,B,C,D,cutdt = shorthand_names(metrics)
    
    empty_items(mcap,metrics,A,B,C,D,cutdt)
    
    pending_items(mcap,metrics,A,B,C,D,cutdt)
    
    ad_hoc_items(mcap,metrics,A,B,C,D,cutdt)
    
    OOB_items(metrics,A,C)
    
    end_date_update(mcap,metrics)
    
    if (input('Filter-safe write y/n? ') or 0) == 'n':
        metrics.update_file_column(A,filter_safe=0)
        metrics.update_file_column(C,filter_safe=0)
    else:
        metrics.update_file_column(A,filter_safe=1)
        metrics.update_file_column(C,filter_safe=1)
    return


#=============================== item functions ===============================


def empty_items(mcap,metrics,A,B,C,D,cutdt):
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff, A, status='int')
    
    naive_update(dff,A,B) # if B > A: A = B
    pending_check(dff,A,C,D,cutdt) # if A = 0 and cutoff <= C + D: A = 'Pending'
    non_drop_check(dff,A,C) # if A = 0 and C >= weekdt + 7 days, A = 'ND'
    identify_problems(dff,A,C,D,cutdt) # if A = 0: A = '?'
    
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return
    
def pending_items(mcap,metrics,A,B,C,D,cutdt):
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff,A,status='Pending')
    
    naive_pending_update(dff,A,B)
    identify_problems(dff,A,C,D,cutdt) # if Pending overdue: A = '?'
    
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return
    
def ad_hoc_items(mcap,metrics,A,B,C,D,cutdt):
    dff = status_filter(metrics.df,C,status='#N/A') # filters on ExpDt = '#N/A'
    for x in range(0,len(dff[A])):
        i = dff.index.values[x]
        
        if (dff.loc[i,B] == 0
            and cutdt > (A + dtt.timedelta(days=7))):
            dff.loc[i,A] = 'ND'
        elif dff.loc[i,B] > 0:
            dff.loc[i,A] = dff.loc[i,B]
        
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return
    
def OOB_items(metrics,A,C):
    dff = status_filter(metrics.df,C,status='None') # filters on ExpDt = '#N/A'
    for x in range(0,len(dff[A])):
        i = dff.index.values[x]
        if dff.loc[i,A] == 0:
            dff.loc[i,A] = 'ND'
            
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    return

        
#============================= filter functions ===============================


def cutoff_filter(df,A,cutdt):
    """Creates a new dataframe that contains only data from the active week
    up to the cutoff date."""
    
    lowbound = A
    hibound = cutdt
        # gotta handle the 'None' and blank exp dates before the comparison
    df = df[
            (df['Exp. Date'] != 'None') &
            (df['Exp. Date'].fillna('#N/A') != '#N/A')
            ]
    dff = df[
            (df['Exp. Date'] >= lowbound) &
            (df['Exp. Date'] < hibound)
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
    'int', 'int>0', '0', '#N/A', 'ND', 'None'
    """
    
    allowed_status = ['all', 'Pending', 'Indexed', 'Review', 'Scraped', 'AC QC',
                        'Published','?','int','int>0','0','#N/A','ND','not_int','None']
    
    if status == 'all':
        return dff
    elif status == '0':
        dff = dff[dff[col] == 0]
        return dff
    elif status == 'int' or status == 'int>0':
        if dff[col].dtype == 'object':
            dff = dff[
                    pd.to_numeric(dff[col],errors='coerce').fillna('NaN') != 'NaN'
                    ]
        if status == 'int>0':
            dff = dff[dff[col] != 0]
        return dff
    elif status == 'not_int':
        dff = dff[
                pd.to_numeric(dff[col],errors='coerce').fillna('NaN') == 'NaN'
                ]
    elif status in allowed_status:
        dff = dff[dff[col] == status]
    else:
        print('Invalid status, please run the filter again.')
    return dff
    
def duplicate_filter(df, A, B):
    dff = status_filter(df, A, status='int')
    dff = dff[dff[B] > 0]
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
    
def non_drop_check(df,A,C):
    
    # if A = 0 and C > weekdt + 7 days, A = ND
    for x in range(0,len(df[A])):
        i = df.index.values[x]
        
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
    cutdt = metrics.cutoff_date
    
    # Integers greater than 0
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff, A, status='int>0')
    
    for x in range(0,len(dff.index)):
        i = dff.index.values[x]
        
        # naive weekly update, perhaps a more sophisticated one based on end
        # date or frequency can be added
        if dff.loc[i,C] < (A + dtt.timedelta(days=7)):
            dff.loc[i,C] += dtt.timedelta(days=7)
            
    mapping.map_small_to_big(C,dff,metrics.df,agg_func=None)
    
    # Non-Drops
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff, A, status='ND')
    
    for x in range(0,len(dff.index)):
        i = dff.index.values[x]

        if dff.loc[i,C] < (A + dtt.timedelta(days=7)):
            dff.loc[i,C] += dtt.timedelta(days=7)
    
    mapping.map_small_to_big(C,dff,metrics.df,agg_func=None)
    
    return