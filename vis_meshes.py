import numpy as np
import pyvista as pv
import argparse
import os

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--N_meshes", type=int, default=10)
    args = parser.parse_args()

    n_cols = 5
    n_rows = int(np.ceil(args.N_meshes/n_cols))
    pl = pv.Plotter(shape=(n_rows,n_cols),off_screen=True)
    face_names = ["wall","av","mv"]
    color_arr = ["cyan","magenta","yellow"]
    for n in range(args.N_meshes):
        case_dir = "cases/LV_{}/mesh".format(n)

        # Plot mesh quality
        vol_mesh = pv.read(os.path.join(case_dir,"mesh_complete.vtu"))
        row, col = np.unravel_index(n,(n_rows,n_cols))
        pl.subplot(row, col)
        pl.add_mesh(vol_mesh, style="wireframe", color="black",
                    opacity=0.2,
                    show_scalar_bar=False)
        for i,face in enumerate(face_names):
            surf_mesh = pv.read(os.path.join(case_dir,"mesh-surfaces","{}.vtp".format(face)))
            pl.add_mesh(surf_mesh,opacity=0.75, color=color_arr[i],
                        show_scalar_bar=False)
        pl.add_title("Ncells={}".format(str(vol_mesh.n_cells)),font_size=10)
        pl.camera.azimuth=-90
        pl.camera.elevation=30
        pl.camera.roll=-60

        print("Mesh %d: %d cells, %d pts" % (n,vol_mesh.n_cells,vol_mesh.n_points))
    pl.link_views()
    pl.camera.zoom(1.5)
    pl.show(screenshot="vol_meshes.png")