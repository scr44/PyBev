from . import metricsobj as mo
from . import datecheck as dc
from . import mapping as mp
from . import colcomp as cc
import datetime as dtt
import time


def stage_select():
    metrics = 'blank'
    while True:
        stage = input(
"""\n Select stage:
 1. Data extraction
 2. Date entry & map MCAP data
 3. Preliminary column comparison
 4. Troubleshooting
 5. Report generation
Type 'q' to quit.\n\n""")
        try:
            stage = int(stage)
        except ValueError:
            stage = stage
        if stage == 1:
            mcap, metrics = stage_one()
        elif stage == 2:
            try: stage_two(mcap, metrics)
            except NameError: print('Please run stage 1 first.')
        elif stage == 3:
            try: stage_three(mcap, metrics)
            except NameError: print('Please run stage 2 first.')
        elif stage == 4:
            try: ts = stage_four(mcap, metrics)
            except NameError: print('Please run stage 3 first.')
        elif stage == 5:
            try: stage_five(mcap, metrics, ts)
            except NameError: print('Please run stage 4 first.')
        elif stage == 'q':
            print('\nTerminating program.')
            return metrics
        elif stage == 'friendly q':
            print('\nGoodbye!')
            return metrics
        elif stage == 'dramatic q':
            print('\nNow, these data will be lost... like tears in the rain...')
            return metrics
        elif stage == 'whiterabbit.obj':
            print('PERMISSION DENIED... ',end=''),
            time.sleep(1)
            print('and...\n')
            time.sleep(1)
            for i in range(0,10):
                print("""                                  AH AH AH!
                        YOU DIDN'T SAY THE MAGIC WORD!\n""")
                time.sleep(.4)
        else:
            print('Invalid stage, please try again.\n')
            continue

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
    
def stage_one():
    """Stage one is where data is extracted from the auto MCAP pull and the
    Metrics excel document, pivoted, and prepared for further analysis."""
    
    mcap_path = panel_selection()
    
    metrics_path = (input('Panel Metrics file location (press enter for default): ')
                # or r'C:\Users\sroy\Documents\BevAl Metrics\2017 BevAl Metrics.xlsx')
                or r'C:\Users\sroy\Documents\BevAl Metrics\test.xlsx')
    
    mcap = mo.MCAPData(mcap_path)
    
    metrics = mo.PanelMetrics(metrics_path)
    
    mcap.extract()
    
    metrics.extract()
    
    metrics.connect_book()
    
    mcap.fpivot()
    
    print('Data ready for processing.\n')
    
    return mcap, metrics
    
def stage_two(mcap,metrics):
    if metrics.volatile_column not in metrics.df.columns:
        metrics.volatile_column = input('Name of the metrics column to write pivoted data to: ')
    
    print('\n')
    
    while True:
        week_date, end = dc.week_date_input()
        metrics.book.save()
        if end == 0: # this whole 'end' thing is dead code, should be cleaned up
                     # at some point; but this could require rewriting all of
                     # the mapping module
            metrics.extract()
            metrics.week_date = week_date
            x = mp.map_index(metrics.week_date, mcap.pivot_df, metrics.df,
                                metrics.volatile_column,agg_func='len')
            if x == 'default':
                break
            elif x == 'invalid':
                continue
            else:
                if (input('Filter-safe write y/n? ') or 0) == 'n':                    
                    metrics.update_file(metrics.volatile_column,filter_safe=0)
                    break
                else:
                    metrics.update_file(metrics.volatile_column,filter_safe=1)
                    break
        else: break
    print('Mapping complete.\n')
    return
    
def stage_three(mcap,metrics):
    print('Beginning column comparison...')
    
    cc.preliminary_update(metrics,mcap) # updates 0s to ints or pending and flags ?s
    
    print('Column comparison complete.')
    return
    
def stage_four(mcap,metrics):
    ts = mo.Troubleshooter(metrics)
    # ts.dupe_check()
    # 
    # ts.resolved_issues()
    # 
    # ts.unresolved_issues()
    return ts
    
def stage_five(mcap,metrics,ts):
    # report = pb.mo.Report(ts)
    #
    # report.gen()
    # 
    # report.save()
    # 
    # report.open()
    return
    
def monday_archive(metrics):
    
    return