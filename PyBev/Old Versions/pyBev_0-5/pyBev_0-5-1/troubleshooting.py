import numpy as np
import pandas as pd
import xlwings as xw
import datetime as dtt
from . import metricsobj as mo
from . import colcomp as cc
from . import mapping as mp


def duplicate_items(mcap,metrics,report,alt_mcap):
    
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    
    dff1 = cc.duplicate_filter(metrics.df,A,B) # B > A
    
    dff2 = cc.cutoff_filter_2(alt_mcap.df,A,cutdt) # BreakDt in range(A,cutdt)
    
    dff3 = cc.status_filter(dff2,'Vehicle_Status','Duplicate') # status == Duplicate
    
    for i in range(0,len(dff1.index)):
        RetMkt = dff1.index[i]
        
        # Non-Dupe Found
        if RetMkt not in dff3.index:
            
            ticket = mo.Ticket(mcap,metrics,RetMkt,'Unknown')
            
            # Ticket ID Info
            ticket.RU = 'U'
            ticket.tick_num = report.unresolved_count + 1
            ticket.ID_gen()
            
            # Pseudo-dupe Info
            ticket.original_ad_count = metrics.df.loc[RetMkt,A]
            ticket.revised_ad_count = metrics.df.loc[RetMkt,B]
            
            # non-QCC MCAP Info
            unique_statuses = np.unique(dff2['Vehicle_Status'].values,return_counts=True)
            try:
                for i2 in range(0,len(unique_statuses[0])):
                    status = unique_statuses[0][i2]
                    ticket.VID_status_count[status] = unique_statuses[1][i2]
                    ticket.VID_list[status] = (
                            dff2[
                                dff2['Vehicle_Status'] == status
                            ].loc[RetMkt]['Vehicleid'].values.tolist()
                            )
                            
                # Issue Info
                ticket.recommended_action = (
    'Check for alternate statuses, late packages, or processing errors.')
                ticket.descrip = 'Duplicate-like behavior, but no duplicate found.'
            
            except KeyError:
                ticket.recommended_action = (
                'Investigate RetMkt date range in MCAP.')
                ticket.descrip = 'No VIDs found.'
                continue            
                        
            report.unresolved_count += 1
            
            report.ticket_list[ticket.tick_ID] = ticket
            report.contents_unres[ticket.tick_ID] = ticket.descrip
            
        # Duplicates found
        if RetMkt in dff3.index:
            
            ticket = mo.Ticket(mcap,metrics,RetMkt,'Duplicate')
            
            # Ticket ID Info
            ticket.RU = 'R'
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
    
def resolved_items(mcap,metrics,report,alt_mcap):
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    return
    
def unresolved_items(mcap,metrics,report,alt_mcap):
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    
    # Existing issue reticketing
    dff = cc.cutoff_filter(metrics.df,A,cutdt)
    dff = cc.status_filter(dff, A, status='not_int')
    old_unresolved_items(mcap,metrics,report,alt_mcap,dff)
    
    # New issues
    dff = cc.cutoff_filter(metrics.df,A,cutdt)
    dff = cc.status_filter(dff, A, status='?')
    
    
    return
    
def old_unresolved_items(mcap,metrics,report,dff):
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    dff = dff[dff[A] != '?'] # other not-ints taken care of in container func
    ticket_count = 1
    
    for i in range(0,len(dff.index)):
        RetMkt = dff.index[i]
        status = dff.loc[i,A]
    
        ticket = mo.Ticket(mcap,metrics,RetMkt,status)
        
        # Ticket ID Info
        ticket.RU = 'R'
        ticket.tick_num = ticket_count
        ticket.ID_gen()
        
        # MCAP Info
        ticket.ads_present = None
        
        
        ticket_count += 1
        
    return


#=========================== MCAP Status Checks ===============================


def mk_mcap_status(panel,status):
    file_path = 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_')+status+'_'+panel+'.txt'
    mcap_path = [file_path, panel]
    
    return mo.MCAPData(mcap_path)


#========================= status troubleshooting =============================


def fix_status(dff,status,RU):
    
    # create a new ticket inside the subfunctions and troubleshoot
    if status == 'Indexed':
        return fix_indexed(dff,RU)
    if status == 'Review':
        return fix_review(dff,RU)
    if status == 'Scraped':
        return fix_scraped(dff,RU)
    if status == 'AC QC':
        return fix_acqc(dff,RU)
    if status == 'Published':
        return fix_published(dff,RU)
    if status == '?':
        return fix_unknown(dff,RU)
    
def fix_indexed(dff):
    
    return dff
    
def fix_review(dff):
    
    return dff

def fix_scraped(dff):
    
    return dff
    
def fix_acqc(dff):
    
    return dff
    
def fix_published(dff):
    
    return dff
    
def fix_unknown(dff):
    
    return dff