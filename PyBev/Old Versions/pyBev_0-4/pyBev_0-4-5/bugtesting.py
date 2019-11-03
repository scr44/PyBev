import datetime as dtt
import numpy as np
import pandas as pd
import os
import sys
import time

from pybev import *
from pybev.metricsobj import *
from pybev.datecheck import *
from pybev.mapping import *
from pybev.colcomp import *
from pybev.troubleshooting import *


# go to the pyBeverage.py file directory
os.chdir(os.path.dirname(sys.argv[0])) 

# initial object setup
mcap, metrics = stage_one()
stage_two(metrics)
stage_three(mcap,metrics)

metrics.book.save()
metrics.extract()

metrics.cutoff_date = date_stripper(dtt.datetime.today())

A,B,C,D,cutdt = shorthand_names(metrics)

df = metrics.df

dff = cutoff_filter(metrics.df,A,cutdt)

col = A