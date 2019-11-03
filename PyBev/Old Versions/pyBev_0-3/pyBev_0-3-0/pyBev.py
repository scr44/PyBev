import os
import sys
import pybev as pb

# os.chdir(os.path.dirname(sys.argv[0])) # go to the pyBeverage.py file directory

metrics = pb.stage_select()

pb.monday_archive(metrics)