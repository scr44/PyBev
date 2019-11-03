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


# go to the pyBeverage.py file directory
os.chdir(os.path.dirname(sys.argv[0])) 

# initial object setup for circulars
panel = 'Beval'
metrics_path = r'C:\Users\sroy\Documents\BevAl Metrics\2018 BevAl Metrics.xlsx'
metrics = PanelMetrics(metrics_path,panel)
metrics.connect_book(default_sheet='Circulars')

mcap_path = create_mcap_path(panel,metrics)
mcap = MCAPData(mcap_path)
alt_mcap = mk_alt_mcap(mcap)

metrics.book.save()
metrics.extract()
mcap.extract()
alt_mcap.extract()

weeksago = -3
metrics.week_date = choose_week(weeksago)
metrics.cutoff_date = date_stripper(dtt.datetime.today())
A,B,C,D,cutdt = shorthand_names(metrics)



#=============================================================================#
#                                Testing code


stage_5(mcap,metrics)