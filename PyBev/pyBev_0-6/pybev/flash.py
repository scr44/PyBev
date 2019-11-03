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

#================================== Menu =======================================
def main():
    global volatile_updated
    global ad_date
    
    ad_date = None
    volatile_updated = False
    return_to_main = False
    mcap,metrics = update_data(mcap,metrics)
    
    while return_to_main is False:
        print(menu_string_gen(mcap,metrics))
        try: user_input = int(input())
        except ValueError: user_input = None
        
        if user_input == 1:
            mcap,metrics = update_data()
            
        elif user_input == 2:
            set_active_date()
            
        elif user_input == 3:
            map_ad_vids()
            
        elif user_input == 4:
            column_update()
            
        elif user_input == 5:
            non_qc_ads()
            
        elif user_input == 6:
            multi_week()
            
        elif user_input == 7:
            cloud_save()
            
        elif user_input == 8:
            return_to_main = True
            
        else:
            print('Unrecognized option, try again.')
        
    return None, None
    
def menu_string_gen(mcap,metrics):
    global ad_date
    try:
        active_panel = mcap.panel
        sheet_name = metrics.sheet_name
    except AttributeError:
        active_panel = 'None'
        sheet_name = ''
        
    try:
        display_ad_date = ad_date.strftime('%m/%d/%Y')
    except AttributeError:
        display_ad_date = 'None'
        
    
    menu_string = ("""
  Flash Menu
  Active Panel: Flash - %s
  Active Ad Date: %s
 1. Update data
 2. Set active date
 3. Map ad VIDs
 4. Column update
 5. Non-QC'd Ads
 6. Multi-Week Update
 7. Save to Cloud (GDrive)
 8. Return to main menu\n\n""" % (sheet_name,display_ad_date))
    return menu_string

#================================== Stages =====================================

def update_data(ROP=False):
    sheet_name = input('Sheet name: ')
    
    mcap = 'placeholder'
    metrics = mo.FlashMetrics()
    return mcap, metrics
    
def set_active_date():
    return
    
def map_ad_vids():
    return
    
def column_update():
    return

def non_qc_ads():
    return
    
def multi_week():
    return
    
def cloud_save():
    return
    
#=============================== Subfunctions ==================================
