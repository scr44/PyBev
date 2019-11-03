import pybev as pb
from pybev import datecheck as dc
from pybev import colcomp as cc
from pybev import troubleshooting as ts
from pybev import mapping as mp
from pybev import metricsobj as mo
import datetime as dtt
import numpy as np
import os
import time

os.chdir(r'C:\Users\sroy\Documents\Projects\PyBev\pyBev_0-4-5') 


def setup():
    
    mcap_path = ['Z:\\'+dtt.datetime.today().strftime('%m%d%Y_QC_Completed_')
                        +'Beval'+'.txt','Beval']
                        
    mcap = mo.MCAPData(mcap_path)
    
    metrics = mo.PanelMetrics(r'C:\Users\sroy\Documents\BevAl Metrics\test.xlsx',mcap_path[1])
    
    mcap.extract()
    
    metrics.extract()
    
    metrics.connect_book()
    
    mcap.fpivot()
    
    metrics.week_date = dtt.datetime(2017,7,23)
    
    metrics.cutoff_date = dtt.datetime(2017,8,8)
    
    # TS-related functions
    
    report = mo.Report(mcap,metrics)
    
    panel = mcap.panel
    
    alt_mcap_path = ['Z:\\'+dtt.datetime.today().strftime('%m%d%Y_not_QCC_')
                        +panel+'.txt',panel]
                        
    alt_mcap = mo.MCAPData(alt_mcap_path)
    
    alt_mcap.extract()
    
    return [mcap, metrics, report, alt_mcap]

# Duplicate check

def duplicate_items(mcap,metrics,report,alt_mcap):
    
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    
    dff1 = cc.duplicate_filter(metrics.df,A,B) # B > A
    
    dff2 = cc.cutoff_filter_2(alt_mcap.df,A,
                                A+dtt.timedelta(days=7)) # BreakDt in range(A,A+wk)
    
    dff3 = cc.status_filter(dff2,'Vehicle_Status','Duplicate') # status == Duplicate
    
    print('Checking for items with duplicates:')
    time.sleep(.5)
    
    if len(dff1.index) == 0:
        print('    No duplicates found.')
    
    for i in range(0,len(dff1.index)):
        RetMkt = dff1.index[i]
        print('   %s' % RetMkt)
        
        # Mystery non-dupe
        if (len(dff1.index) != 0) and (RetMkt not in dff3.index):
            
            ticket = mo.Ticket(mcap,metrics,RetMkt,'Unknown')
            
            # Ticket ID Info
            ticket.RU = 'U'
            ticket.tick_num = report.unresolved_count + 1
            ticket.ID_gen()
            
            # Pseudo-dupe Info
            ticket.original_ad_count = metrics.df.loc[RetMkt,A]
            ticket.revised_ad_count = metrics.df.loc[RetMkt,B]
            
            # non-QCC MCAP Info
            try:
                try: unique_statuses = np.unique(
                    dff2.loc[RetMkt]['Vehicle_Status'].values,
                    return_counts=True)
                except AttributeError: unique_statuses = np.unique(
                    dff2.loc[RetMkt]['Vehicle_Status'],
                    return_counts=True)
                for i2 in range(0,len(unique_statuses[0])):
                    status = unique_statuses[0][i2]
                    ticket.VID_status_count[status] = unique_statuses[1][i2]
                    try: ticket.VID_list[status] = (
                            dff2[
                                dff2['Vehicle_Status'] == status
                                 ].loc[RetMkt]['Vehicleid'].values.tolist()
                                    )
                    except AttributeError: ticket.VID_list[status] = (
                            dff2[
                                dff2['Vehicle_Status'] == status
                                 ].loc[RetMkt]['Vehicleid']
                                    )
                            
                # Issue Info
                ticket.recommended_action = (
    'Check for alternate statuses, late packages, or processing errors.')
                ticket.descrip = 'Duplicate behavior, but no duplicate found.'
            
            except KeyError:
                ticket.recommended_action = (
                'Investigate RetMkt activity in MCAP between %s and %s.'
                % (A.strftime('%m/%d/%Y'), (A + dtt.timedelta(days=7)).strftime('%m/%d/%Y'))
                )
                ticket.descrip = 'No VIDs found.'
                continue
                        
            report.unresolved_count += 1
            
            report.ticket_list[ticket.tick_ID] = ticket
            report.contents_unres[ticket.tick_ID] = ticket.descrip
            
        # Duplicates found
        if RetMkt in dff3.index:
            
            ticket = mo.Ticket(mcap,metrics,RetMkt,'Duplicate')
            
            # Ticket ID Info
            ticket.RU = 'D'
            ticket.tick_num = report.resolved_count + 1
            ticket.ID_gen()
            
            # Dupe Info
            ticket.original_ad_count = metrics.df.loc[RetMkt,A]
            ticket.revised_ad_count = metrics.df.loc[RetMkt,B]
            
            # Duplicate MCAP Info
            status = 'Duplicate'
            ticket.VID_status_count[status] = len(dff3[dff3.index == RetMkt])
            try: ticket.VID_list[status] = dff3.loc[RetMkt]['Vehicleid'].values.tolist()
            except AttributeError: ticket.VID_list[status] = dff3.loc[RetMkt]['Vehicleid']
            
            # Issue Info
            ticket.descrip = 'Duplicate removed.'
            
            # Issue Fix
            metrics.df.loc[RetMkt,A] = metrics.df.loc[RetMkt,B]
            
            report.resolved_count += 1
            
            report.ticket_list[ticket.tick_ID] = ticket
            report.contents_dupe[ticket.tick_ID] = ticket.descrip
    
    return

# Resolved items
def resolved_items(mcap,metrics,report,alt_mcap):
    
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    
    dff1 = cc.cutoff_filter(metrics.df,A,cutdt)
    dff1 = cc.status_filter(dff1,A,status='not_int') # A is an issue type, B > 0
    
    dff2 = cc.cutoff_filter_2(mcap.df,A,
                                A+dtt.timedelta(days=7)) # QCC, Breakdt in range(A,A+wk)
    dff2 = dff2[
                dff2['Vehicle_Status'] != 'Duplicate'
                ]
    
    dff3 = cc.cutoff_filter_2(alt_mcap.df,A,
                                A+dtt.timedelta(days=7)) # non-QCC, Breakdt in range(A,A+wk)
    
    print('Updating resolved items:')
    time.sleep(.5)
    
    if len(dff1.index) == 0:
        print('    No resolved issues found.')
        
    for i in range(0,len(dff1.index)):
        RetMkt = dff1.index[i]
        print('   %s' % RetMkt)
        
        ticket = mo.Ticket(mcap,metrics,RetMkt,None)
        
        # Ticket ID Info
        ticket.RU = 'R'
        ticket.tick_num = report.resolved_count + 1
        ticket.ID_gen()
        
        # Issue Info
        ticket.status = metrics.df.loc[RetMkt,A]
        ticket.known_issue = metrics.df.loc[RetMkt]['Issue']
        
        # MCAP Info
        try:
            for i in range(0,len(dff2.loc[RetMkt]['Vehicle_Status'].values)):
                ticket.VID_list['QC Completed'] = dff2.loc[RetMkt]['Vehicleid'].values.tolist()
        except AttributeError:
            ticket.VID_list['QC Completed'] = dff2.loc[RetMkt]['Vehicle_Status']
        except KeyError: # no QCC ads detected... why is it on the list?
            continue
            
        try:
            try: unique_statuses = np.unique(
                    dff3.loc[RetMkt]['Vehicle_Status'].values,
                    return_counts=True)
            except AttributeError: unique_statuses = np.unique(
                    dff3.loc[RetMkt]['Vehicle_Status'],
                    return_counts=True)
                    
            for i2 in range(0,len(unique_statuses[0])):
                
                status = unique_statuses[0][i2]
                ticket.VID_status_count[status] = unique_statuses[1][i2]
                
                try: ticket.VID_list[status] = dff3[
                                dff3['Vehicle_Status'] == status
                                    ].loc[RetMkt]['Vehicleid'].values.tolist()
                except AttributeError:
                    ticket.VID_list[status] = dff3[dff3['Vehicle_Status'] == status
                        ].loc[RetMkt]['Vehicleid']
        except KeyError: # no non-QCC ads detected
            continue
        
        ticket.descrip = 'Ad processed.'
        
        report.unresolved_count += 1
        
        report.ticket_list[ticket.tick_ID] = ticket
        report.contents_unres[ticket.tick_ID] = ticket.descrip
        
        metrics.df.loc[RetMkt,A] = metrics.df.loc[RetMkt,B]
    
    return

def unresolved_items_known(mcap,metrics,report,alt_mcap):
    return
    
def unresolved_items_unknown(mcap,metrics,report,alt_mcap):
    return



args = setup()

duplicate_items(*args)

resolved_items(*args)

metrics = args[1]

metrics.book.save(r'C:\Users\sroy\Documents\BevAl Metrics\test2.xlsx')

metrics.update_file_column(metrics.week_date,filter_safe=0)

metrics.book.save()