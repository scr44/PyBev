import os
import sys
import pybev as pb
import progress

os.chdir(os.path.dirname(sys.argv[0])) # go to the pyBeverage.py file directory
print('''
===================================Stage 1=====================================
''')
# path inputs - consider a 'with x as y' statement for conciseness & no globals
mcap_path = (input('MCAP data file location (press enter for default): ') 
            or r'C:\Users\sroy\Documents\BevAl Metrics\MCAP - Print Data Tool.csv')

metrics_path = (input('Panel Metrics file location (press enter for default): ')
            or r'C:\Users\sroy\Documents\BevAl Metrics\2017 BevAl Metrics.xlsx')
# Insert a query_YN() function equivalent here to create a new data file and pull
# the MCAP database to create it if desired.

mcap = pb.metricsobj.MCAPData(mcap_path)
metrics = pb.metricsobj.PanelMetrics(metrics_path)

print('\tExtracting data; this may take a few minutes... ',end=''),
mcap.extract()
metrics.extract()
print('Done')

print('Connecting to excel spreadsheet... ',end=''),
metrics.connect_book()

print('Creating pivot table (Count of VIDs)... ',end=''),
mcap.fpivot()
print('Done')

# Run the mapping loop for live analysis (consider splitting this to allow
# column comparison and troubleshooting for each loop).
print('Mapping MCAP data to Metrics (press enter to proceed to column comparison):')
pb.mapping.mapping_loop(mcap, metrics)

print(' '*27,'>>>Stage 1 Complete<<<')


# print('''
# ===================================Stage 1=====================================
# ''')
# # get cutoff date
#check_cutoff = pb.datecheck.check_before_input()

# # run comparison (very complex, possibly write a comparison module instead)
# comparison_date = comparison_date_input()
# metrics.column_comparison(comparison_date)