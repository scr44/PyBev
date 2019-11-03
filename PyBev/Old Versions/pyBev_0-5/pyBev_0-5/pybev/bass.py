from . import datecheck as dc
from . import colcomp as cc
from . import mapping as mp
import datetime as dtt
import numpy as np
import pandas as pd
import warnings


def comp_check(mcap, metrics):
    """Data is not generally checked after two weeks past the drop date if no
    issues were raised. This means that it is effectively "frozen in" at this
    point. However, data can change after that time frame, so to keep the metrics
    up to date it behooves us to compare the nominal metrics data against the
    current MCAP data.
    
    Discrepant integer counts will be silently adjusted. This includes removed 
    duplicates and extra drops. Anything involving misses will be given an appropriate
    error code (999 for int->miss, 111 for miss->int). Uninvestigated circular 
    issues (0s) will be flagged with '?'s. For ROP, 0s will be left blank.
    
    Please turn off all filters in the Metrics document before performing this
    operation!
    """
    
    if (mcap == None) or (metrics == None):
        print('Please extract data first (step 1).')
        return
    bass_backup(metrics)
    
    print('Performing BASS Comp Check...')
        
    stripday = dc.date_stripper(dtt.datetime.today())
    
    if stripday.weekday() != 6:
        
        monday_diff = dtt.timedelta(days=stripday.weekday())
        
        thisweek = stripday - monday_diff - dtt.timedelta(days=1)
    else:
        thisweek = stripday
        
    metrics.cutoff_date = stripday
    
    date_column_max = int(np.where(metrics.df.columns == 'MCAP Data')[0][0] + 2 - 1)
    
    if mcap.ROP is False:
        pre_date_cols = 3
    else:
        pre_date_cols = 4
    
    
    for i in range(0,date_column_max - pre_date_cols):
        # Stage 2
        
        metrics.week_date = thisweek - (i * dtt.timedelta(days=7))
        print(metrics.week_date.strftime('%m/%d/%Y'))
        
        # Stage 3
        metrics.book.save()
    
        metrics.extract()
        
        mp.map_index(
            metrics.week_date,
            mcap.pivot_df,
            metrics.df,
            metrics.volatile_column,
            agg_func='len'
            )
        
        # BASS updating
        pd.options.mode.chained_assignment = None # default='warn', this shuts down the
                                              # "use df.loc[x,y]" warnings
        warnings.simplefilter(action='ignore', category=FutureWarning)
        
        cc.late_added_items(mcap,metrics,metrics.week_date,metrics.volatile_column)
        cc.late_removed_items(mcap,metrics,metrics.week_date,metrics.volatile_column)
        
        flag_old_zeros(metrics)
        
        metrics.update_file_column(metrics.week_date,filter_safe=0)
    metrics.week_date = None
    print('BASS Comp Check completed.')
        
    return

def flag_old_zeros(metrics):
    A = metrics.week_date
    C = 'Exp. Date'
    
    dff = metrics.df.loc[metrics.df[A] == 0]
    if dff.size > 0:
        # only data with expected dates, the ad hocs should take care of themselves with ND
        dff = dff[pd.to_datetime(dff['Exp. Date'],errors='coerce').fillna('NaT') != 'NaT']
        
        for x in range(0,len(dff.index)):
            i = dff.index[x]
            # if the zero falls 2 weeks or more behind the next expected ad
            if (dff.loc[i,C] > (A + dtt.timedelta(days=14))):
                dff.loc[i,A] = '?'

        mp.map_small_to_big(metrics.week_date,dff,metrics.df)
    return

def bass_safety_check():
    x = input(
'''
                            !!! WARNING !!!

Before performing the BASS check, please ensure that ALL filters are turned
off in the appropriate worksheet. Failure to do so will overwrite ALL metrics
data with incorrect values.

                            !!! WARNING !!!

            Press ENTER to continue or input 'cancel' to stop.

''') or None
    return x

    
def bass_backup(metrics):
    metrics.book.save()
    # metrics_folder_path = options.metrics_folder_path
    metrics_folder_path = r'C:\Users\sroy\OneDrive\Documents\BevAl Metrics'
    filename = (metrics_folder_path + r'\Archive\BASS Archive'+'\\' + metrics.panel +
               '_' + dtt.datetime.today().strftime('%Y-%m-%d_%H%M') + '.xlsx')
    
    filename2 = (metrics_folder_path + '\\' + dtt.datetime.today().strftime('%Y ') +
                    metrics.panel + ' Metrics.xlsx')
                    
    metrics.book.save(filename)
    metrics.book.save(filename2)
    print('Backup saved to %s' % filename)