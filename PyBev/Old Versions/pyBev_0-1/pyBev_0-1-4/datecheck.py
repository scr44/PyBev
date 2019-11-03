#Date checking functions
import datetime as dtt

  
def date_from_str(datestring):
    """Turns a string into a datetime. Takes date string using the format
    'MM/DD/YYYY'. If given a default from a canceled input prompt, it carries
    it through."""
    
    if datestring == 'default':
        return 'default'
    else:
        return dtt.datetime.strptime(datestring,'%m/%d/%Y')

def valid_date_check(datestring):
    """If provided a date in the valid format MM/DD/YYYY, returns a datetime
    object. Otherwise, returns the string 'invalid'."""
    
    try:
        date = date_from_str(datestring)
    except ValueError:
        print('Unrecognized date format, please try again.\n')
        date = 'invalid'
    return date    

def date_input_checker(prompt):
    """Runs a validity check until it is convinced it has a usable datetime
    object, which it then returns."""
    
    while True:
        datestring = input(prompt) or 'default'
        date = valid_date_check(datestring)
        if (date == 'invalid'):
            continue
        else:
            break
    return date

def week_date_input():
    """Asks for the starting day of the week (Sunday) that you wish to compare
    against the MCAP data in Stage 1."""
    
    prompt = 'Input week start date (press enter to cancel): MM/DD/YYYY\n'
    week_date = date_input_checker(prompt)
    if week_date == 'default':
        print('Canceling date entry.')
        return 'No date entered.'
    else:
        return week_date
    
def check_before_input():
    """Asks for a cutoff date, defaulting to the date the program is being run.
    this will be used in Stage 2 to determine which columns to compare."""
    
    prompt = 'Input check cutoff date (press enter to use today): MM/DD/YYYY\n'
    check_before = date_input_checker(prompt)
    if check_before == 'default':
        return dtt.date.today()
    else:
        return check_before