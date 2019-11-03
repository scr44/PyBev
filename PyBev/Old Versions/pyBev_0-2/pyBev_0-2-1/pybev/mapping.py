"""Functions to map data from the mcap pivot table to the metrics volatile column."""


from . import datecheck
import pandas


def valid_index_check(column_name, check_df, agg_func=None):
    """Checks to see whether a given column_name is a column header in the
    dataframe check_df. Returns either 'valid' or 'invalid'. If check_df is a
    pivot table with an agg_func, then the argument needs to be provided to
    properly check the column."""
    
    if column_name == 'default':
        return 'default'
    elif agg_func == None:
        if ((column_name in check_df.columns) == True):
            return 'valid'
        else:
            return 'invalid'
    else:
        if ((column_name in check_df[agg_func].columns) == True):
            return 'valid'
        else:
            return 'invalid' 

def map_to_metrics(week_date, mcap_pivot_df, metrics_df, volatile_column, agg_func='len'):
    """Takes a given week_date and maps the corresponding pivot table (Count of
    unique ads) data to a given column in the Metrics dataframe."""
    
    validity = valid_index_check(week_date,mcap_pivot_df,agg_func)
    if validity == 'default':
        return 'default'
    elif validity == 'invalid':
        print('Invalid weekdate. Please use the Sunday date beginning the week.')
        return 'invalid'
    else:
        metrics_df[volatile_column] = metrics_df.index.to_series().map(mcap_pivot_df.fillna(0)['len',week_date])
        print('\tMapping successful.')
        return 'complete'
        
def mapping_loop(mcap, metrics):
    """Loops the mapping function until the user quits."""
    
    while True:
        week_date = datecheck.week_date_input()
        metrics.extract()
        x = map_to_metrics(week_date, mcap.pivot_df, metrics.df,
                            metrics.volatile_column)
        if x == 'default':
            break
        elif x == 'invalid':
            continue
        else:
            metrics.update_file()
            continue
    return