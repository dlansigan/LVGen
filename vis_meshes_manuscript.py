import numpy as np
import pyvista as pv
import argparse
import os

def add_mesh_to_plotter(pl, vol_mesh, surf_meshes):
    d = [1,1,1]
    pl.add_mesh(vol_mesh.clip(d,crinkle=True), show_edges=True, edge_color='black', color='white',
                show_scalar_bar=False)
    for surf_mesh in surf_meshes:
        pl.add_mesh(surf_mesh,opacity=0.2, color='lightblue',
                    show_scalar_bar=False)

def set_mesh_camera(pl):
    pl.camera.azimuth=-40
    pl.camera.elevation=30
    pl.camera.roll=-60

def save_mesh_subplot(vol_mesh, surf_meshes, mesh_num, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "LV_mesh_{}.eps".format(mesh_num))

    save_pl = pv.Plotter(off_screen=True,window_size=(500,600))
    add_mesh_to_plotter(save_pl, vol_mesh, surf_meshes)
    # save_pl.add_title("Ncells={}".format(str(vol_mesh.n_cells)),font_size=10)
    set_mesh_camera(save_pl)
    # save_pl.image_scale=5
    save_pl.camera.zoom(1.45)
    save_pl.show(auto_close=False)
    save_pl.save_graphic(save_path)
    save_pl.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--N_meshes", type=int, default=10)
    args = parser.parse_args()

    n_cols = 5
    n_rows = int(np.ceil(args.N_meshes/n_cols))
    pl = pv.Plotter(shape=(n_rows,n_cols))
    face_names = ["wall","av","mv"]
    save_dir = os.path.join("figs","meshes")
    for n in range(args.N_meshes):
        case_dir = "cases/LV_{}/mesh".format(n)

        # Plot mesh quality
        vol_mesh = pv.read(os.path.join(case_dir,"mesh_complete.vtu"))
        surf_meshes = []
        for face in face_names:
            surf_meshes.append(pv.read(os.path.join(case_dir,"mesh-surfaces","{}.vtp".format(face))))

        row, col = np.unravel_index(n,(n_rows,n_cols))
        pl.subplot(row, col)
        add_mesh_to_plotter(pl, vol_mesh, surf_meshes)
        # pl.add_title("Ncells={}".format(str(vol_mesh.n_cells)),font_size=10)
        set_mesh_camera(pl)
        save_mesh_subplot(vol_mesh, surf_meshes, n, save_dir)

        print("Mesh %d: %d cells, %d pts" % (n,vol_mesh.n_cells,vol_mesh.n_points))
    pl.link_views()
    pl.camera.zoom(1.5)
    # pl.show()
