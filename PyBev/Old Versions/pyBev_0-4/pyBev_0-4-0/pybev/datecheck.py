"""Functions to turn user input dates into valid datetime objects."""


import datetime as dtt

  
def date_from_str(datestring):
    """Turns a string into a datetime. Takes date string using the format
    'MM/DD/YYYY'. If given 'default' as the string, it will return today as a
    datetime."""
    
    if datestring == 'default':
        # the fact that there's no dtt.date.to_datetime() method is just mind-
        # bogglingly dumb
        today_date = dtt.datetime.today()
        
        today_datetime = dtt.datetime(
                                    year=today_date.year,
                                    month=today_date.month,
                                    day=today_date.day
                                    )

        return today_datetime
    else:
        return dtt.datetime.strptime(datestring,'%m/%d/%Y')

def valid_date_check(datestring):
    """If provided a date in the valid format MM/DD/YYYY, returns a datetime
    object. Otherwise, returns the string 'invalid'."""
    
    try:
        date = date_from_str(datestring)
    except ValueError:
        print('Unrecognized date format, please try again.')
        date = 'invalid'
    return date    

def date_input_checker(prompt):
    """Runs a validity check until it is convinced it has a usable datetime
    object, which it then returns."""
    
    date = valid_date_check('default')
    while True:
        datestring = input(prompt) or 'default'
        if datestring == 'end' or datestring == 'End':
            end = 1
            return date, end
        else:
            date = valid_date_check(datestring)
            if (date == 'invalid'):
                continue
            else:
                end = 0
                return date, end
    

def week_date_input():
    """Asks for the week you wish to check. Using the default will return the
    current week."""
    
    prompt = 'Input the week to check (Press enter to use the current week): MM/DD/YYYY\n'
    week_date, end = date_input_checker(prompt)
    
    if week_date.weekday() != 6: # if it's not a sunday
        monday_difference = dtt.timedelta(days=week_date.weekday())
        
        # -1 since dtt starts at monday for some reason
        week_date = (week_date - monday_difference - dtt.timedelta(days=1))
    
    return week_date, end
    
def check_before_input():
    """Asks for a cutoff date, defaulting to the date the program is being run.
    this will be used in Stage 2 to determine which columns to compare."""
    
    prompt = 'Input check cutoff date (press enter to use today\'s date): MM/DD/YYYY\n'
    check_before, end = date_input_checker(prompt)
    return check_before
        
# def comparison_date_input():
#     """Asks for the starting day of the week (Sunday) that you wish to compare
#     against the MCAP data in Stage 2."""
#     
#     prompt = 'Input week to inspect (press enter to cancel): MM/DD/YYYY\n'
#     comparison_date = date_input_checker(prompt)
#     if comparison_date == 'default':
#         print('Canceling date entry.')
#         return 'No date entered.'
#     else:
#         return comparison_date