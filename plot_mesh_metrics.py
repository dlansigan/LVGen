import numpy as np
import os
import pyvista as pv
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import glob

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_cases", type=int, required=True)
    args = parser.parse_args()

    data = []
    bad_list = []

    for i in range(args.n_cases):
        fn = "cases/LV_{}/mesh/mesh_complete.vtu".format(i)
        mesh = pv.read(fn)

        ar_max = np.max(mesh["aspect_ratio"])
        ar_mean = np.mean(mesh["aspect_ratio"])
        len_min = np.max(mesh["volume"]**(1/3))
        len_mean = np.mean(mesh["volume"]**(1/3))

        if ar_max > 50:
            bad_list.append(i)

        data.append([i,ar_max,ar_mean,len_min,len_mean])

    df = pd.DataFrame(data,columns=["Case","AR_max","AR_mean","edge_length_min","edge_length_mean"])
    print(df)

    df.plot.bar(x="Case", y=["AR_max","AR_mean","edge_length_min","edge_length_mean"],
                 subplots=True,
                 layout=(2, 2),
                 figsize=(6, 6))
    plt.tight_layout()
    plt.show()

    print(bad_list)
