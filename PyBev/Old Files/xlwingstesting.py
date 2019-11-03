import xlwings as xw

import pandas as pd

wb = xw.Book() #opens new file

wb.save(r'C:\Users\sroy\Documents\Test Files\xlwings testing') # saves file

wb = xw.Book(r'C:\Users\sroy\Documents\Test Files\xlwings testing') # opens specific file

s1 = wb.sheets['Sheet1'] # sheets calls the sheet, s1 is now the sheet object

s1.range('A1').value = 'Hello, World!' # sets cell value

x = [[1, 2, 3], [4, 5, 6]]

s1.range('a1').value = x # writes an array starting in the cell specified

s1.range('a1').expand().value # returns the full array

s1.range('b1').expand().value # returns a subset array starting at the argument cell down to the bottom left cell

pd.DataFrame(s1.range('a1').expand().value, columns=['a','b','c']) # returns the array as a dataframe with row/column labels

df = pd.DataFrame([[1,2],[3,4]], columns=['a', 'b'])

## Ranges

xw.Range('A1') # Cell name
xw.Range('A1:C3') # Cell name range
xw.Range((1,1)) #Cell array position (excel starts at 1, not 0)
xw.Range((1,1),(3,3)) # Top left cell, bottom right cell range
xw.Range('NamedRange')
xw.Range(xw.Range('A1'), xw.Range('B2'))

## Round braces follow excel's 1-based arrays, square brackets follow python's 0-based arrays

rng = wb.sheets[0].range('A1:C2')

#>>> Sample Spotfire Data Update
wb = xw.Book(r'C:\Users\sroy\Documents\Projects\PyBooze\BAM.xlsx')
#wb2 = xw.Book(r'https://markettrackllc.sharepoint.com/sites/SolonAdOps/Team Sites/coverage&collections/Shared Documents/Coverage Metrics/2017 BevAl Metrics', 'r+')
bam = wb.sheets['Sheet1']

bamdf = bam.range('A1:F6').options(pd.DataFrame).value