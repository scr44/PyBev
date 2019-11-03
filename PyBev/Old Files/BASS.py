# 617 items
# one man
# all the overtime in the world
# IT'S CODIN' TIME

import pybev as pb
from pybev import datecheck as dc
from pybev import colcomp as cc
from pybev import troubleshooting as ts
from pybev import mapping as mp
from pybev import metricsobj as mo
import datetime as dtt
import numpy as np
import pandas as pd
import os
import time


# Stage 1
mcap_path = ['Z:\\'+dtt.datetime.today().strftime('%m%d%Y_QC_Completed_')
                    +'Beval'+'.txt','Beval']
                    
mcap = mo.MCAPData(mcap_path)

metrics = mo.PanelMetrics(r'C:\Users\sroy\Documents\BevAl Metrics\2017 BevAl Metrics.xlsx',mcap_path[1])

mcap.extract()

metrics.extract()

metrics.connect_book()

mcap.fpivot()

stripday = dc.date_stripper(dtt.datetime.today())

if stripday.weekday() != 6:
    
    monday_diff = dtt.timedelta(days=stripday.weekday())
    
    thisweek = stripday - monday_diff - dtt.timedelta(days=1)
else:
    thisweek = stripday

metrics.cutoff_date = stripday

date_column_max = int(np.where(metrics.df.columns == 'MCAP Data')[0][0] + 2 - 1)

for i in range(0,date_column_max-3):
    # Stage 2
    
    metrics.week_date = thisweek - (i * dtt.timedelta(days=7))
    print(metrics.week_date.strftime('%m/%d/%Y'))
    A = metrics.week_date
    B = metrics.volatile_column
    
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
    cc.late_added_items(mcap,metrics,metrics.week_date,metrics.volatile_column)
    cc.late_removed_items(mcap,metrics,metrics.week_date,metrics.volatile_column)
    
    metrics.update_file_column(metrics.week_date,filter_safe=0)
        