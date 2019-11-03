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
metrics_path = r'C:\Users\sroy\Documents\BevAl Metrics\2019 BevAl Metrics.xlsx'
metrics = PanelMetrics(metrics_path,panel)
metrics.connect_book(default_sheet='Circulars')

mcap_path = create_mcap_path(panel,metrics)
mcap = MCAPData(mcap_path)
alt_mcap = mk_alt_mcap(mcap)
report = None

metrics.book.save()
metrics.extract()
mcap.extract()
alt_mcap.extract()

# choosing date
weeksago = -1
metrics.week_date = choose_week(weeksago)

# test code

# review_items_found = ts.non_qcc_items(mcap,metrics,report,alt_mcap,'Review')
# ts.non_qcc_items(mcap,metrics,report,alt_mcap,'Review')
status = 'Review'

cc.silence_index_warning()
metrics.wipe_volatile_data()

metrics.cutoff_date = dc.date_from_str()
A,B,C,D,cutdt = cc.shorthand_names(metrics)
alt_mcap.fpivot_status(status)

# B = Status_item_Count
if mp.valid_index_check(metrics.week_date,alt_mcap.status_pivot_df,'len') is False:
    print('No ads with status remaining for %s.' % metrics.week_date.strftime('%m/%d/%Y'))
    print('False')