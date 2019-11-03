from . import metricsobj as mo
from . import datecheck as dc
from . import mapping as mp
from . import colcomp as cc
from . import troubleshooting as ts
import numpy as np
import xlwings as xw
import datetime as dtt
import time
import os


def run_main_program():
    print('\n=== pyBev v0.4.1 ===\n')
    mcap = None
    metrics = None
    report = None
    mcap, metrics, report = main_menu(mcap,metrics,report)
    
    return mcap, metrics, report


#================================== Menus =====================================


def main_menu(mcap,metrics,report):
    main_menu_string = """
  Main Menu
 1. Data extraction
 2. Set active date
 3. Map ad count
 4. Column comparison
 5. Fix & report problems
 6. Run full program
 7. Options
Type 'q' to quit.\n\n"""
    while True:
        print(main_menu_string)
        
        user_input = input()
        
        try: user_input = int(user_input)
        except ValueError: user_input = user_input
        
        if type(user_input) is int:
            mcap,metrics,report = program_stages(user_input,mcap,metrics,report)
        elif menu_commands(user_input) is 0:
            break
        else:
            continue
                
    return mcap,metrics,report
            
def options_menu():
    print("""\n Still under construction in this build!\n""")
    
    print(
"""
Active panel:
Active week:
Active metrics file:
""")
    return
        
def program_stages(stage,mcap,metrics,report):
    if stage == 1:
        mcap, metrics = stage_one()
    elif stage == 2:
        # try: 
        stage_two(metrics)
        # except NameError: print('Please run stage 1 first.')
    elif stage == 3:
        # try:
        stage_three(mcap, metrics)
        # except NameError: print('Please run stage 2 first.')
    elif stage == 4:
        # try:
        stage_four(mcap, metrics)
        # except NameError: print('Please run stage 3 first.')
    elif stage == 5:
        report = stage_five(mcap,metrics)
        # try: report = stage_five(mcap,metrics)
        # except NameError: print('Please run stage 4 first.')
    elif stage == 6:
        stage_six()
        print('Still under construction.')
    elif stage == 7:
        stage_seven()
    else:
        print('Unrecognized stage, please try again')
    
    return mcap,metrics,report
            
def menu_commands(user_input):
    if user_input == 'q':
        print('\nTerminating program.')
        return 0
        
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
                        YOU DIDN'T SAY THE MAGIC WORD!\n""")
            time.sleep(.4)
    else:
        print('Unknown command, please try again.\n')
    
    return None
    
    
#============================== Program Stages ================================


def stage_one():
    """Extracts data from the auto MCAP pull and the Metrics excel document,
    pivots where appropriate, and prepares it for further analysis."""
    
    mcap_path = panel_selection()
    
    metrics_path = (input('Panel Metrics file location (press enter for default): ')
                or r'C:\Users\sroy\Documents\BevAl Metrics\2017 BevAl Metrics.xlsx')
                # or r'C:\Users\sroy\Documents\BevAl Metrics\test.xlsx')
    
    print('Location set to '+metrics_path,end='\n')
    
    mcap = mo.MCAPData(mcap_path)
        
    metrics = mo.PanelMetrics(metrics_path)
    
    try:
        print('Extracting MCAP data... ',end=''),
        mcap.extract()
        print('Done')
        
        print('Extracting Metrics data... ',end=''),
        metrics.extract()
        print('Done')
    except FileNotFoundError:
        print('File not found, please try again.')
        time.sleep(1)
        return mcap, metrics
    
    metrics.connect_book()
    
    mcap.fpivot()
    
    monday_new_column(metrics)
    
    print('Data ready for processing.\n')
    
    return mcap, metrics
    
def stage_two(metrics):
    """User sets an active date for the program."""
    
    metrics.week_date = dc.choose_week()
    
    return
    
def stage_three(mcap,metrics):
    """Maps the VID count from the MCAP data to the metrics object and writes
    it to the excel document."""
    
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
        
    if (input('Filter-safe write y/n? ') or 0) == 'n':                    
        metrics.update_file_column(metrics.volatile_column,filter_safe=0)
    else:
        metrics.update_file_column(metrics.volatile_column,filter_safe=1)
    
    print('Mapping complete.')
    
    return
    
def stage_four(mcap,metrics):
    """Compares the active week column to the volatile column, updating Pending,
    Non-Drop, and Naive items. When done comparing, it updates all appropriate
    end dates by one week (will make this step more sophisticated later). Finally,
    the Metrics document is sorted by expected date and active week item status."""
    
    print('Beginning column comparison...')
    
    metrics.book.save()

    metrics.extract()
    
    cc.preliminary_update(mcap,metrics) # updates 0s to ints or pending and flags ?s
    
    metrics.xl_col_sort() # sorts all data by date ascending
    
    print('Column comparison complete.')
    
    return
    
def stage_five(mcap,metrics):
    
    report = mo.Report(mcap,metrics)
    
    metrics.book.save()
    
    metrics.extract()
    
    mcap_path = [0,0]
    mcap_path[0] = 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_QC_Completed_')+mcap.panel+'.txt'
    mcap_path[1] = mcap.panel
    
    alt_mcap = mo.MCAPData(mcap_path) # non-QCC mcap data
    
    ts.duplicate_items(mcap,metrics,report,alt_mcap)
    
    ts.resolved_items(mcap,metrics,report,alt_mcap)
    
    ts.unresolved_items(mcap,metrics,report,alt_mcap)
    
    return report
    
def stage_six():
    return
    
def stage_seven():
    options_menu()
    return
   
     
#============================== Stage Subfunctions ============================


def panel_selection():
    while True:
        panel = input(
"""Please select a panel:
 1. BevAl
 2. Non-Flash
 3. WIP
(Defaults to BevAl)\n""") or '1'
        if (panel == '1' or panel=='BevAl'):
            panel = 'Beval'
            break
        elif (panel == '2' or panel=='Non-Flash'):
            panel = 'NonFlash'
            break
        else:
            print('Unrecognized panel, please choose another.\n')
            continue
    mcap_path = [0,0]
    mcap_path[0] = 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_QC_Completed_')+panel+'.txt'
    mcap_path[1] = panel
    return mcap_path

def monday_archive(metrics):    
# def monday_archive(metrics,options):
    
    if dtt.datetime.today().weekday() == 0:
        if input(
'''Today is a Monday. Would you like to archive the Metrics file? y/n: ''') == 'y':
            
            # archive_path = options.archive_path
            archive_path = r'C:\Users\sroy\Documents\BevAl Metrics\Archive'
            
            filename = (archive_path + '\\' + 
                            dtt.datetime.today().strftime('%Y-%m-%d') + '.xlsx')
        
            if os.path.isfile(filename) == 0:
                print('Archiving data...\n',end=''), 
                
                metrics.book.save(filename)
                
                print('Done')
                print(
'''Data archived to %s
You can change the archive directory in Options.''' % archive_path)
            else:
                print('Archive file already exists, please delete before archival.')
    return
    
def monday_new_column(metrics):
    """On Monday, if there is no column with the current week date as a header,
    inserts a column with said week date between the latest week column and the
    MCAP Data column. The new column will be filled with zeroes to prevent errors
    from the colcomp module."""
    
    stripped_date = dc.date_to_datetime(dtt.datetime.today().date())
    
    if stripped_date.weekday() == 0:
        if stripped_date not in metrics.df.columns:
            
            col_num = int(np.where(metrics.df.columns == metrics.volatile_column)[0][0] + 2)
            max_row = int(len(metrics.df.index) + 2)
            xlShiftToRight = xw.constants.InsertShiftDirection.xlShiftToRight
            zero_array = np.zeros((max_row,), dtype=np.int)[np.newaxis].T
            
            print('Adding new week column...',end=''),
            
            range_obj = metrics.sheet.range((1,col_num))
            
            range_obj.api.Insert(Shift=xlShiftToRight)
            range_obj.api.value = zero_array
            
            print('Done')
    
    return

