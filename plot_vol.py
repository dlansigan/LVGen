import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import natsort
import argparse
import pyvista as pv

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--case", type=str)
    parser.add_argument("--T_HB", type=float, default=0.8)
    parser.add_argument("--show_plot", action="store_true")
    args = parser.parse_args()

    case_path = args.case

    # Compute volume for LV
    v_LV_fn = os.path.join(case_path,"LV_volume.npy")
    
    results_path = os.path.join(case_path,"mesh","motion","Debug")
    files = natsort.natsorted(glob.glob(os.path.join(results_path,"*vtp")))
    v_LV = []
    for fn in files:
        mesh = pv.read(fn)
        v_LV.append(mesh.volume)
    v_LV = np.array(v_LV)
    np.save(v_LV_fn,v_LV)

    t = np.linspace(0,args.T_HB,len(v_LV))
    mask = np.arange(0,len(t),100)
    print(mask)

    if args.show_plot:
        plt.plot(t,v_LV)
        plt.scatter(t[mask],v_LV[mask])
        plt.show()