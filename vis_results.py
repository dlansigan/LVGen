import numpy as np
import pyvista as pv
import os
import glob
from pygifsicle import optimize
import argparse
import natsort
import cmocean as cmo

def create_plotter(gif_path):
    pl = pv.Plotter(window_size=(600,750),off_screen=True)
    pl.open_gif(gif_path,fps=15)
    pl.enable_parallel_projection()
    return pl

def refresh_plotter(pl,meshes,mesh_props,title):
    for actor in pl.actors:
        pl.remove_actor(actor)
    for mesh, props in zip(meshes,mesh_props):
        pl.add_volume(mesh,**props)
    pl.camera.focal_point = mesh.center
    pl.camera.roll = -60
    # pl.camera.elevation = 15
    pl.show_axes()
    pl.add_text(title,position="upper_edge")
    pl.write_frame()

    return pl


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--case", type=str)
    parser.add_argument("--dt", type=float, default=0.008)
    parser.add_argument("--last_cycles", type=int, default=-1, help="If defined, plot the last number of cycles.")
    parser.add_argument("--T_HB", type=int, default=100, help="Number of time points per cycle.")
    parser.add_argument("--save_frames", type=int, nargs="+", help="List frames to save.")
    parser.add_argument("--frame_skip", type=int, default=1, help="Number of frames to skip in animation.")
    args = parser.parse_args()

    if args.save_frames:
        save_frames = [frame-1 for frame in args.save_frames]
    else:
        save_frames = []
    case_path = args.case
    temp = case_path.split('/')
    temp = [item for item in temp if item != '']
    case_name = temp[-1]
    results_path = os.path.join(case_path,"4-procs")
    files = natsort.natsorted(glob.glob(os.path.join(results_path,"result*.vtu")))
    print("Case: " + case_name)

    os.makedirs("anim",exist_ok=True)
    os.makedirs(os.path.join("anim",case_name),exist_ok=True)

    pv.global_theme.cmap = cmo.cm.balance

    if args.last_cycles==-1:
        tstart=0
    else:
        tstart = len(files)-args.last_cycles*args.T_HB-1

    # tstart = len(files)-21
    for i in range(tstart,len(files),args.frame_skip):
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

        # Make mesh into volume
        grid = pv.create_grid(mesh, dimensions=(128,128,128))
        mesh = grid.sample(mesh)
        mesh["magU"] = np.linalg.norm(mesh["Velocity"], axis=1)
        mesh["u"] = mesh["Velocity"][:,0]
        mesh["v"] = mesh["Velocity"][:,1]
        mesh["w"] = mesh["Velocity"][:,2]
        
        # # Set up streamlines
        # radius = 0.02
        # center = (0.58,0.47,0.38)
        # seed = pv.Sphere(radius=radius, center=center, theta_resolution=50, phi_resolution=10) 
        # streamlines = mesh.streamlines_from_source(
        #     seed,
        #     integration_direction="forward"
        # )

        if i==tstart:
            pl = create_plotter(os.path.join("anim",case_name,"vel.gif"))
            pl1 = create_plotter(os.path.join("anim",case_name,"vel_y.gif"))
            pl2 = create_plotter(os.path.join("anim",case_name,"vel_z.gif"))

        mesh_props = [
            {"scalars": "magU", "clim": (0,50), "opacity_unit_distance":0.5}
        ]
        refresh_plotter(pl,[mesh],mesh_props,"t={:.2f}".format((i*args.dt)))
        
        mesh_props = [
            {"scalars": "v", "clim": (-50,50), "opacity_unit_distance":0.5}
        ]
        refresh_plotter(pl1,[mesh],mesh_props,"t={:.2f}".format((i*args.dt)))
                
        mesh_props = [
            {"scalars": "w", "clim": (-50,50), "opacity_unit_distance":0.5}
        ]
        refresh_plotter(pl2,[mesh],mesh_props,"t={:.2f}".format((i*args.dt)))
        
        # mesh_props = [
        #     {"opacity": 0.3, "color": "lightblue", "clim": (0.01,0.3)},
        #     {"scalars": "Velocity", "opacity": 0.5, "component": 2, "clim": (-50,50), "show_scalar_bar": False}
        # ]
        # refresh_plotter(pl2,[mesh,mesh2],mesh_props,"t={:.2f}".format((i*args.dt)))

        if i in save_frames:
            pl.screenshot(os.path.join("anim",case_name,"frame_{}.png".format(i+1)))

    pl.close()
    pl1.close()
    pl2.close()

    # optimize(os.path.join("anim",case_name,"vel.gif"))
    # optimize(os.path.join("anim",case_name,"vel_y.gif"))
    # optimize(os.path.join("anim",case_name,"vel_z.gif"))
