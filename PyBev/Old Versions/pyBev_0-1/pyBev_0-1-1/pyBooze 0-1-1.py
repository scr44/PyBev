#pyBooze - daily panel updates with python
#
#Alpha version 0.1.1 (Data reading) changelog:
#can now read spotfire's UTF-16 LE BOM csv outputs into pandas DF
#automated pivot table creation in Stage 1

#--Script run stages--
#Stage 1: Spotfire/Database query (get data to feed into column comparison)
#Stage 2: Column Comparison (compare columns and return list of problems)
#Stage 3: AC Database query (checking AC for P1 and P2 problems)
#Stage 4: MCAP Database query (check MT for paper/insert and JA problems)
#Stage 5: Report (produce a report for the user to investigate)

import numpy as np
import xlwings as xw
import pandas as pd
import datetime as dtt

#Stage 1 functions

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

#open the data file from a user-given or default pathname and create a dataframe
pathname = raw_input('Spotfire data file path: ') or r'C:\Users\sroy\Documents\Projects\PyBooze\data.csv'

with open(pathname,encoding='UTF-16') as f:
    df = pd.read_csv(f,delimiter='\t')

#create a pivot table: RetMktConcatenated vs. WeekOf, count of VehicleId
dp = pd.pivot_table(df,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])

#>>>Stage 2
#sort the data

#>>>Stage 3
#>>>Stage 4
#>>>Stage 5

#Program End