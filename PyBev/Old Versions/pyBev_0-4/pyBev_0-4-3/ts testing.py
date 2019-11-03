import pybev as pb
import datetime as dtt
from pybev import colcomp as cc
from pybev import troubleshooting as ts
from pybev import metricsobj as mo

mcap, metrics = pb.stage_one()

metrics.week_date = dtt.datetime(2017,7,23)

metrics.cutoff_date = dtt.datetime(2017,8,1)

report = mo.Report(mcap,metrics)

metrics.book.save()

metrics.extract()

