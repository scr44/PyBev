import os
import sys
import pybev as pb

os.chdir(os.path.dirname(sys.argv[0])) # go to the pyBeverage.py file directory

#==================================Stage 1=====================================

# path inputs - consider a 'with x as y' statement for conciseness & no globals
mcap_path = (input('MCAP data file location (press enter for default): ') 
            or r'C:\Users\sroy\Documents\BevAl Metrics\MCAP - Print Data Tool.csv')
            # or 'Z:\\'+dtt.datetime.today().strftime('%m%d%Y_QC_Completed_Beval.txt') )
            
#mcap_path = pb.panel_selection()

metrics_path = (input('Panel Metrics file location (press enter for default): ')
            or r'C:\Users\sroy\Documents\BevAl Metrics\2017 BevAl Metrics.xlsx')
            # or r'C:\Users\sroy\Documents\BevAl Metrics\2017 BevAl Metrics Test.xlsx')

# Insert a query_YN() function equivalent here to create a new data file and pull
# the MCAP database to create it if desired.

mcap = pb.mo.MCAPData(mcap_path)
metrics = pb.mo.PanelMetrics(metrics_path)

print('\tExtracting data; this may take a few minutes... ',end=''),
mcap.extract()
metrics.extract()
print('Done')

print('Connecting to excel spreadsheet... ',end=''),
metrics.connect_book()

print('Creating pivot table (Count of VIDs)... ',end=''),
mcap.fpivot()
print('Done')

if metrics.volatile_column not in metrics.df.columns:
    metrics.volatile_column = input('Name of the metrics column to write pivoted data to: ')

# Run the mapping loop for live analysis (consider splitting this to allow
# column comparison and troubleshooting for each loop).
print('Mapping MCAP data to Metrics (end date entry to proceed to column comparison):')
pb.mp.mapping_loop(mcap, metrics) # this step will be deprecated per the above


#==================================Stage 2=====================================
print('Beginning column comparison...')

pb.cc.preliminary_update(metrics,mcap) # includes naive update and problem identifying
# 
# pb.cc.end_date_update(mcap)
# 
# ts = pb.mo.Troubleshooter(metrics) # takes the ts_subframe and generates ts object
# 
# ts.dupe_check()
# 
# ts.resolved_issues() # finds existing items it thinks have been fixed and creates report
# 
# ts.
# 
#
#==================================Stage 3=====================================
#
# ts.