import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyvista as pv
import os
import glob
from cycler import cycler
import argparse
import natsort

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--case", type=str)
    parser.add_argument("--calc_vol", action="store_true")
    parser.add_argument("--save_ic", action="store_true")
    parser.add_argument("--save_figs", action="store_true")
    args = parser.parse_args()

    case_path = args.case
    calc_LV_vol = args.calc_vol

    pscale = 1333.22

    # Plotting settings
    color_cycle = ["#377eb8", "#ff7f00", "#4daf4a","#f781bf",]
    line_cycle = ["-", "--", ":", "-."]
    plt.rc("axes", prop_cycle=(cycler("color", color_cycle) +
                            cycler("linestyle", line_cycle)))

    # Read svZeroD
    fn = os.path.join(case_path,"svZeroD_data")
    sv0d = pd.read_csv(fn, sep=" ")
    # print(sv0d)

    # Plot  circulation vs time
    t = sv0d["39"]
    p_pul = [
             sv0d["pressure:PV:ART_PUL"]/pscale,
             sv0d["pressure:ART_PUL:J1"]/pscale,
             sv0d["pressure:J1:VEN_PUL"]/pscale,
             sv0d["pressure:VEN_PUL:J0"]/pscale
            ]
    p_sys = [
             sv0d["pressure:AV:ART_SYS"]/pscale,
             sv0d["pressure:ART_SYS:J3"]/pscale,
             sv0d["pressure:J3:VEN_SYS"]/pscale,
             sv0d["pressure:VEN_SYS:J2"]/pscale
            ]
    q_pul = [
             sv0d["flow:PV:ART_PUL"],
             sv0d["flow:ART_PUL:J1"],
             sv0d["flow:J1:VEN_PUL"],
             sv0d["flow:VEN_PUL:J0"]
            ]
    q_sys = [
             sv0d["flow:AV:ART_SYS"],
             sv0d["flow:ART_SYS:J3"],
             sv0d["flow:J3:VEN_SYS"],
             sv0d["flow:VEN_SYS:J2"]
            ]
    p_cha_left = [
             sv0d["pressure:J0:LA"]/pscale,
             sv0d["pressure:LA:MV"]/pscale,
             sv0d["pressure:MV:DUMMY_MV"]/pscale,
             sv0d["pressure:DUMMY_AV:AV"]/pscale
            ]
    q_cha_left = [
             sv0d["flow:J0:LA"],
             sv0d["flow:LA:MV"],
             sv0d["flow:MV:DUMMY_MV"],
             sv0d["flow:DUMMY_AV:AV"]
            ]
    p_cha_right = [
             sv0d["pressure:J2:RA"]/pscale,
             sv0d["pressure:RA:TV"]/pscale,
             sv0d["pressure:TV:RV"]/pscale,
             sv0d["pressure:RV:PV"]/pscale,
            ]
    q_cha_right = [
             sv0d["flow:J2:RA"],
             sv0d["flow:RA:TV"],
             sv0d["flow:TV:RV"],
             sv0d["flow:RV:PV"],
            ]
    fig1,ax1=plt.subplots(4,2,figsize=(10,12))
    # Pulmonary/systemic
    for i in range(len(p_pul)):
        ax1[0,0].plot(t,p_pul[i])
        ax1[1,0].plot(t,p_sys[i])
        ax1[0,1].plot(t,q_pul[i])
        ax1[1,1].plot(t,q_sys[i])
    # Chambers
    for i in range(len(p_cha_left)):
        ax1[2,0].plot(t,p_cha_left[i])
        ax1[2,1].plot(t,q_cha_left[i])
        ax1[3,0].plot(t,p_cha_right[i])
        ax1[3,1].plot(t,q_cha_right[i])
    ax1[0,0].set_ylabel("Pulmonary")
    ax1[1,0].set_ylabel("Systemic")
    # ax1[1,1].set_ylim([-10,420])
    ax1[2,0].set_ylabel("Left Heart")
    # ax1[2,0].set_ylim([-10,120])
    ax1[3,0].set_ylabel("Right Heart")
    ax1[0,0].set_title("Pressure")
    ax1[0,1].set_title("Flow")
    ax1[-1,0].set_xlabel("Time")
    ax1[-1,1].set_xlabel("Time")

    # Get pressures and volumes for LA, RV, RA from svZeroD sv0d
    p_LA = sv0d["pressure:LA:MV"]/pscale
    p_RV = sv0d["pressure:RV:PV"]/pscale
    # p_LV = sv0d["pressure:DUMMY_AV:AV"]/pscale
    p_RA = sv0d["pressure:RA:TV"]/pscale
    v_LA = sv0d["Vc:LA"]
    v_RV = sv0d["Vc:RV"]
    v_RA = sv0d["Vc:RA"]

    # Read boundary integrated pressure for LV
    fn = os.path.join(case_path,"4-procs","B_FS_Pressure_average.txt")
    p_LV = pd.read_csv(fn,sep=" ",skiprows=9)
    p_LV = p_LV["LV_wall"]/pscale # Convert dyn/cm^2 to mmHG

    # Compute volume for LV
    v_LV_fn = os.path.join(case_path,"LV_volume.npy")
    if not os.path.exists(v_LV_fn) or calc_LV_vol:
        results_path = os.path.join(case_path,"4-procs")
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
    fig2,ax2 = plt.subplots(2,2,tight_layout=True)
    ax2 = ax2.flatten()
    for i,name in enumerate(chambers):
        ax2[i].plot(chambers[name][1],chambers[name][0])
        ax2[i].set_title(name)
        if name=="LV":
            ax2[i].set_ylim([0,150])
    ax2[2].set_xlabel("V")
    ax2[3].set_xlabel("V")
    ax2[0].set_ylabel("P")
    ax2[2].set_ylabel("P")
    
    fig3,ax3 = plt.subplots(1,1,tight_layout=True)
    # tot_vol = 0
    for i,name in enumerate(chambers):
        ax3.plot(t,chambers[name][1],label=name)
        # tot_vol+=chambers[name][1]
    # ax3.plot(t,tot_vol)
    ax3.set_xlabel("t")
    ax3.set_ylabel("v")
    ax3.legend()

    if args.save_ic:
        p0 = []
        q0 = []
        v0 = []
        with open(os.path.join(case_path,"IC.dat"), 'w') as file:
            for name in sv0d:
                if "pressure" in name:
                    p0.append([name,sv0d[name].iloc[-1]])
                elif "flow" in name:
                    q0.append([name,sv0d[name].iloc[-1]])
                elif "Vc" in name:
                    v0.append([name,sv0d[name].iloc[-1]])
            for pair in p0:
                file.write(f"\"{pair[0]}\": {pair[1]},\n")
            for pair in q0:
                file.write(f"\"{pair[0]}\": {pair[1]},\n")
            for pair in v0:
                file.write(f"\"{pair[0]}\": {pair[1]},\n")

    # Post-process valve resistances: (P_in-P_out)/Q_in
    R_MV = (sv0d["pressure:LA:MV"] - sv0d["pressure:MV:DUMMY_MV"])/pscale / sv0d["flow:LA:MV"]
    R_AV = (sv0d["pressure:DUMMY_AV:AV"] - sv0d["pressure:AV:ART_SYS"])/pscale / sv0d["flow:DUMMY_AV:AV"]
    R_TV = (sv0d["pressure:RA:TV"] - sv0d["pressure:TV:RV"])/pscale / sv0d["flow:RA:TV"]
    R_PV = (sv0d["pressure:RV:PV"] - sv0d["pressure:PV:ART_PUL"])/pscale / sv0d["flow:RV:PV"]
    fig4,ax4 = plt.subplots(4,1,tight_layout=True)
    ax4[0].plot(t,R_MV)
    ax4[0].set_ylabel("MV")
    ax4[1].plot(t,R_AV)
    ax4[1].set_ylabel("AV")
    ax4[2].plot(t,R_TV)
    ax4[2].set_ylabel("TV")
    ax4[3].plot(t,R_PV)
    ax4[3].set_ylabel("PV")

    fig5,ax5 = plt.subplots(2,2)
    # ax5[0].plot(t,sv0d["pressure:MV:DUMMY_MV"])
    # ax5[0].plot(t,sv0d["pressure:DUMMY_MV:LPN_outlet"])
    # ax5[0].plot(t,sv0d["pressure:LPN_inlet:DUMMY_AV"])
    # ax5[0].plot(t,sv0d["pressure:DUMMY_AV:AV"])
    # ax5[1].plot(t,sv0d["flow:MV:DUMMY_MV"])
    # ax5[1].plot(t,sv0d["flow:DUMMY_MV:LPN_outlet"])
    # ax5[1].plot(t,sv0d["flow:LPN_inlet:DUMMY_AV"])
    # ax5[1].plot(t,sv0d["flow:DUMMY_AV:AV"])

    ax5[0][0].plot(t,sv0d["pressure:DUMMY_AV:AV"]/pscale,label="P_in")
    ax5[0][0].plot(t,sv0d["pressure:AV:ART_SYS"]/pscale,label="P_out")
    ax5[1][0].plot(t,sv0d["flow:DUMMY_AV:AV"],label="Q_in")
    ax5[1][0].plot(t,sv0d["flow:AV:ART_SYS"],label="Q_out")
    ax5[0][0].set_title("AV")
    ax5[0][1].plot(t,sv0d["pressure:LA:MV"]/pscale,label="P_in")
    ax5[0][1].plot(t,sv0d["pressure:MV:DUMMY_MV"]/pscale,label="P_out")
    ax5[1][1].plot(t,sv0d["flow:LA:MV"],label="Q_in")
    ax5[1][1].plot(t,sv0d["flow:MV:DUMMY_MV"],label="Q_out")
    ax5[0][1].set_title("MV")
    ax5[0][0].set_ylabel("P")
    ax5[1][0].set_ylabel("Q")
    ax5[0][0].legend()
    ax5[1][0].legend()

    fig6,ax6 = plt.subplots(2,1)
    ax6[0].plot(t,sv0d["pressure:LPN_inlet:DUMMY_AV"],label="inlet")
    ax6[0].plot(t,sv0d["pressure:DUMMY_MV:LPN_outlet"],label="outlet")
    ax6[0].set_ylabel("p")
    ax6[1].plot(t,sv0d["flow:LPN_inlet:DUMMY_AV"],label="inlet")
    ax6[1].plot(t,sv0d["flow:DUMMY_MV:LPN_outlet"],label="outlet")
    ax6[1].set_ylabel("q")
    ax6[1].legend()

    if args.save_figs:
        fig1.savefig(os.path.join(case_path,"p_and_q.png"))
        fig2.savefig(os.path.join(case_path,"pv.png"))
        fig3.savefig(os.path.join(case_path,"v_vs_t.png"))
        fig4.savefig(os.path.join(case_path,"R.png"))
        fig5.savefig(os.path.join(case_path,"p_valves.png"))
    else:
        plt.show()
