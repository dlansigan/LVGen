import numpy as np
import pyvista as pv
import glob
import os

if __name__=="__main__":
    interp_dir = 'meshes/mesh_0/motion/Debug'
    fns = sorted(glob.glob(os.path.join(interp_dir,'debug*.vtp')))
    n_phases = len(fns)
    n_meshes = 3

    n_cols = 3
    n_rows = 1
    pl = pv.Plotter(shape=(n_rows,n_cols),border=False)
    pl.open_gif('meshes_interp.gif',fps=50)
    
    meshes = {}
    for phase in range(n_phases):
        for n in range(n_meshes):
            # Load mesh at phase
            interp_dir = "meshes/mesh_{}/motion/Debug".format(str(n))
            phase_name = os.path.basename(fns[phase])
            fn = os.path.join(interp_dir,phase_name)

            # Plot
            pl.subplot(0,n)
            if phase==0:
                meshes[str(n)] = pv.read(fn)
                pl.add_mesh(meshes[str(n)],scalars='ModelFaceID',
                            opacity=0.75,
                            show_scalar_bar=False)
                # pl.add_title(mesh_dir,font_size=10)
                pl.camera.azimuth=-90
                pl.camera.elevation=30
                pl.camera.roll=-60
                pl.camera.zoom(1.2)
            else:
                new_mesh = pv.read(fn)
                meshes[str(n)].points = new_mesh.points
            
        pl.write_frame()
    pl.link_views()
    # pl.show()
    pl.close()
