import numpy as np
import pyvista as pv
import glob
import os

if __name__=="__main__":
    template_dir = '../data/template_LV/LV/'
    n_meshes = 10
    n_phases = 10

    n_cols = 5
    n_rows = int(np.ceil(n_meshes/n_cols))
    pl = pv.Plotter(shape=(n_rows,n_cols))
    pl.open_gif('meshes.gif')
    
    meshes = {}
    for phase in range(n_phases):
        for n in range(n_meshes):
            # Load mesh at phase
            mesh_dir = "mesh_{}".format(str(n))
            fn = os.path.join(template_dir,mesh_dir,"phase{}.vtp".format(str(phase)))

            # Plot
            row, col = np.unravel_index(n,(n_rows,n_cols))
            pl.subplot(row, col)
            if phase==0:
                meshes[str(n)] = pv.read(fn)
                pl.add_mesh(meshes[str(n)],scalars='ModelFaceID',
                            opacity=0.75,
                            show_scalar_bar=False)
                # pl.add_title(mesh_dir,font_size=10)
                pl.camera.azimuth=-90
                pl.camera.elevation=30
                pl.camera.roll=-60
                pl.camera.zoom(1.5)
            else:
                new_mesh = pv.read(fn)
                meshes[str(n)].points = new_mesh.points
            
        pl.write_frame()
    pl.link_views()
    # pl.show()
    pl.close()
