#pyBooze - daily panel updates with python
#Alpha version 0.1.3 (Autofilling Spotfire Data)
#
#--Script run stages--
#Stage 1: Spotfire/Database query (get data to feed into column comparison)
#Stage 2: Column Comparison (compare columns and return list of problems)
#Stage 3: AC Database query (checking AC for P1 and P2 problems)
#Stage 4: MCAP Database query (check MT for paper/insert and JA problems)
#Stage 5: Report (produce a report for the user to investigate)
#
import numpy as np
import xlwings as xw
import pandas as pd
import datetime as dtt

#Stage 1 functions
def spotfill(weeksago,sdpath,bampath):
    #weeksago is the number of weeks prior to the rundate that you want to check; default is 0 (current week). sdpath and bampath are the file paths for the spotfire data and BAM respectively.
    
    #Create dataframes from Spotfire & BAM
    print('Extracting data (this may take a while!)... ',end='')
    with open(sdpath,encoding='UTF-16') as f:
        sd = pd.read_csv(f,delimiter='\t',parse_dates=['WeekOf','BreakDt','EndDt','QCDt'], index_col=0) #make sure to parse_dates, or you'll get strings instead of sortable datetimes!
    bam = pd.read_excel(bampath, index_col=0)
    print('Done')
    
    #Create Pivot Table of Spotfire Data
    print('Pivoting data... ',end='')
    pt = pd.pivot_table(sd,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])
    print('Done')
    
    #psuedo-INDEXMATCH mapping to fill the BAM Dataframe's 'Spotfire Data' column
    print('Mapping MCAP data to Metrics... ',end=''),
    weekColNum = np.where(bam.columns.values=='Spotfire Data')[0][0] - 1 - weeksago #column number of the week you're checking
    weekof = bam.columns[weekColNum] #returns the dtt obj of the week you're checking || replace this step with a direct datetime input        
    bam['Spotfire Data'] = bam.index.to_series().map(pt.fillna(0)['len',weekof])
    print('Done')
    

    
    print('''Job's done, boss!''')
    return bam

def bamwrite(bampath, bam):
    #Write the new Spotfire Data to the BAM
    print('Writing data to file... ',end=''),
    b = xw.Book(bampath)
    s = b.sheets['Sheet1']
    x = len(bam.index)
    y = weekColNum + 3 + weeksago # the +3 is because excel starts arrays at 1 (+1), the DFs use excel column 1 as the index (+1), and Spotfire is 1 column right of the dates (+1)
    s.range((2,int(y)),(int(x),int(y))).value = bam['Spotfire Data'].values[np.newaxis].T #we have to turn the 1D array into a 2D in order to transpose it
    print('Done')
    return
    
    
#Stage 2 functions
#colsort: select a date column, pre-sort that column by expdt
def colsort():
    
    return
    
#colchoose: index the column for values that need to be checked (expdt < rundate or sysdate)
def colchoose():
    
    return

#colcomp: compare the chosen date columns
def colcomp():
    
    return
    
#valchange: update column values based on contents of spotdata and issuetype
def valchange():
    
    return

#reportgen: generate a list of the values that need to be checked
def reportgen():
    
    return


#>>>Stage 1
#query the database
queryYN = input('Would you like a fresh set of data? y/n') or 'n'
if (queryYN == 'Yes' or queryYN == 'y' or queryYN == 'yes')
    sdpath = input('Save file to path: ')
    spotpull(sdpath)
elif (queryYN == 'No' or queryYN == 'n' or queryYN == 'no')
    break
else
    queryYN = input('''Unknown input, using old data.''') or 'n'
#input initial variables
WeekToCheck = input('Analyze week: YYYY MM DD\n') #do some fiddling to turn this into a datetime, try dtt.strptime
sdpath = input('MCAP data file path (press Enter if using fresh data): ') or sdpath
bampath = input('Panel Metrics path: ')
weeksago = #some math involving WeekToCheck - eventually remove this in favor of just using WeekToCheck as a datetime to call columns

#write the spotfire data column
spotfill(weeksago,sdpath,bampath)

#>>>Stage 2
#>>>Stage 3
#>>>Stage 4
#>>>Stage 5

#Program End