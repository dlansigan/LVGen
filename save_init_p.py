import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyvista as pv
import os
import argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--case", type=str, required=True)
    parser.add_argument("--init_p", type=float, required=True)
    args = parser.parse_args()

    mesh_fn = os.path.join(args.case,"mesh","mesh_complete.vtu")
    mesh = pv.read(mesh_fn)
    mesh.point_data['Pressure'] = args.init_p # dyn/cm^2
    mesh.save(os.path.join(args.case,"mesh","init_p.vtu"))

