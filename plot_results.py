import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyvista as pv
import os
import glob
from cycler import cycler

if __name__=="__main__":

    case_path = "cases/LV_regazzoni"
    calc_LV_vol = False

    # Plotting settings
    color_cycle = ['#377eb8', '#ff7f00', '#4daf4a','#f781bf',]
    line_cycle = ['-', '--', ':', '-.']
    plt.rc('axes', prop_cycle=(cycler('color', color_cycle) +
                            cycler('linestyle', line_cycle)))

    # Read svZeroD
    fn = os.path.join(case_path,"svZeroD_data")
    sv0d = pd.read_csv(fn, sep=" ")
    # print(sv0d)

    # Plot  circulation vs time
    t = sv0d["39"]
    p_pul = [
             sv0d["pressure:PV:ART_PUL"],
             sv0d["pressure:ART_PUL:J1"],
             sv0d["pressure:J1:VEN_PUL"],
             sv0d["pressure:VEN_PUL:J0"]
            ]
    p_sys = [
             sv0d["pressure:AV:ART_SYS"],
             sv0d["pressure:ART_SYS:J3"],
             sv0d["pressure:J3:VEN_SYS"],
             sv0d["pressure:VEN_SYS:J2"]
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
             sv0d["pressure:J0:LA"],
             sv0d["pressure:LA:MV"],
             sv0d["pressure:MV:DUMMY_MV"],
             sv0d["pressure:DUMMY_AV:AV"]
            ]
    q_cha_left = [
             sv0d["flow:J0:LA"],
             sv0d["flow:LA:MV"],
             sv0d["flow:MV:DUMMY_MV"],
             sv0d["flow:DUMMY_AV:AV"]
            ]
    p_cha_right = [
             sv0d["pressure:J2:RA"],
             sv0d["pressure:RA:TV"],
             sv0d["pressure:TV:RV"],
             sv0d["pressure:RV:PV"],
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
    ax1[2,0].set_ylabel("Left Heart")
    ax1[3,0].set_ylabel("Right Heart")
    ax1[0,0].set_title("Pressure")
    ax1[0,1].set_title("Flow")
    ax1[-1,0].set_xlabel("Time")
    ax1[-1,1].set_xlabel("Time")

    # Get pressures and volumes for LA, RV, RA from svZeroD sv0d
    p_LA = sv0d["pressure:LA:MV"]
    p_RV = sv0d["pressure:RV:PV"]
    p_RA = sv0d["pressure:RA:TV"]
    v_LA = sv0d["Vc:LA"]
    v_RV = sv0d["Vc:RV"]
    v_RA = sv0d["Vc:RA"]

    # Read boundary integrated pressure for LV
    fn = os.path.join(case_path,"4-procs","B_FS_Pressure_average.txt")
    p_LV = pd.read_csv(fn,sep=" ",skiprows=9)
    p_LV = p_LV["LV_wall"]

    # Compute volume for LV
    v_LV_fn = os.path.join(case_path,"LV_volume.npy")
    if not os.path.exists(v_LV_fn) or calc_LV_vol:
        results_path = os.path.join(case_path,"4-procs")
        files = sorted(glob.glob(os.path.join(results_path,"result*.vtu")))
        v_LV = []
        for fn in files:
            mesh = pv.read(fn)
            mesh.set_active_vectors("Displacement")
            mesh = mesh.warp_by_vector()
            mesh = mesh.extract_surface(algorithm='geometry')
            v_LV.append(mesh.volume)
        v_LV = np.array(v_LV)
        np.save(v_LV_fn,v_LV)
    else:
        v_LV = np.load(v_LV_fn)

    print(np.max(v_LV),np.max(v_RV))

    # Plot PV curves
    chambers = {
        "LA": [p_LA, v_LA],
        "RA": [p_RA, v_RA],
        # "LV": [p_LV, v_LV],
        "RV": [p_RV, v_RV],
    }
    fig2,ax2 = plt.subplots(2,2,tight_layout=True)
    ax2 = ax2.flatten()
    for i,name in enumerate(chambers):
        ax2[i].plot(chambers[name][1],chambers[name][0])
        ax2[i].set_title(name)
    ax2[2].set_xlabel("V")
    ax2[3].set_xlabel("V")
    ax2[0].set_ylabel("P")
    ax2[2].set_ylabel("P")
    
    fig3,ax3 = plt.subplots(1,1,tight_layout=True)
    for i,name in enumerate(chambers):
        ax3.plot(t,chambers[name][1],label=name)
    ax3.set_xlabel("t")
    ax3.set_ylabel("v")
    ax3.legend()

    plt.show()
