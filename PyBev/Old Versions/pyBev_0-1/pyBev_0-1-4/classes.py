class MCAPData:
    """The MCAP Data object. Contains the equivalent of a spotfire pull as well
    as a pivot table counting the unique VIDs. Includes functions to pull data,
    extract it from csvs and xlsx docs to dataframes, and pivot it."""
    
    def __init__(self):
        self.mcap_path = 0 #this replaces sdpath
        self.mcap_df = 0 #this replaces sd
        self.mcap_pivot_df = 0 #used in indexcheck.mapping_loop()
    
    def extract():
        
        return mcap_df
    
class MetricsPanel:
    """The Metrics object. Contains the data from the given metrics worksheet.
    Includes functions to map data from MCAPData to the Spotfire Data column,
    write the data to the xlsx at bampath, and run a column comparison."""
    
    def __init__(self):
        self.metrics_path = 0 #this replaces bampath
        self.metrics_df = 0 #this replaces bam
        self.volatile_column = 0 #used in indexcheck.map_to_metrics
        
    def update_metrics():
        return