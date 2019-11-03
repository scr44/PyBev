import numpy as np
import xlwings as xw
import pandas as pd
import datetime as dtt
import dateutil as dtu

#Stage 1 functions
#spotpull: pulls the data from MCAP

#spotfill: Fills the 'Spotfire Data' column on the BAM
def spotfill(weeksago=0,sdpath=r'C:/Users/sroy/Documents/Projects/PyBooze/data.csv',bampath=r'C:/Users/sroy/Documents/Projects/PyBooze/BAM.xlsx'):
    #weeksago is the number of weeks prior to the rundate that you want to check; default is 0 (current week). sdpath and bampath are the file paths for the spotfire data and BAM respectively.
    #
    #future: using weeksago makes you do VLOOKUP counting, gotta find a better way with just date input
    #
    #Create dataframes from Spotfire & BAM
    print('Extracting data (this may take a while!)...')
    with open(sdpath,encoding='UTF-16') as f:
        sd = pd.read_csv(f,delimiter='\t',parse_dates=['WeekOf','BreakDt','EndDt','QCDt'], index_col=0) #make sure to parse_dates, or you'll get strings instead of sortable datetimes!
    bam = pd.read_excel(bampath, index_col=0)
    
    #Create Pivot Table of Spotfire Data
    pt = pd.pivot_table(sd,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])
    
    #pseudo-INDEXMATCH to fill BAM 'Spotfire Data' column
    bam['Spotfire Data'] = bam.index.to_series().map(pt.fillna(0)['len',weekof])
    
    #psuedo-INDEXMATCH to fill the BAM Dataframe's 'Spotfire Data' column
    #print('Running indexmatch...')
    #weekColNum = np.where(bam.columns.values=='Spotfire Data')[0][0] - 1 - weeksago #column number of the week you're checking
    #weekof = bam.columns[weekColNum] 
    #for i in range(0,len(bam.index),1):
    #    rmc = bam.index[i]
    #    try:
    #        count = pt.fillna(0).loc[rmc]['len',weekof] #this try-except block replicates the #N/A returning functionality of INDEXMATCH
    #        bam.set_value(rmc,'Spotfire Data',count)
    #    except KeyError:
    #        bam.set_value(rmc,'Spotfire Data',np.nan)
    
    #Write the new Spotfire Data to the BAM
    print('Writing data to file...')
    b = xw.Book(bampath)
    s = b.sheets['Sheet1']
    x = len(bam.index)
    y = weekColNum + 3 + weeksago # the +3 is because excel starts arrays at 1 (+1), the DFs use excel column 1 as the index (+1), and Spotfire is 1 column right of the dates (+1)
    #readarray = s.range((2,1),(int(x),int(y))).value #xlwings doesn't like having non-numeric coordinates, even simple variables
    #s.range((1,1),(int(x),int(y))).expand().value = bam #this version will overwrite all data to the left of the spotcolumn
    s.range((2,int(y)),(int(x),int(y))).value = bam['Spotfire Data'].values[np.newaxis].T #we have to turn the 1D array into a 2D in order to transpose it
    
    print('''Job's done, boss!''')
    return

#>>>Stage 1
weeksago = input('Weeks ago = ') or 0 #look into making this a date range instead with dtt deltas

sdpath = input('Spotfire File Location: ') or r'C:\Users\sroy\Documents\Projects\PyBooze\data.csv'

bampath = input('Metrics File Location: ') or r'C:\Users\sroy\Documents\Projects\PyBooze\BAM.xlsx'

#spotpull()
spotfill(weeksago,sdpath,bampath)