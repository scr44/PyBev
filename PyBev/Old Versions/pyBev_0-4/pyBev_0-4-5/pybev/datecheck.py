"""Functions to turn user input dates into valid datetime objects."""


import datetime as dtt

  
def date_stripper(date):
    """Takes a given date or datetime object and strips out all information besides
    the day, month, and year, then returns as a datetime object. Can be used to
    turn dates into datetimes."""
    
    # the fact that there's no native dtt.date.to_datetime() method is just mind-
    # bogglingly dumb
    return dtt.datetime(
                year=date.year,
                month=date.month,
                day=date.day
                )

def date_from_str(datestring=None):
    """Turns a string into a datetime. Takes date string using the format
    'MM/DD/YYYY'. If given 'default' as the string, it will return today as a
    datetime."""
    
    if datestring is None:
        
        today_date = dtt.datetime.today()
        
        today_datetime = date_stripper(today_date)

        return today_datetime
    else:
        try:
            date = dtt.datetime.strptime(datestring,'%m/%d/%Y')
        except ValueError:
            print('Unrecognized date format, please try again.')
            date = None
        return date
    
def choose_week():
    """Asks for the week you wish to check. Using the default will return the
    current week. Accepts either a date in the format MM/DD/YYYY or an integer
    of a week difference (one week ago would be -1, for example)."""
    
    prompt = '''Input date to check.
Format as MM/DD/YYYY or negative integer of weeks ago:
(Defaults to current week)\n\n'''
    
    datestring = input(prompt) or None
    
    try: 
        
        weeksago = int(datestring)
        
        week_date = dtt.datetime.today() + (dtt.timedelta(days=7) * weeksago)
        
        week_date = date_stripper(week_date.date()) # strip out the hh:mm:ss data
        
    except (NameError,ValueError,TypeError):
            
        week_date = date_from_str(datestring)
        
        if week_date is None:
            
            return None
        
    if week_date.weekday() != 6: # if it's not a Sunday
        
        monday_difference = dtt.timedelta(days=week_date.weekday())
        
        # -1 since Monday == 0 for some reason
        week_date = (week_date - monday_difference - dtt.timedelta(days=1))
        
    if week_date > dtt.datetime.today():
        print('Warning: Future dates may not function correctly with other stages.')
    
    return week_date
    
def choose_cutoff():
    """Asks for a cutoff date for the comparison checking. Returns a datetime
    object."""
    
    prompt = '''Input comparison check cutoff date (MM/DD/YYYY):
(Defaults to current day)\n'''

    datestring = input(prompt) or None
    
    return date_from_str(datestring)