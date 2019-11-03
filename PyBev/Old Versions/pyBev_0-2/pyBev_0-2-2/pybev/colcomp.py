"""Functions to compare data from the metrics volatile column against the
corresponding metrics data column. This module can find discrepancies, make 
appropriate updates, and generate a list of problems for troubleshooting in
stages 3 and 4."""


# def compare_columns(ts,status):
#     
#     A = ts.week_date
#     B = ts.vol_col
#     
#     ts.filter(status) #filter on status
#     
#     for i in range(0,len(ts.index)): #what about when A is a string?
#         foo = bar
#     
# def preliminary_update(df):
#     # changes all the type(A)==int and A=='ND' end dates
#     
#     # do something to filter on cutoff_date
#     # filter on type(A) is int
#     naive_update(df) # if B > A: A = B
#     dupe_checker(df) # if B < A: A = B, report in Duplicates section
#     identify_problems(df) # if A = B = 0: A = '?'
#     end_date_update(df)
#     return
#     
# def naive_update(df):
#     return
#     
# def dupe_checker(df):
#     return
#     
# def identify_problems(df):
#     return
# 
# def end_date_update():
#     return
#     
# def compare_categories(ts):
#     """Breaks down the column comparison per category to improve runtime."""
#     
#     compare_columns(ts,'Indexed')
#     compare_columns(ts,'Review')
#     compare_columns(ts,'Scraped')
#     compare_columns(ts,'AC QC')
#     compare_columns(ts,'Published')
#     compare_columns(ts,'?')
#     
# def compare_columns(ts,status):
#     
#     A = ts.week_date
#     B = ts.vol_col
    # 
    # ts.filter(status) #filter on status
    # 
    # for i in range(0,len(ts.index)): #what about when A is a string?
    #     foo = bar