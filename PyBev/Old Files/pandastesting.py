import xlwings as xw
import numpy as np
import pandas as pd
import datetime as dtt

#Opening the CSV and decoding it from UTF-16 (unicode is THE DEVIL)

with open(r'C:\Users\sroy\Documents\Projects\PyBooze\data.csv',encoding='UTF-16') as f:
    df = pd.read_csv(f,delimiter='\t',parse_dates=['WeekOf','BreakDt','EndDt','QCDt'])
    
#calling the first row
df[:1]

#calling the first column
df['Ret.Descrip']

#display index (x-labels)
df.index

#explicitly
df.index.values

#display columns (y-labels)
df.columns

#full DF array
df.values

#pivot table RMC vs. WeekOf, count of VIDs
dp = pd.pivot_table(df,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])

#get current date
cdt = dtt.datetime.now().date()

#column of datetimes - unneeded if you add parse_dates to the read_csv
dtcol = pd.to_datetime(df['WeekOf'])

#sort by WeekOf
dfsorted = df.sort_values(by='WeekOf')

dpsorted = pd.pivot_table(dfsorted,index='RetMktConcatenated',columns='WeekOf',values='VehicleId', aggfunc=[len])

bam = pd.read_excel(r'C:\Users\sroy\Documents\Projects\PyBooze\BAM.xlsx')