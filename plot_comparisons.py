import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pyvista as pv
import os
import glob
from cycler import cycler
import argparse
import natsort

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--cases", type=str, nargs="+")
    parser.add_argument("--save_name", type=str)
    # parser.add_argument("--last_cycles", type=int, default=0, help="If defined, plot the last number of cycles.")
    # parser.add_argument("--T_HB", type=float, default=1000, help="Number of time points per cycle.")
    parser.add_argument("--save_figs", action="store_true")
    args = parser.parse_args()

    cases = args.cases

    pscale = 1333.22

    # Plotting settings
    color_cycle = ["#377eb8", "#ff7f00", "#4daf4a","#f781bf",]
    line_cycle = ["-", "--", ":", "-."]
    plt.rc("axes", prop_cycle=(cycler("color", color_cycle) +
                            cycler("linestyle", line_cycle)))
    rcParams['text.usetex'] = True 

    fig1,ax1 = plt.subplots(2,2,tight_layout=True,figsize=(6,5))
    ax1 = ax1.flatten()

    for case in cases:

        # Plot PV curves
        chambers = ["RA","LA","RV","LV"]

        for i,name in enumerate(chambers):
            p = np.load(os.path.join(case,"{}_p.npy".format(name)))
            v = np.load(os.path.join(case,"{}_v.npy".format(name)))
            ax1[i].plot(v,p,linewidth=2)
            ax1[i].set_title(name,fontsize=20)

    ax1[2].set_xlabel(r"$V$",fontsize=20)
    ax1[3].set_xlabel(r"$V$",fontsize=20)
    ax1[0].set_ylabel(r"$P$",fontsize=20)
    ax1[2].set_ylabel(r"$P$",fontsize=20)

    if args.save_figs:
        fig_path = "figs"
        case = os.path.basename(case)
        save_dir = os.path.join(fig_path,args.save_name)
        os.makedirs(save_dir,exist_ok=True)
        fig1.savefig(os.path.join(save_dir,"pv_comp.png"))
    else:
        plt.show()
