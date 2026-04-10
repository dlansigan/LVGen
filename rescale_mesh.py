import numpy as np
import pyvista as pv
import os
import vtk
import glob
import argparse
import sys
sys.path.append("interp-src")
import utils
from io_utils import write_vtk_polydata, write_vtu_file
import pickle

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--template_dir", type=str, required=True)
    parser.add_argument("--save_dir", type=str, required=True)
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--n_meshes", type=int, default=1)
    parser.add_argument("--scale", type=float, default=None)
    parser.add_argument("--target_vol", type=float, default=None)
    parser.add_argument("--phase", type=int, default=0)
    args = parser.parse_args()

    template_dir = args.template_dir
    save_dir = args.save_dir
    scale = args.scale
    target_vol = args.target_vol
    if scale and target_vol:
        raise ValueError("Cannot use both scale and target volume. Please choose one.")
    os.makedirs(save_dir,exist_ok=True)

    scales = []
    for n in range(args.n_meshes):
        mesh_dir = "mesh_{}".format(str(n))
        os.makedirs(os.path.join(save_dir,mesh_dir),exist_ok=True)
        files = sorted(glob.glob(os.path.join(template_dir, mesh_dir, "*.vtp")))
        # print(template_dir,mesh_dir, files)
        # Get reference phase volume
        if target_vol:
            fn = files[args.phase]
            mesh = pv.read(fn)
            ref_vol = mesh.volume
        for fn in files:
            mesh = pv.read(fn)
            if target_vol:
                scale=(target_vol/ref_vol)**(1/3)
            scales.append(scale)
            mesh.points*=scale
            new_fn, _ = os.path.splitext(os.path.basename(fn))
            # mesh.save(os.path.join(save_dir,mesh_dir,new_fn+".vtu")) # Volume mesh
            mesh.save(os.path.join(save_dir,mesh_dir,new_fn+".vtp")) # Surface mesh
            # print("%s -> %s" % (fn,os.path.join(save_dir,mesh_dir,new_fn+".vtp")))
            if fn==files[9]:
                print(mesh.volume)

    with open(os.path.join(save_dir,"scales.pkl"), "wb") as f:
        pickle.dump(scales, f)

    # # Compare meshes
    # fn_gen = os.path.join(save_dir,"mesh_0","phase0.vtp")
    # mesh_gen = pv.read(fn_gen)
    # fn_pat = "../HealthyPatientTest/HealthyPatientTest/lv_ris/biv-mesh-complete/walls_combined.vtp"
    # mesh_pat = pv.read(fn_pat)
    # # print(mesh_gen)
    # # print(mesh_pat)
    # print(mesh_gen.volume,mesh_pat.volume)
    # if args.vis:
    #     pl = pv.Plotter(shape=(1,2))
    #     pl.subplot(0,0)
    #     pl.add_mesh(mesh_gen)
    #     pl.subplot(0,1)
    #     pl.add_mesh(mesh_pat)
    #     pl.show()