import pybev as pb
import datetime as dtt
from pybev import colcomp as cc
from pybev import troubleshooting as ts
from pybev import metricsobj as mo

mcap, metrics = pb.stage_one()

metrics.week_date = dtt.datetime(2017,7,23)

metrics.cutoff_date = dtt.datetime(2017,8,1)

# pb.stage_three(mcap,metrics)
# 
# pb.stage_four(mcap,metrics)

# Stage 5

report = mo.Report(mcap,metrics)

# ts.duplicate_items(mcap,metrics,report)

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
    mcap_status = ts.mk_mcap_status(mcap.panel,status)
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

# ts.resolved_items(mcap,metrics,report)
# 
# ts.unresolved_items(mcap,metrics,report)