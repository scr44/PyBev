"""Functions to update weekly data from the volatile column and identify issues.
The syntax may be a little confusing: A & B are column headers in the code, but
the comments use them to mean A(i) & B(i) etc."""


from . import mapping
from . import datecheck
import numpy as np
import datetime as dtt
import warnings

# consider turning preliminary update into a dff class

def preliminary_update(metrics,mcap):
    metrics.cutoff_date = datecheck.check_before_input()
    
    A = metrics.week_date
    B = metrics.volatile_column
    C = 'Exp. Date'
    D = 'Exp. Lag'
    cutdt = metrics.cutoff_date
    
    dff = cutoff_filter(metrics.df,A,cutdt)
    dff = status_filter(dff, A, status='int')
    
    naive_update(dff,A,B) # if B > A: A = B
    pending_check(dff,A,C,D,cutdt) # if A = 0 and cutoff <= C + D: A = 'Pending'
    identify_problems(dff,A,C,D,cutdt) # if A = 0 or Pending overdue: A = '?'
    
    mapping.map_small_to_big(A,dff,metrics.df,agg_func=None)
    end_date_update(metrics,mcap)
    
    if (input('Filter-safe write y/n? ') or 0) == 'y':
        metrics.update_file(A,filter_safe=1)
        metrics.update_file(C,filter_safe=1)
    else:
        metrics.update_file(A,filter_safe=0)
        metrics.update_file(C,filter_safe=0)
    return
    
def cutoff_filter(df,A,cutdt):
    """Creates a new dataframe that contains only the currently checked week
    up to the cutoff date."""
    
    lowbound = A
    hibound = cutdt
        # gotta handle the 'None' and blank exp dates somehow before the comparison
    df = df[
            (df['Exp. Date'] != 'None') &
            (df['Exp. Date'].fillna('#N/A') != '#N/A')
            ]
    dff = df[
            (df['Exp. Date'] >= lowbound) &
            (df['Exp. Date'] < hibound)
            ]
    return dff

def status_filter(dff, date, status='all'):
    """Filters the given dataframe by status.
    
    status: 'all', 'Pending', 'Indexed', 'Review', 'Scraped', 'AC QC', 'Published', '?',
    'int', '0', '#N/A'
    """
    
    allowed_status = ['all', 'Pending', 'Indexed', 'Review', 'Scraped', 'AC QC', 'Published', '?',
    'int', '0', '#N/A']
    
    if status == 'all':
        return dff
    elif status == '0':
        dff = dff[dff[date] == 0]
        return dff
    elif status == 'int':
        # pandas wants to deprecate this and replace it with the crappy "to_numeric()"
        # method that doesn't work on dataframes, just series; if this code breaks
        # then they've probably removed the method and you need to find a workaround
        # or just roll the pandas version back.
        warnings.simplefilter(action='ignore', category=FutureWarning)
        dff = dff[
                dff[date].convert_objects(convert_numeric=True).fillna('NaN') != 'NaN'
                ]
        return dff
    elif status in allowed_status:
        dff = dff[dff[date] == status]
    else:
        print('Invalid status, please run the filter again.')
    return dff
    
def naive_update(df,A,B): # if B > A: A = B
    for x in range(0,len(df[A])):
        i = df.index.values[x]
        if df.loc[i,B] > df.loc[i,A]:
            df.loc[i,A] = df.loc[i,B]
    return

def pending_check(df,A,C,D,cutoff): # if A = 0 and cutoff <= C + D: A = 'Pending'
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
    
def end_date_update(metrics,mcap):
    return