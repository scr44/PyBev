import os
import sys
import pybev as pb

# os.chdir(os.path.dirname(sys.argv[0])) # go to the pyBeverage.py file directory
# test account for executables un/pw: pybev/Sys!admin1

mcap, metrics, report = pb.run_main_program()

try: metrics.wipe_volatile_data()
except AttributeError: print('')