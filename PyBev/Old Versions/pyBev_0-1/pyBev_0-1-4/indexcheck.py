# Index checking functions for comparing metrics & pivot table
import pandas as pd
import datecheck


def valid_index_check(column_name, check_df, agg_func=None):
    """Checks to see whether a given column_name is a column header in the
    dataframe check_df. Returns either 'valid' or 'invalid'. If check_df is a
    pivot table with an agg_func, then the argument needs to be provided to
    properly check the column."""
    
    if column_name == 'default':
        return 'default'
    elif agg_func == None:
        if (column_name in check_df.columns == True):
            return 'valid'
        else:
            return 'invalid'
    else:
        if (column_name in check_df[agg_func].columns == True):
            return 'valid'
        else:
            return 'invalid'

def valid_column_values(column_name, check_df, agg_func=None):
    """If given a valid column header, returns the column values. If given an
    invalid header, returns an invalid notification. If given a default marker,
    carries the default through."""
    
    valid_check = valid_index_check(column_name, check_df, agg_func)
    if column_name == 'default':
        return 'default'
    elif valid_check == 'valid':
        if agg_func == None:
            return check_df[column_name].values
        else:
            return check_df[agg_func, column_name].values
    else:
        return 'invalid'   

def map_to_metrics(week_date, mcap_pivot_df, metrics_df, volatile_column):
    """Takes a given week_date and maps the corresponding pivot table data to
    a given column in the Metrics dataframe."""

    values = valid_column_values(week_date,mcap_pivot_df,agg_func='len')
    if values == 'default':
        return 'default'
    elif values == 'invalid':
        print('Invalid weekdate. Please use the Sunday date beginning the week.')
        return 'invalid'
    else:
        metrics_df[metrics_data_column] = metrics_df.index.to_series().map(mcap_pivot_df.fillna(0)[agg_func,week_date])
        return 'complete'
        print('Success.')
        
def mapping_loop(MCAP, Metrics): #must get classes working
    """Loops the mapping function until the user quits."""
    
    print('Mapping MCAP data to Metrics (press enter to end)...',end=''),
    while True:
        week_date = datecheck.week_date_input()# must get datecheck module working
        x = map_to_metrics(week_date, MCAP.mcap_pivot_df, Metrics.metrics_df,
                            Metrics.volatile_column)
        if x == 'default':
            print('Mapping complete.')
            break
        elif x == 'invalid':
            continue
        else:
            Metrics.update_metrics()
            continue
    return