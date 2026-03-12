import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyvista as pv
import os
import glob
from cycler import cycler
import argparse

def get_var(df,var):
    return df.loc[df["name"]==var,"y"].to_numpy()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--case", type=str)
    parser.add_argument("--case_3d", type=str, default=None)
    parser.add_argument("--save_figs", action="store_true")
    args = parser.parse_args()

    case_path = args.case

    # Define params
    # tstart, tend = 0, 500
    tstart, tend = -500, -1
    save_path = os.path.join(case_path,"IC.dat")
    # Plotting settings
    color_cycle = ['#377eb8', '#ff7f00', '#4daf4a','#f781bf',]
    line_cycle = ['-', '--', ':', '-.']
    plt.rc('axes', prop_cycle=(cycler('color', color_cycle) +
                            cycler('linestyle', line_cycle)))

    # Read svZeroD
    fn = os.path.join(case_path,"output.csv")
    sv0d = pd.read_csv(fn)
    # print(sv0d)

    # Plot  circulation vs time
    t = sv0d["time"].unique()
    p_pul = [
             get_var(sv0d,"pressure:PV:ART_PUL"),
             get_var(sv0d,"pressure:ART_PUL:J1"),
             get_var(sv0d,"pressure:J1:VEN_PUL"),
             get_var(sv0d,"pressure:VEN_PUL:J0"),
            ]
    p_sys = [
             get_var(sv0d,"pressure:AV:ART_SYS"),
             get_var(sv0d,"pressure:ART_SYS:J3"),
             get_var(sv0d,"pressure:J3:VEN_SYS"),
             get_var(sv0d,"pressure:VEN_SYS:J2"),
            ]
    q_pul = [
             get_var(sv0d,"flow:PV:ART_PUL"),
             get_var(sv0d,"flow:ART_PUL:J1"),
             get_var(sv0d,"flow:J1:VEN_PUL"),
             get_var(sv0d,"flow:VEN_PUL:J0"),
            ]
    q_sys = [
             get_var(sv0d,"flow:AV:ART_SYS"),
             get_var(sv0d,"flow:ART_SYS:J3"),
             get_var(sv0d,"flow:J3:VEN_SYS"),
             get_var(sv0d,"flow:VEN_SYS:J2"),
            ]
    p_cha_left = [
             get_var(sv0d,"pressure:J0:LA"),
             get_var(sv0d,"pressure:LA:MV"),
             get_var(sv0d,"pressure:MV:LV"),
             get_var(sv0d,"pressure:LV:AV"),
            ]
    q_cha_left = [
             get_var(sv0d,"flow:J0:LA"),
             get_var(sv0d,"flow:LA:MV"),
             get_var(sv0d,"flow:MV:LV"),
             get_var(sv0d,"flow:LV:AV"),
            ]
    p_cha_right = [
             get_var(sv0d,"pressure:J2:RA"),
             get_var(sv0d,"pressure:RA:TV"),
             get_var(sv0d,"pressure:TV:RV"),
             get_var(sv0d,"pressure:RV:PV"),
            ]
    q_cha_right = [
             get_var(sv0d,"flow:J2:RA"),
             get_var(sv0d,"flow:RA:TV"),
             get_var(sv0d,"flow:TV:RV"),
             get_var(sv0d,"flow:RV:PV"),
            ]
    fig1,ax1=plt.subplots(4,2,figsize=(10,12))
    # Pulmonary/systemic
    for i in range(len(p_pul)):
        ax1[0,0].plot(t[tstart:tend],p_pul[i][tstart:tend])
        ax1[1,0].plot(t[tstart:tend],p_sys[i][tstart:tend])
        ax1[0,1].plot(t[tstart:tend],q_pul[i][tstart:tend])
        ax1[1,1].plot(t[tstart:tend],q_sys[i][tstart:tend])
    # Chambers
    for i in range(len(p_cha_left)):
        ax1[2,0].plot(t[tstart:tend],p_cha_left[i][tstart:tend])
        ax1[2,1].plot(t[tstart:tend],q_cha_left[i][tstart:tend])
        ax1[3,0].plot(t[tstart:tend],p_cha_right[i][tstart:tend])
        ax1[3,1].plot(t[tstart:tend],q_cha_right[i][tstart:tend])
    ax1[0,0].set_ylabel("Pulmonary")
    ax1[1,0].set_ylabel("Systemic")
    ax1[2,0].set_ylabel("Left Heart")
    ax1[3,0].set_ylabel("Right Heart")
    ax1[0,0].set_title("Pressure")
    ax1[0,1].set_title("Flow")
    ax1[-1,0].set_xlabel("Time")
    ax1[-1,1].set_xlabel("Time")

    # Get pressures and volumes for LA, RV, RA from svZeroD sv0d
    p_LA = get_var(sv0d,"pressure:LA:MV")
    p_LV = get_var(sv0d,"pressure:LV:AV")
    p_RV = get_var(sv0d,"pressure:RV:PV")
    p_RA = get_var(sv0d,"pressure:RA:TV")
    v_LV = get_var(sv0d,"Vc:LV")
    v_LA = get_var(sv0d,"Vc:LA")
    v_RV = get_var(sv0d,"Vc:RV")
    v_RA = get_var(sv0d,"Vc:RA")

    # Plot PV curves
    chambers = {
        "RA": [p_RA, v_RA],
        "LA": [p_LA, v_LA],
        "RV": [p_RV, v_RV],
        "LV": [p_LV, v_LV],
    }
    fig2,ax2 = plt.subplots(2,2,tight_layout=True)
    ax2 = ax2.flatten()
    for i,name in enumerate(chambers):
        ax2[i].plot(chambers[name][1][tstart:tend],chambers[name][0][tstart:tend])
        ax2[i].set_title(name)
    ax2[2].set_xlabel("V")
    ax2[3].set_xlabel("V")
    ax2[0].set_ylabel("P")
    ax2[2].set_ylabel("P")
    
    fig3,ax3 = plt.subplots(1,1,tight_layout=True)
    for i,name in enumerate(chambers):
        ax3.plot(t[tstart:tend],chambers[name][1][tstart:tend],label=name)
    ax3.set_xlabel("t")
    ax3.set_ylabel("v")
    ax3.legend()

    # Post-process valve resistances: (P_in-P_out)/Q_in
    R_MV = (get_var(sv0d,"pressure:LA:MV") - get_var(sv0d,"pressure:MV:LV")) / get_var(sv0d,"flow:LA:MV")
    R_AV = (get_var(sv0d,"pressure:LV:AV") - get_var(sv0d,"pressure:AV:ART_SYS")) / get_var(sv0d,"flow:LV:AV")
    R_TV = (get_var(sv0d,"pressure:RA:TV") - get_var(sv0d,"pressure:TV:RV")) / get_var(sv0d,"flow:RA:TV")
    R_PV = (get_var(sv0d,"pressure:RV:PV") - get_var(sv0d,"pressure:PV:ART_PUL")) / get_var(sv0d,"flow:RV:PV")
    fig4,ax4 = plt.subplots(4,1,tight_layout=True)
    ax4[0].plot(t[tstart:tend],R_MV[tstart:tend])
    ax4[1].plot(t[tstart:tend],R_AV[tstart:tend])
    ax4[2].plot(t[tstart:tend],R_TV[tstart:tend])
    ax4[3].plot(t[tstart:tend],R_PV[tstart:tend])

    # Write ICs for 3D-0D sim
    with open(save_path, 'w') as file:
        for name in sorted(sv0d["name"].unique()):
            if name == "Vc:LV":
                continue
            val = str(get_var(sv0d,name)[-1])
            name = name.replace("LV:","DUMMY_AV:")
            name = name.replace(":LV",":DUMMY_MV")
            file.write(f"\"{name}\": {val},\n")
    file.close()

    if args.case_3d:
        mesh_fn = os.path.join(args.case_3d,"mesh","mesh_complete.vtu")
        mesh = pv.read(mesh_fn)
        mesh.point_data['Pressure'] = get_var(sv0d,"pressure:LV:AV")[-1]*1333.22 # mmHg to dyn/cm^2
        # print(mesh['Pressure'])
        mesh.save(os.path.join(args.case_3d,"mesh","init_p.vtu"))

    if args.save_figs:
        fig1.savefig(os.path.join(case_path,"p_and_q.png"))
        fig2.savefig(os.path.join(case_path,"pv.png"))
        fig3.savefig(os.path.join(case_path,"v_vs_t.png"))
        fig4.savefig(os.path.join(case_path,"R.png"))
    else:
        plt.show()