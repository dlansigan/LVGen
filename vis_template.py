import numpy as np
import pyvista as pv
import argparse
import os

def set_mesh_camera(pl):
    pl.camera.azimuth=-0
    pl.camera.elevation=0
    pl.camera.roll=-60

if __name__=="__main__":

    fn = "template_meshes/LV.vtp"
    mesh = pv.read(fn)

    save_dir = os.path.join("figs","meshes")
    save_path = os.path.join(save_dir, "LV_template.eps")

    pl = pv.Plotter(window_size=(500,600))
    pl.add_mesh(mesh, color='lightblue',
                show_scalar_bar=False)
    
    set_mesh_camera(pl)
    pl.camera.zoom(1.45)
    pl.save_graphic(save_path)
    # pl.show()

    fns = [
        "scaled_meshes/mesh_0/phase0.vtp",
        "scaled_meshes/mesh_0/phase1.vtp",
        "scaled_meshes/mesh_0/phase9.vtp",
    ]

    for i,fn in enumerate(fns):
        mesh = pv.read(fn)
        save_path = os.path.join(save_dir, f"LV_surf_{i}.eps")

        pl = pv.Plotter(window_size=(500,600))
        pl.add_mesh(mesh, color='lightblue',
                    show_scalar_bar=False)
        
        set_mesh_camera(pl)
        pl.camera.zoom(1.45)
        pl.save_graphic(save_path)
