"""Functions to map data between dataframes."""


from . import datecheck


def valid_index_check(column_name, check_df, agg_func=None):
    """Checks to see whether a given column_name is a column header in the
    dataframe check_df. Returns either 'valid' or 'invalid'. If check_df is a
    pivot table with an agg_func, then the argument needs to be provided to
    properly check the column."""
    
    if agg_func == None:
        if ((column_name in check_df.columns) == True):
            return 'valid'
        else:
            return 'invalid'
    else:
        if ((column_name in check_df[agg_func].columns) == True):
            return 'valid'
        else:
            return 'invalid'

def map_index(index_col, source_df, target_df, target_column, agg_func=None):
    """Takes a given index column shared by source_df and target_df, and maps
    the corresponding data (e.g., a pivot table of VID count) to the target 
    column in the target dataframe."""
    
    validity = valid_index_check(index_col,source_df,agg_func)
    if validity == 'invalid':
        print('Column not found in target dataframe.')
        return
    else:
        if agg_func == None:
            target_df[target_column] = target_df.index.to_series().map(source_df.fillna(0)[index_col])
        else:
            target_df[target_column] = target_df.index.to_series().map(source_df.fillna(0)[agg_func,index_col])
        print('Mapping successful.')
        return
        
def map_small_to_big(shared_col,small,big,agg_func=None):
    """Overwrites the shared_col in the big dataframe with matching indexed
    values from the small dataframe."""
    
    small = small[shared_col].fillna('#N/A')
    
    validity = valid_index_check(shared_col,big,agg_func)

    if validity == 'invalid':
        print('Invalid weekdate. Please use the Sunday date beginning the week.')
        return
    else:
        if agg_func == None:
            big[shared_col] = small.combine_first(big[shared_col])
        else:
            big[shared_col] = small.combine_first(big[agg_func,shared_col])
        return