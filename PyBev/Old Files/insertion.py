import xlwings as xw
import numpy as np
import pandas as pd

def f1():
    bk = xw.Book(r'C:\Users\sroy\Documents\Test Files\insertion test.xlsx')
    
    sht = bk.sheets['Sheet1']
    
    range_obj = sht.range((1,2),(2,2))
    
    range_obj.api.Insert()

def f2():
    file_path = r'C:\Users\sroy\Documents\BevAl Metrics\2017 BevAl Metrics.xlsx'
    df = pd.read_excel(file_path, index_col=0)
    bk2 = xw.Book(file_path)
    sht1 = bk2.sheets['Sheet1']
    sht2 = bk2.sheets['Sheet2']
    
    col_num = int(np.where(df.columns == 'MCAP Data')[0][0] + 2)
    max_row = int(len(df.index) + 2)
    
    # range_obj = sht2.range((1,2),(2,2))
    
    range_obj = sht1.range((2,col_num),(max_row,col_num))
    
    # range_obj.api.Insert()
    
    range_obj.api.EntireColumn.Insert()
    
    # range_obj.api.Select();import sys;sys.exit()