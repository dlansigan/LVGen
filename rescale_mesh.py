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

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--template_dir", type=str, required=True)
    parser.add_argument("--save_dir", type=str, required=True)
    parser.add_argument("--vis", action="store_true")
    parser.add_argument("--n_meshes", type=int, default=1)
    parser.add_argument("--scale", type=float, default=27)
    args = parser.parse_args()

    template_dir = args.template_dir
    save_dir = args.save_dir
    scale = args.scale
    os.makedirs(save_dir,exist_ok=True)

    for n in range(args.n_meshes):
        mesh_dir = "mesh_{}".format(str(n))
        os.makedirs(os.path.join(save_dir,mesh_dir),exist_ok=True)
        files = glob.glob(os.path.join(template_dir, mesh_dir, "*.vtp"))
        for fn in files:
            mesh = pv.read(fn)
            mesh.points*=scale
            mesh.save(os.path.join(save_dir,mesh_dir,os.path.basename(fn)))

    # Compare meshes
    fn_gen = os.path.join(save_dir,"mesh_0_less_motion","phase0.vtp")
    mesh_gen = pv.read(fn_gen)
    fn_pat = "../HealthyPatientTest/HealthyPatientTest/lv_ris/biv-mesh-complete/walls_combined.vtp"
    mesh_pat = pv.read(fn_pat)
    # print(mesh_gen)
    # print(mesh_pat)
    print(mesh_gen.volume,mesh_pat.volume)
    if args.vis:
        pl = pv.Plotter(shape=(1,2))
        pl.subplot(0,0)
        pl.add_mesh(mesh_gen)
        pl.subplot(0,1)
        pl.add_mesh(mesh_pat)
        pl.show()