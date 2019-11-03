import os
import sys
import pybev as pb

# os.chdir(os.path.dirname(sys.argv[0])) # go to the pyBeverage.py file directory

mcap, metrics, report = pb.run_main_program()

metrics.wipe_volatile_data()