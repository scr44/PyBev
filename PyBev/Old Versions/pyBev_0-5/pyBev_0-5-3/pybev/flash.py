"""As flash is unique compared to BAP and nonflash, this module handles behavior
for it separately."""

from . import metricsobj as mo
from . import datecheck as dc
from . import mapping as mp
from . import colcomp as cc
from . import troubleshooting as ts
from . import bass
import pybev as pb
import numpy as np
import xlwings as xw
import datetime as dtt
import pytz
import time
import os
import sys
import pandas as pd
import configparser
import warnings

def main():
    ad_date = None
    
    return
    
def menu_string_gen(mcap,metrics):
    global ad_date
    try:
        active_panel = mcap.panel
        sheet_name = r' - ' + metrics.sheet_name
    except AttributeError:
        active_panel = 'None'
        sheet_name = ''
        
    try:
        active_date = ad_date.strftime('%m/%d/%Y')
    except AttributeError:
        active_date = 'None'
        
    
    main_menu_string = ("""
  Main Menu
  Active Panel: %s%s
  Active Date: %s
 1. Data extraction
 2. Set active date
 3. Map ad count
 4. Column comparison
 5. Non-QC'd Ads
 6. Multi-Week Update
 7. BASS
 8. Save to Cloud (GDrive)
 9. Options
Enter 'q' to quit.\n\n""" % (active_panel,sheet_name,active_date))
    return main_menu_string