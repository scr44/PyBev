import datetime as dtt
import numpy as np
import pandas as pd
import os
import sys
import time
import pytz
import xlwings as xw

#Indirect import block
import pybev as pb
import pybev.metricsobj as mo
import pybev.datecheck as dc
import pybev.mapping as mp
import pybev.colcomp as cc
import pybev.troubleshooting as ts

#Direct import block
from pybev import *
from pybev.metricsobj import *
from pybev.datecheck import *
from pybev.mapping import *
from pybev.colcomp import *
from pybev.troubleshooting import *

# go to the pyBev.py file directory
os.chdir(os.path.dirname(sys.argv[0])) 

# initial object setup for circulars
panel = 'Beval'
metrics_path = r'C:\Users\sroy\OneDrive\Documents\BevAl Metrics\2018 BevAl Metrics.xlsx'
metrics = PanelMetrics(metrics_path,panel)
metrics.connect_book(default_sheet='Circulars')

# mcap_path = create_mcap_path(panel,metrics)
# mcap = MCAPData(mcap_path)
# alt_mcap = mk_alt_mcap(mcap)

metrics.book.save()
metrics.extract()
# mcap.extract()
# alt_mcap.extract()
# 
# weeksago = -3
# metrics.week_date = choose_week(weeksago)
# metrics.cutoff_date = date_stripper(dtt.datetime.today())
# A,B,C,D,cutdt = shorthand_names(metrics)



#=============================================================================#
#                                Testing code

def test(metrics):
    cols = metrics.df.columns
    latest_week = metrics.df.columns[np.where(cols == metrics.volatile_column)[0][0]-1]
    current_week_date = dc.sunday_date(dtt.datetime.today())
    print('latest week < current_week_date')
    print(latest_week < current_week_date) # i.e. dataframe doesn't contain current week

    # new_week_column()
    UTC = pytz.timezone('UTC')
    latest_date_col = np.where(metrics.df.columns == metrics.volatile_column)[0][0] - 1
    new_date = metrics.df.columns[latest_date_col] + dtt.timedelta(days=7)
    sunday_date = UTC.localize(dc.sunday_date(new_date))
    
    col_num = int(np.where(metrics.df.columns == metrics.volatile_column)[0][0] + 2)
    max_row = int(len(metrics.df.index) + 1)
    xlShiftToRight = xw.constants.InsertShiftDirection.xlShiftToRight
    
    print('Adding new week column...'),
    
    metrics.sheet.range((1,col_num)).api.EntireColumn.Insert(Shift=xlShiftToRight)
    metrics.sheet.range((1,col_num)).api.value = sunday_date
    metrics.sheet.range((2,col_num),(max_row,col_num)).api.value = 0
    metrics.book.save()
    # end
    
    metrics.extract()

