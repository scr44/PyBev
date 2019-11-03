##Index Match in Python with pandas
#Remember that dataframes start at 0, excel starts at 1
#This only works if both DFs have the same indices (integers, strings, whatever)
import numpy as np
import pandas as pd

#sample dataframes
d = {'Match Column' : [0.,1.,2.,3.,4.,7.,'string'],
     'Read Column' : ['zero','one','two','three','four','seven','string']}

dfRead = pd.DataFrame(d)

d2 = {'Match Column' : [0.,1.,2.,3.,4.,5.,6.,7.,'8'],
      'Write Column' : [0,0,0,0,0,0,0,0,'0']}

dfWrite = pd.DataFrame(d2)

#test arguments
ReadColumn = 'Read Column'
WriteColumn = 'Write Column'
ReadMatchColumn = 'Match Column'
WriteMatchColumn = 'Match Column'

def indexmatch(dfRead, dfWrite, ReadColumn, WriteColumn, ReadMatchColumn, WriteMatchColumn, skiprows=0):
#convert the string inputs to a column number for each dataframe
    RCNum = np.where(dfRead.columns == ReadColumn)[0][0]
    WCNum = np.where(dfWrite.columns == WriteColumn)[0][0]
    RMCNum = np.where(dfRead.columns == ReadMatchColumn)[0][0]
    WMCNum = np.where(dfWrite.columns == WriteMatchColumn)[0][0]

    for i in range(skiprows,len(dfWrite.index),1):
        match = dfWrite.loc[dfWrite.index[i]][WMCNum] #the value we're using to match the columns    
        try:
            matchind = dfRead.index[np.where(dfRead[ReadMatchColumn] == match)[0][0]]
            value = dfRead.fillna('#N/A').loc[matchind][RCNum] #replaces DF NaN values with excel's #N/A, can change to 0 if you want empty cells to be 0
            dfWrite.set_value(dfWrite.index[i],WriteColumn,value)
        except KeyError:
            dfWrite.set_value(dfWrite.index[i],WriteColumn,np.nan) #if there is no match, write NaN to the 'cell'
        except IndexError:
            dfWrite.set_value(dfWrite.index[i],WriteColumn,np.nan)
            
# OR... The easy, built-in way!
dfWrite['Write Column'] = dfWrite['Match Column'].map(dfRead.set_index('Match Column')['Read Column'])
#To match on the index of dfRead, skip the .set_index(...) step. To match on the index of dfWrite, replace dfWrite['Match Column'].map with dfWrite.index.to_series().map