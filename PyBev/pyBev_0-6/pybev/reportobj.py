"""Reporting functions of the program are currently inactive, as a full manual
review of the material each day is required anyway. If there's time this may
eventually be expanded to produce a report as shown below, but it seems
unnecessary as all the information is already available in the metrics docs."""

class Ticket:
    """A troubleshooting ticket that will be printed out with the report in
    stage 5. Contains all automatable information about a given issue, including
    relevant troubleshooting attempts and suggested actions."""
    
    def __init__(self,mcap,metrics,RetMkt,status):
        # Metrics details
        self.RetMkt = RetMkt
        self.retailer = mcap.df.loc[RetMkt]['Retailer'].values[-1]
        self.market = mcap.df.loc[RetMkt]['Market'].values[-1]
        self.status = status
        self.exp_date = metrics.df.loc[RetMkt]['Exp. Date']
        self.sender = mcap.df.loc[RetMkt]['Sender'].values[-1]
        self.media = metrics.df.loc[RetMkt]['Media']
        self.ret_website = metrics.df.loc[RetMkt]['Website Link']
        
        # Ticket ID
        self.RU = None
        self.media_abbv = None
        self.tick_name = None
        self.tick_num = None
        self.tick_ID = None
        self.abbv_func()
        self.name_gen()
        
        # Duplicate Information
        self.original_ad_count = None
        self.revised_ad_count = None
        
        # MCAP Information
        self.ads_present = None
        self.ads_expected = None
        self.days_overdue = None
        self.VID_status_count = {}
        self.VID_list = {}
        self.last_package_dt = None
        self.last_package_EID = None
        
        # AC Information
        self.AC_Retailer = None
        self.AC_Market = None
        self.storeID = None
        self.last_scrape_dt = None
        self.circular_status = None
        self.last_scrape_path = None
        
        # Issue Information
        self.known_issue = metrics.df.loc[RetMkt]['Issue']
        self.recommended_action = None
        self.descrip = None
        
    def abbv_func(self):
        media = self.media
        
        if media == r'Client-1':
            self.media_abbv = 'P1C'
        elif media == r'Client-2':
            self.media_abbv = 'P2C'
        elif media == r'Scrape-1':
            self.media_abbv = 'P1S'
        elif media == r'Scrape-2':
            self.media_abbv = 'P2S'
        elif media == r'Insert/Paper':
            self.media_abbv = 'IP'
        elif media == r'JA DL':
            self.media_abbv = 'JADL'
        else:
            self.media_abbv == 'UKWN'
            print('\t %s has unknown media type.' % self.RetMkt)
        return
            
    def name_gen(self):
        self.tick_name = '%s - %s - %s' % (
            self.retailer,
            self.market,
            self.exp_date.strftime('%m/%d/%Y')
            )
    
    def ID_gen(self):
        self.tick_ID = '%s-%s-%d' % (
            self.RU,
            self.media_abbv,
            self.tick_num
            )
        
class Report:
    """Turns information from given tickets into a formatted, human-readable
    report and outputs it in a txt file.
    
    Currently non-functional.
    """
    
    def __init__(self,mcap,metrics):
        self.panel = mcap.panel
        self.rundate = dtt.datetime.today()
        self.duplicate_count = 0
        self.resolved_count = 0
        self.unresolved_count = 0
        self.ticket_list = {}
        self.header = None
        self.contents_dupe = {}
        self.contents_unres = {}
        self.contents_res = {}
        self.detail_view = None
        
    def mk_header(self):
        self.header = """
pyBev Metrics Report
Panel: %s
Scan initiated: %s
Items resolved: %d
Items unresolved: %d
""" % (self.panel, dtt.datetime.today().strftime('%m/%d/%Y %x'), self.resolved_count,
self.unresolved_count)
        return
    
    def mk_TOC(self):
        for i in range(0,len(self.ticket_list)):
            # do something
            x = 1
        return
        
    def mk_detail_view(self):
        return
        
    def write_to_file(self):
        return