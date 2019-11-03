class class1:
    """This is the class description."""
    sample_var = 1
    sample_str = 'Hello, world!'
    
    def f(self):
        return 'Hi, world!'

        
class MCAPData:
    """The MCAP Data object. Contains the equivalent of a spotfire pull as well
    as a pivot table counting the unique VIDs. Includes functions to pull data,
    extract it from csvs and xlsx docs to dataframes, and pivot it.
    """
    MCAP_path = 0 #this replaces sdpath
    df = 0 #this replaces sd
    pt = 0
    
    
class MetricsPanel:
    """The Metrics object. Contains the data from the given metrics worksheet.
    Includes functions to map data from MCAPData to the Spotfire Data column,
    write the data to the xlsx at bampath, and run a column comparison.
    """
    metrics_path = 0 #this replaces bampath
    df = 0 #this replaces bam
    week = 0
    book = 0
    
def valid_date_check(arg):
    switch = False
    return arg, switch
    
def valid_index_check(arg):
    switch = False
    return arg, switch