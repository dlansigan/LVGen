import numpy as np
import os
import glob
import natsort

if __name__=="__main__":
    cases_dir = "cases"
    log_files = natsort.natsorted(glob.glob(os.path.join(cases_dir,"LV_*/*.log")))
    for log in log_files:
        with open(log, "r") as f:
            if "5000-3s" not in f.read():
                print(log)