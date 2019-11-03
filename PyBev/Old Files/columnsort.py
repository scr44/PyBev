import xlwings as xw
# from xlwings.constants import YesNoGuess


bk1 = xw.Book(r'C:\Users\sroy\Documents\Test Files\xlwings sorting.xlsx')
sht1 = bk1.sheets['Sheet1']

# bk2 = xw.Book(r'C:\Users\sroy\Documents\BevAl Metrics\test.xlsx')
# sht2 = bk2.sheets['Sheet1']

def xl_col_sort(sht,col_num):
    xlGuess = 0
    xlYes = 1
    xlNo = 2

    # sht.range((2,col_num)).api.Sort(Key1=sht.range((2,col_num),(8,col_num)).api, Order1=1,
    #                                     Header=xlYes)
                                        
    sht.range((2,1),(8,4)).api.Sort(Key1=sht.range((2,col_num)).api, Order1=1,
                                        Header=xlYes)
    return
    
# xl_col_sort(sht1,2)