# pyBev - daily metrics panel updates with python
# Alpha version 0.1.4 (classes and objects)
# 
# --Script run stages--
# Stage 1: Spotfire/Database query (get data to feed into column comparison)
# 
# Stage 2: Column Comparison (compare columns and return list of problems)
# 
# Stage 3: AC Database query (checking AC for P1 and P2 problems)
# 
# Stage 4: MCAP Database query (check MT for paper/insert and JA problems)
# 
# Stage 5: Report (produce a report for the user to investigate)
# 
#
#This is the function definition block.
import numpy as np
import pandas as pd
import xlwings as xw
import datetime as dtt

#Stage 1 functions
def spotpull():
    """Automatically queries the MCAP database. Default parameters are:
    Filters:
    Date range = YTD (1/1/YYYY - MM/DD/YYYY) | Status.Descrip = QC Complete
    Attributes:
    Ret.Descrip | Mkt.Descrip | RetMktConcatenated | VehicleId | WeekOf |
    BreakDt | EndDt | QCDt | QCDt-BreakDt | FlyerID
    """
    print('I wanna be a real function when I grow up!')
    return


    
def query_YN():
    """Gets an existing file path or creates a new file and pulls data from MCAP."""
    queryYN = input('Use existing data file? y/n: ') or 'y'
    if (queryYN == 'Yes' or queryYN == 'y' or queryYN == 'yes'):
        sdpath = (input('MCAP data file location (Press Enter for default): ')
            or r'C:\Users\sroy\Documents\BevAl Metrics\MCAP - Print Data Tool.csv')
    else:
        sdpath = input('Save new file to path: ')
        spotpull(sdpath)
        print('still a WIP')
    return sdpath
    
def week_init():
    """Creates an initial week datetime and determines what the checking cutoff
    to be used in Stage 2 is."""
    week = input('Week to check: MM/DD/YYYY\n')
    switch = 1
    while switch == 1:
        try:
            week = dtt.datetime.strptime(week,'%m/%d/%Y') #turns input to a datetime
            switch = 0
        except ValueError:
            week = input('Unrecognized date format, please try again: MM/DD/YYYY\n')
    beforeday = (input('Check days before date (Press enter to use today): MM/DD/YYYY\n')
        or dtt.date.today())
    if (beforeday != dtt.date.today()):
        switch = 1
        while switch == 1:
            try:
                beforeday = dtt.datetime.strptime(beforeday,'%m/%d/%Y')
                switch = 0
            except ValueError:
                beforeday = input('Unrecognized date format, please try again: MM/DD/YYYY\n')
    return week, beforeday

def spotextract(week,sdpath,bampath):
    """Create & pivot dataframes from MCAP and the Metrics excel."""
    print('Extracting data; this may take a few minutes... ',end=''),
    
    #Opening files and initializing dataframes.
    with open(sdpath,encoding='UTF-16') as f:
        sd = pd.read_csv(f,delimiter='\t',parse_dates=['WeekOf','BreakDt','EndDt','QCDt'], index_col=0)
        #make sure to use parse_dates, or you'll get strings instead of sortable datetimes!
    bam = pd.read_excel(bampath, index_col=0)
    print('Done')
    
    #Create Pivot Table of MCAP Data
    print('Pivoting data... ',end='')
    pt = pd.pivot_table(sd,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])
    print('Done')
    return bam, sd, pt
    
def spotmap(week, bam, pt):
    """Maps the pivoted data for the chosen week to the Metrics dataframe's Spotfire Data column."""
    print('Mapping MCAP data to Metrics... ',end=''),
    switch = 1
    while switch == 1:
        try:
            bam['Spotfire Data'] = bam.index.to_series().map(pt.fillna(0)['len',week])
            switch = 0
        except KeyError:
            print('Invalid date, please try again.')
            week = input('Week start date (Sunday): MM/DD/YYYY\n')
    print('Done')
    return bam

def bamwrite(week, bam, book):
    #Write the new Spotfire Data to the BAM
    print('Writing data to file... ',end=''),
    s = book.sheets['Sheet1']
    x = len(bam.index)
    
    #numpy starts at 0 (+1), dataframe uses 1st column as index (+1)
    y = np.where(bam.columns == 'Spotfire Data')[0][0] + 2
    
    #we have to turn the 1D array into a 2D in order to transpose it.
    s.range((2,int(y)),(int(x),int(y))).value = bam['Spotfire Data'].fillna('#N/A').values[np.newaxis].T
    
    #save the changes so that read_excel can pull the current metrics data
    book.save()
    print('Done')
    return
    
def spotfill():
    """Quickly writes pivoted data to the dataframe and book without 
    re-extracting from the data pull."""
    global pt, book
    x = 1
    book.save()
    bam = pd.read_excel(bampath, index_col=0)
    datestring = input('Input week: MM/DD/YYYY\n') or 0
    if datestring == 0:
        x = 0
    else:
        switch = 1
        while switch == 1:
            try:
                week = dtt.datetime.strptime(datestring,'%m/%d/%Y')
                switch = 0
            except ValueError:
                datestring = input('Unrecognized date format, please try again: MM/DD/YYYY\n')
        bam = spotmap(week, bam, pt)
        bamwrite(week, bam, book)
    return x
    
def fillLoop():
    """Loops the spotfill function for convenience while the user is actively
    reviewing the panel."""
    print('Now looping spotfill (press enter to quit).')
    x = 1
    while x != 0:
        x = spotfill()
    print('Ending spotfill.')
    return
    
#Stage 2 functions
#colsort: select a date column, pre-sort that column by expdt
def colsort():
    
    return
    
#colchoose: index the column for values that need to be checked
#(expdt < rundate or sysdate)
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


if __name__ == '__main__':
#>>>Stage 1
#input initial variables
    sdpath = query_YN()
    bampath = (input('Panel Metrics file location (Press enter for default): ')
        or r'C:\Users\sroy\Documents\BevAl Metrics\2017 BevAl Metrics.xlsx')
    book = xw.Book(bampath) #open the excel workbook
    week, beforeday = week_init()

#write the spotfire data column
    bam, sd, pt = spotextract(week,sdpath,bampath)
    fillLoop()
    print('Stage 1 Complete')

#>>>Stage 2
#>>>Stage 3
#>>>Stage 4
#>>>Stage 5

#Program End