import cleanerMeasureLight as CSLA
import numpy as np

measuredData = CSLA.MeasuredData()

ran = CSLA.Capture()

arry2 = [7, 8, 9, 10, 11, 12]

results = measuredData.get()

print(results)