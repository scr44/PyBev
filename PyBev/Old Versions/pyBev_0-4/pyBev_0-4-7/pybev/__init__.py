from . import metricsobj as mo
from . import datecheck as dc
from . import mapping as mp
from . import colcomp as cc
from . import troubleshooting as ts
from . import bass
import numpy as np
import xlwings as xw
import datetime as dtt
import pytz
import time
import os
import pandas as pd
import warnings


def run_main_program():
    print('\n=== pyBev v0.4.7 ===\n')
    mcap = None
    metrics = None
    report = None
    mcap, metrics, report = main_menu(mcap,metrics,report)
    
    return mcap, metrics, report


#================================== Menus =====================================
def menu_string_gen(mcap,metrics):
    
    try:
        active_panel = mcap.panel
        sheet_name = r' - ' + metrics.sheet_name
    except AttributeError:
        active_panel = 'None'
        sheet_name = ''
        
    try:
        active_date = metrics.week_date.strftime('%m/%d/%Y')
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
 5. Troubleshooting (WIP)
 6. 3-Week Update
 7. BASS
 8. Options (WIP)
Enter 'q' to quit.\n\n""" % (active_panel,sheet_name,active_date))
    return main_menu_string

def main_menu(mcap,metrics,report):
    
    volatile_updated = False
    
    while True:
        main_menu_string = menu_string_gen(mcap,metrics)
        print(main_menu_string)
        
        user_input = input()
        
        try: user_input = int(user_input)
        except ValueError: user_input = user_input
        
        if type(user_input) is int:
            mcap,metrics,report = program_stages(
                                user_input,mcap,metrics,report)
        elif menu_commands(user_input) is 0:
            break
        else:
            continue
                
    return mcap,metrics,report
            
def options_menu():
    print("""\n Still under construction in this build!\n""")
    
    print(
"""
 1. Default Metrics Path:
 2. Default Archive Path:

To change a setting, input its number.
""")
    return
        
def program_stages(stage,mcap,metrics,report):
    if stage == 1:
        mcap, metrics = stage_1()
    elif stage == 2:
        stage_2(metrics)
    elif stage == 3:
        stage_3(mcap, metrics)
    elif stage == 4:
        stage_4(mcap, metrics)
    elif stage == 5:
        report = stage_5(mcap,metrics)
    elif stage == 6:
        stage_6(mcap,metrics)
    elif stage == 7:
        stage_7(mcap,metrics)
    elif stage == 8:
        stage_8()
    else:
        print('Unrecognized stage, please try again')
    
    return mcap,metrics,report
            
def menu_commands(user_input):
    if user_input == 'q':
        print('\nTerminating program.')
        return 0
        
    elif user_input == 'help':
        print('\nFeature not active in this version.')
        # open readme.txt
        
    # Easter Eggs
    elif user_input == 'friendly q':
        print('\nGoodbye!')
        return 0
    elif user_input == 'dramatic q':
        print('\nNow, these data will be lost... like tears in the rain...')
        return 0
    elif user_input == 'whiterabbit.obj':
        print('PERMISSION DENIED... ',end=''),
        time.sleep(1)
        print('and...\n')
        time.sleep(1)
        for i in range(0,10):
            print(
"""                                  AH AH AH!
                        YOU DIDN'T SAY THE MAGIC WORD!
""")
            time.sleep(.4)
        time.sleep(2)
    else:
        print('Unknown command, please try again.\n')
    
    return None
    
    
#============================== Program Stages ================================

# DATA EXTRACTION
def stage_1():
    """Extracts data from the auto MCAP pull and the Metrics excel document,
    pivots where appropriate, and prepares it for further analysis."""
    
    panel = panel_selection()
    
    if panel == None:
        return None, None
    
    metrics_path = (input('Panel Metrics file location (press enter for default): ')
                or r'C:\Users\sroy\OneDrive\Documents\BevAl Metrics\2018 BevAl Metrics.xlsx')
                # or r'C:\Users\sroy\Documents\BevAl Metrics\test.xlsx')
    
    print('Metrics location set to '+metrics_path,end='\n')
        
    metrics = mo.PanelMetrics(metrics_path,panel)
    
    metrics.connect_book()
    
    mcap_path = create_mcap_path(panel,metrics)
    
    if metrics.sheet_name == 'ROP':
        mcap = mo.MCAPData(mcap_path,ROP=True)
    else:
        mcap = mo.MCAPData(mcap_path)
    
    # Extract the data
    try:
        print('Extracting MCAP data... ',end='')
        mcap.extract()
        print('Done')
        
        mcap.fpivot()
        
        print('Extracting Metrics data... ',end='')
        metrics.extract()
        print('Done')
    except FileNotFoundError:
        print('File not found, please try again.')
        return mcap, metrics
        
    metrics.wipe_volatile_data()
    metrics.week_date = None

    # Add new week columns if needed
    cols = metrics.df.columns
    latest_week = metrics.df.columns[np.where(cols == metrics.volatile_column)[0][0]-1]
    current_week_date = dc.sunday_date(dtt.datetime.today())
        
    while latest_week < current_week_date: # i.e. dataframe doesn't contain current week
        new_week_column(metrics)
        metrics.book.save()
        metrics.extract()
        
        cols = metrics.df.columns
        latest_week = metrics.df.columns[np.where(cols == metrics.volatile_column)[0][0]-1]
    
    print('''
Data ready for processing. Please turn off all excel filters before proceeding.
''')
    
    monday_archive(metrics)
    
    return mcap, metrics
 
# SET ACTIVE DATE
def stage_2(metrics,weeksago=None):
    """User sets an active date for the program."""
    try:
        metrics.week_date = dc.choose_week(weeksago)
        print('Active date set to '+metrics.week_date.strftime('%m/%d/%Y'))
    except AttributeError:
        print('Error: You must run stage 1 at least once before stage 2.')
    
    global volatile_updated
    volatile_updated = False
    
    return

# MAP AD COUNT    
def stage_3(mcap,metrics):
    """Maps the VID count from the MCAP data to the metrics object and writes
    it to the excel document."""
    try:
        if metrics.week_date == None:
            print('Cannot perform without active week date!')
            return
    except AttributeError:
        print('Error: You must run stage 1 at least once before stage 3.')
        return
    
    print('Beginning MCAP-Metrics mapping...')
    
    if metrics.volatile_column not in metrics.df.columns:
        prompt = 'Name of the metrics column to write pivoted data to: '
        metrics.volatile_column = input(prompt)

    metrics.book.save()

    metrics.extract()
    
    mp.map_index(
        metrics.week_date,
        mcap.pivot_df,
        metrics.df,
        metrics.volatile_column,
        agg_func='len'
        )
        
    # if (input('Filter-safe write y/n? ') or 0) == 'n':                    
    #     metrics.update_file_column(metrics.volatile_column,filter_safe=0)
    # else:
    #     metrics.update_file_column(metrics.volatile_column,filter_safe=1)
    
    metrics.update_file_column(metrics.volatile_column,filter_safe=0)
    
    print('Mapping complete.')
    
    global volatile_updated
    volatile_updated = True
    
    return

# COLUMN COMPARISON
def stage_4(mcap,metrics):
    """Compares the active week column to the volatile column, updating Pending,
    Non-Drop, and Naive items. When done comparing, it updates all appropriate
    end dates according to their listed Frequencies. Finally, the Metrics document
    is sorted by expected date and active week item status."""
    
    global volatile_updated
    try:
        if metrics.week_date == None:
            print('Cannot perform without active week date!')
            return
        if volatile_updated is not True:
            print('The data column is not up to date. Please run stage 3 first.')
            return
    except AttributeError:
        print('Error: You must run stage 1 at least once before stage 4.')
        return
    
    print('Beginning column comparison...')
    
    metrics.book.save()

    metrics.extract()
    
    if mcap.ROP is not True:
        cc.colcomp_update(mcap,metrics) # updates 0s to ints or pending and flags ?s
        metrics.xl_col_sort() # sorts all data by date ascending
    else:
        cc.colcomp_update(mcap,metrics,ROP=True)
        metrics.xl_col_sort(key1='Location',key2='Auditor',key3='Publication')
    
    print('Column comparison complete.')
    
    return

# TROUBLESHOOTING
def stage_5(mcap,metrics):
    
    if metrics.week_date == None:
        print('No week date set. Please run stage 2.')
        return
    
    global volatile_updated
    volatile_updated = False
    
    #report = mo.Report(mcap,metrics)
    report = None # until report functionality is built
    
    metrics.wipe_volatile_data()
    
    metrics.book.save()
    
    metrics.extract()
    
    alt_mcap = mk_alt_mcap(mcap)
    
    alt_mcap.extract()

    # 
    # ts.duplicate_items(mcap,metrics,report,alt_mcap)
    #
    indexed_items_found = ts.indexed_items(mcap,metrics,report,alt_mcap)
    
    if indexed_items_found is not False:
        metrics.update_file_column(metrics.week_date,filter_safe=0)
        metrics.update_file_column(metrics.volatile_column,filter_safe=0)
    
    # 
    # ts.resolved_items(mcap,metrics,report,alt_mcap)
    # 
    # ts.unresolved_items(mcap,metrics,report,alt_mcap)
    
    return report

# 3-WEEK UPDATE
def stage_6(mcap,metrics):
    if input(
'''                  Please deactivate all excel filters now.

             Press ENTER to continue or input 'cancel' to stop.\n''') != 'cancel':
        for i in (-2,-1,0):
            stage_2(metrics,i)
            stage_3(mcap,metrics)
            stage_4(mcap,metrics)
        metrics.wipe_volatile_data()
        metrics.week_date = None
    return

# BASS
def stage_7(mcap,metrics):
    x = bass.bass_safety_check()
    if x == None:
        bass.comp_check(mcap,metrics)
    else:
        print('BASS canceled.')
    return

# OPTIONS
def stage_8():
    options_menu()
    return
   
     
#============================== Stage Subfunctions ============================


def panel_selection():
    while True:
        panel = input(
"""Please select a panel:
 1. BevAl
 2. Non-Flash
(Defaults to BevAl, 'cancel' to stop)\n""") or '1'
        if (panel == '1' or panel=='BevAl'):
            panel = 'Beval'
            break
        elif (panel == '2' or panel=='Non-Flash'):
            panel = 'NonFlash'
            break
        elif panel == 'cancel':
            print('Canceling panel selection.')
            return None
        else:
            print('Unrecognized panel, please choose another.\n')
            continue
    return panel
    
def create_mcap_path(panel,metrics):
    mcap_path = [0,0]
    
    if metrics.sheet_name == 'ROP':
        panel2 = panel + 'ROP'
        mcap_path[0] = 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_QC_Completed_')+panel2+'.txt'
    else:
        mcap_path[0] = 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_QC_Completed_')+panel+'.txt'
    mcap_path[1] = panel
    return mcap_path
    
def mk_alt_mcap(mcap):
    mcap_path = [0,0]
    mcap_path[0] = 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_not_QCC_')+mcap.panel+'.txt'
    mcap_path[1] = mcap.panel
    
    alt_mcap = mo.MCAPData(mcap_path)
    
    return alt_mcap

def monday_archive(metrics):    
# def monday_archive(metrics,options):
    
    today = dtt.datetime.today()
    
    if today != 0: # if it's not a Monday
        
        monday_difference = dtt.timedelta(days=today.weekday())
        
        monday_date = (today - monday_difference)
    
    # archive_path = options.archive_path
    archive_path = r'C:\Users\sroy\OneDrive\Documents\BevAl Metrics'
    
    filename = (archive_path + '\\Archive\\' + 
                    monday_date.strftime('%Y-%m-%d ') + metrics.panel + '.xlsx')
                    
    filename2 = (archive_path + '\\2018 BevAl Metrics.xlsx')

    if os.path.isfile(filename) == 0:
        if input(
'''There is no existing archive for this week. Would you like to archive the Metrics file? y/n: ''') == 'y':
        
            print('Archiving data...\n',end=''), 
            
            metrics.book.save(filename)
            metrics.book.save(filename2)
            
            print('Done')
            print(
'''Data archived to %s
You can change the archive directory in Options. (WIP)''' % (archive_path + '\\Archive\\'))
    
    return

def is_dst(tz):
    now = pytz.utc.localize(dtt.datetime.utcnow())
    return now.astimezone(tz).dst() != dtt.timedelta(0)

def new_week_column(metrics):
    """If there is no column with the current week date as a header, inserts a 
    column for the week after the latest week between the latest week column
    and the MCAP Data column. The new column will be filled with zeroes to
    prevent errors from the colcomp module. The process can be repeated until
    a column with the current weekday exists."""
        
    EST = pytz.timezone('US/Eastern')
    latest_date_col = np.where(metrics.df.columns == metrics.volatile_column)[0][0] - 1
    new_date = metrics.df.columns[latest_date_col] + dtt.timedelta(days=7)
    sunday_date = EST.localize(new_date) - dtt.timedelta(hours=4) # EST = GMT - 4
    # handle daylight savings time
    DST = is_dst(EST)
    if DST is False:
        sunday_date -= dtt.timedelta(hours=1)
    
    col_num = int(np.where(metrics.df.columns == metrics.volatile_column)[0][0] + 2)
    max_row = int(len(metrics.df.index) + 1)
    xlShiftToRight = xw.constants.InsertShiftDirection.xlShiftToRight
    
    print('Adding new week column...',end=''),
    
    metrics.sheet.range((1,col_num)).api.EntireColumn.Insert(Shift=xlShiftToRight)
    metrics.sheet.range((1,col_num)).api.value = sunday_date
    metrics.sheet.range((2,col_num),(max_row,col_num)).api.value = 0
    metrics.book.save()
    metrics.extract()
    
    print('Done')
            
    return