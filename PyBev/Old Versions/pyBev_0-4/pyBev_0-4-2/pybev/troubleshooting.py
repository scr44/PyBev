import numpy as np
import pandas as pd
import xlwings as xw
import datetime as dtt
from . import metricsobj as mo
from . import colcomp as cc
from . import mapping as mp


def duplicate_items(mcap,metrics,report):
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    
    dff = cc.duplicate_filter(metrics.df,A,B)
    
    status = 'Duplicate'
    
    mystery_ticket_count = 1
    
    for i in range(0,len(dff.index)):
        ticket_count = (report.duplicate_count + 1)
        
        RetMkt = dff.index[i]
        ticket = mo.Ticket(mcap,metrics,RetMkt,status)
        
        # Ticket ID Info
        ticket.RU = 'R'
        ticket.tick_num = ticket_count
        ticket.ID_gen()
        ticket.name_gen()
        
        # Duplicate Info
        ticket.original_ad_count = int(dff.loc[RetMkt,A])
        ticket.revised_ad_count = int(dff.loc[RetMkt,B])
        
        # MCAP Info (need to create major function here, pulling from Z:\ files)
        mcap_status = mk_mcap_status(mcap.panel,status)
        mcap_status.extract()
        status_dff = cc.cutoff_filter_2(mcap_status.df,A,cutdt)
        
        try:
            ticket.VID_list[status] = status_dff.loc[RetMkt]['Vehicleid'].values.tolist()
            
            # Issue Info
            ticket.descrip = 'Duplicate removed'
            
            report.ticket_list[ticket.tick_ID] = ticket
            report.contents_dupe[ticket.tick_ID] = ticket.descrip
            
            report.duplicate_count += 1
            
        except KeyError: # no duplicates found for that RetMkt
            metrics.df.loc[RetMkt,A] = '?'
            ticket.descrip = 'Ad removed, no duplicate found'
            ticket.RU = 'U'
            ticket.tick_num = mystery_ticket_count
            ticket.ID_gen()
            ticket.name_gen()
            
            report.ticket_list[ticket.tick_ID] = ticket
            report.contents_unres[ticket.tick_ID] = ticket.descrip
            
            mystery_ticket_count += 1
            report.unresolved_count += 1
    return
    
def resolved_items(mcap,metrics,report):
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    status = ['Indexed', 'Review', 'Scraped', 'AC QC', 'Published', '?']
    ticket_count = (report.resolved_count + 1)
    
    for i in range(0,len(status)):
        dff = cc.cutoff_filter(metrics.df)
        dff = cc.status_filter(dff, A, status[i])
        dff = cc.status_filter(dff, B, 'int>0') # selects only seemingly-resolved issues
        
        for x in range(0,len(dff.index)):
            RetMkt = dff.index[x]
            ticket = mo.Ticket(mcap,metrics,RetMkt,status[i])
            
            # Ticket ID info
            ticket.RU = 'R'
            ticket.tick_num = ticket_count
            ticket.ID_gen()
            ticket.name_gen()
            
            # MCAP Info
            mcap_status = mk_mcap_status(mcap.panel,status)
            mcap_status.extract()
            status_dff = cc.cutoff_filter_2(mcap_status.df,A,cutdt)
        
            ticket.VID_list[status] = status_dff.loc[RetMkt]['Vehicleid'].values.tolist()
            
            # AC Info if necessary
            # AC_info(ticket,RetMkt)
            
            ticket_count += 1
            report.resolved_count += 1
            
            dff.loc[RetMkt,A] = dff.loc[RetMkt,B]
            dff.loc[RetMkt,'Issue'] = np.nan # removes stated issue
            
        mp.map_small_to_big(A,dff,metrics.df,agg_func=None)
        
    return
    
def unresolved_items(mcap,metrics,report):
    A,B,C,D,cutdt = cc.shorthand_names(metrics)
    status = ['Indexed', 'Review', 'Scraped', 'AC QC', 'Published', '?']
    
    for i in range(0,len(status)):
        dff = cc.cutoff_filter(metrics.df)
        dff = cc.status_filter(dff, A, status[i])
        
        dff = fix_status(dff,status[i])
    
    return


#=========================== MCAP Status Checks ===============================


def mk_mcap_status(panel,status):
    file_path = 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_')+status+'_'+panel+'.txt'
    mcap_path = [file_path, panel]
    
    return mo.MCAPData(mcap_path)
    
def mcap_info(ticket,RetMkt,mcap_status):
    ticket.ads_present = ads_present(RetMkt,mcap_status)
    return
    
def ads_present(RetMkt,mcap_status):
    
    return
    
def days_overdue(RetMkt,mcap_status):
    
    return
    
def VID_statuses(RetMkt,mcap_status):
    
    return
    
def VIDs(RetMkt,mcap_status):
    
    return
    
def last_package_dt(RetMkt,mcap_status):
    
    return
    
def last_package_EID(RetMkt,mcap_status):
    
    return


#========================= status troubleshooting =============================


def fix_status(dff,status):
    
    # create a new ticket inside the subfunctions and troubleshoot
    if status == 'Indexed':
        return fix_indexed(dff)
    if status == 'Review':
        return fix_review(dff)
    if status == 'Scraped':
        return fix_scraped(dff)
    if status == 'AC QC':
        return fix_acqc(dff)
    if status == 'Published':
        return fix_published(dff)
    if status == '?':
        return fix_unknown(dff)
    
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