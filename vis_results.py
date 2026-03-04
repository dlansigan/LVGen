import numpy as np
import pyvista as pv
import os
import glob
from pygifsicle import optimize
import argparse
import natsort
import cmocean as cmo

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--case", type=str)
    args = parser.parse_args()

    case_path = args.case
    case_name = case_path.split('/')[-2]
    results_path = os.path.join(case_path,"4-procs")
    files = natsort.natsorted(glob.glob(os.path.join(results_path,"result*.vtu")))
    print("Case: " + case_name)

    os.makedirs("anim",exist_ok=True)

    pv.global_theme.cmap = cmo.cm.balance

    for i in range(0,len(files),1):
        fn = files[i]
        print(fn)
        # Read mesh
        mesh = pv.read(fn)

        # Warp
        mesh.set_active_scalars("Velocity")
        mesh.set_active_vectors("Displacement")
        mesh = mesh.warp_by_vector()
        mesh.set_active_vectors("Velocity")
        mesh2 = mesh.slice([1,1,1])
        
        # Set up streamlines
        radius = 0.02
        center = (0.58,0.47,0.38)
        seed = pv.Sphere(radius=radius, center=center, theta_resolution=50, phi_resolution=10) 
        streamlines = mesh.streamlines_from_source(
            seed,
            integration_direction="forward"
        )

        if i==0:
            pl = pv.Plotter()
            pl.open_gif(os.path.join("anim",case_name+".gif"),fps=60)
            pl.enable_parallel_projection()
        if i>0:
            pl.remove_actor(a1)
            pl.remove_actor(a2)
        a1 = pl.add_mesh(mesh,opacity=0.3,color='lightblue')
        # pl.add_mesh(src)
        # a2 = pl.add_mesh(streamlines.tube(radius=0.001),clim=(0.01,0.3))
        a2 = pl.add_mesh(mesh2,scalars="Velocity",component=1,opacity=0.5,clim=(-50,50),cmap='jet',show_scalar_bar=False)
        # a2 = pl.add_mesh(mesh2,scalars="Velocity",opacity=0.5,clim=(0,200),show_scalar_bar=False)
        pl.show_axes()
        pl.write_frame()
    # pl.show()
    pl.close()

    optimize(os.path.join("anim",case_name+".gif"))
