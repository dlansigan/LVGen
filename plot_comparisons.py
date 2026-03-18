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
    parser.add_argument("--last_cycles", type=int, default=0, help="If defined, plot the last number of cycles.")
    parser.add_argument("--T_HB", type=float, default=100, help="Number of time points per cycle.")
    parser.add_argument("--calc_vol", action="store_true")
    parser.add_argument("--save_figs", action="store_true")
    args = parser.parse_args()

    cases = args.cases
    calc_LV_vol = args.calc_vol

    pscale = 1333.22

    # Plotting settings
    color_cycle = ["#377eb8", "#ff7f00", "#4daf4a","#f781bf",]
    line_cycle = ["-", "--", ":", "-."]
    plt.rc("axes", prop_cycle=(cycler("color", color_cycle) +
                            cycler("linestyle", line_cycle)))
    rcParams['text.usetex'] = True 

    fig1,ax1 = plt.subplots(2,2,tight_layout=True,figsize=(6,5))
    ax1 = ax1.flatten()
    fig2,ax2 = plt.subplots(2,2,tight_layout=True,figsize=(6,5))
    ax2 = ax2.flatten()

    for case in cases:
        # Read svZeroD
        fn = os.path.join(case,"svZeroD_data")
        sv0d = pd.read_csv(fn, sep=" ")
        # print(sv0d)
        t = sv0d["39"]
        tstart = -args.last_cycles*args.T_HB

        # Get pressures and volumes for LA, RV, RA from svZeroD sv0d
        p_LA = sv0d["pressure:LA:MV"]/pscale
        p_RV = sv0d["pressure:RV:PV"]/pscale
        p_RA = sv0d["pressure:RA:TV"]/pscale
        v_LA = sv0d["Vc:LA"]
        v_RV = sv0d["Vc:RV"]
        v_RA = sv0d["Vc:RA"]

        # Read boundary integrated pressure for LV
        fn = os.path.join(case,"4-procs","B_FS_Pressure_average.txt")
        p_LV = pd.read_csv(fn,sep=" ",skiprows=9)
        p_LV = p_LV["LV_wall"]/pscale # Convert dyn/cm^2 to mmHG

        # Compute volume for LV
        v_LV_fn = os.path.join(case,"LV_volume.npy")
        if not os.path.exists(v_LV_fn) or calc_LV_vol:
            results_path = os.path.join(case,"4-procs")
            files = natsort.natsorted(glob.glob(os.path.join(results_path,"result*.vtu")))
            v_LV = []
            for fn in files:
                mesh = pv.read(fn)
                mesh.set_active_vectors("Displacement")
                mesh = mesh.warp_by_vector()
                mesh = mesh.extract_surface(algorithm="geometry")
                v_LV.append(mesh.volume)
            v_LV = np.array(v_LV)
            np.save(v_LV_fn,v_LV)
        else:
            v_LV = np.load(v_LV_fn)

        print(v_LV[0], v_RV[0], v_LA[0], v_RA[0])
        print(np.max(v_LV),np.max(v_RV))

        # Plot PV curves
        chambers = {
            "RA": [p_RA, v_RA],
            "LA": [p_LA, v_LA],
            "RV": [p_RV, v_RV],
            "LV": [p_LV, v_LV],
        }

        for i,name in enumerate(chambers):
            ax1[i].plot(chambers[name][1][tstart:],chambers[name][0][tstart:],linewidth=2)
            ax1[i].set_title(name,fontsize=20)

        if case==cases[0]:
            ref = chambers
        else:
            for i,name in enumerate(chambers):
                ax2[i].plot(chambers[name][1][tstart:],
                            chambers[name][0][tstart:]-ref[name][0][tstart:],linewidth=2)
                ax2[i].set_title(name,fontsize=20)

    ax1[2].set_xlabel(r"$V$",fontsize=20)
    ax1[3].set_xlabel(r"$V$",fontsize=20)
    ax1[0].set_ylabel(r"$P$",fontsize=20)
    ax1[2].set_ylabel(r"$P$",fontsize=20)
    ax2[2].set_xlabel(r"$V$",fontsize=20)
    ax2[3].set_xlabel(r"$V$",fontsize=20)
    ax2[0].set_ylabel(r"$P$",fontsize=20)
    ax2[2].set_ylabel(r"$P$",fontsize=20)

    if args.save_figs:
        fig_path = "figs"
        case = os.path.basename(case)
        save_dir = os.path.join(fig_path,args.save_name)
        os.makedirs(save_dir,exist_ok=True)
        fig1.savefig(os.path.join(save_dir,"pv_comp.png"))
        fig2.savefig(os.path.join(save_dir,"pv_comp_err.png"))
    else:
        plt.show()
