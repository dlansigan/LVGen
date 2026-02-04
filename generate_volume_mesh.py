import numpy as np
import pyvista as pv
from tetgen import TetGen
import os
import matplotlib.pyplot as plt

if __name__=="__main__":
    template_dir = "../data/template_LV/LV/"
    save_dir = "meshes/"
    face_names = ["wall","av","mv"]
    overwrite = False

    n_meshes = 10  

    n_cols = 5
    n_rows = int(np.ceil(n_meshes/n_cols))
    pl = pv.Plotter(shape=(n_rows,n_cols),off_screen=True)

    # Generate meshes
    for n in range(n_meshes):
        # Load surface mesh at phase 0
        mesh_dir = "mesh_{}".format(str(n))
        fn = os.path.join(template_dir,mesh_dir,"phase0.vtp")
        surf_mesh = pv.read(fn)

        vol_fn = os.path.join(save_dir,mesh_dir,"mesh_complete.vtu")
        os.makedirs(os.path.join(save_dir,mesh_dir),exist_ok=True)
        print(vol_fn)

        if not os.path.exists(vol_fn) or overwrite: # If volume mesh exists, assumes all others do, too
            # Generate volume mesh
            tetgen = TetGen(surf_mesh)
            tetgen.tetrahedralize(switches="pq1.Y")
            vol_mesh = tetgen.grid

            # Save volume mesh
            vol_mesh.save(vol_fn)

            # Extract and save individual faces
            os.makedirs(os.path.join(save_dir,mesh_dir,"mesh-surfaces"),exist_ok=True)
            face_ids = np.unique(surf_mesh["ModelFaceID"])
            for i,id in enumerate(face_ids):
                face = surf_mesh.threshold(id,scalars="ModelFaceID").extract_surface()
                face.save(os.path.join(save_dir,mesh_dir,"mesh-surfaces","{}.vtp".format(face_names[i])))

        # Plot
        vol_mesh = pv.read(os.path.join(save_dir,mesh_dir,"mesh_complete.vtu"))
        row, col = np.unravel_index(n,(n_rows,n_cols))
        pl.subplot(row, col)
        pl.add_mesh(vol_mesh, style="wireframe", color="white",
                    opacity=0.3,
                    show_scalar_bar=False)
        for i,face in enumerate(face_names):
            surf_mesh = pv.read(os.path.join(save_dir,mesh_dir,"mesh-surfaces","{}.vtp".format(face)))
            pl.add_mesh(surf_mesh,scalars="ModelFaceID",opacity=0.75,
                        show_scalar_bar=False)
        pl.add_title("Ncells={}".format(str(vol_mesh.n_cells)),font_size=10)
        pl.camera.azimuth=-90
        pl.camera.elevation=30
        pl.camera.roll=-60

        print("Mesh %d: %d cells, %d pts" % (n,vol_mesh.n_cells,vol_mesh.n_points))
    pl.link_views()
    pl.camera.zoom(1.5)
    pl.show(screenshot="vol_meshes.png")

    # Plot cell quality
    fig,ax = plt.subplots(1,2,figsize=(8,3))
    ax[0].hist(vol_mesh.compute_cell_quality("volume")["CellQuality"],bins=50,range=(0,1e-6))
    ax[0].set_title("volume")
    ax[0].set_xlabel("# cells")
    ax[1].hist(vol_mesh.compute_cell_quality("aspect_ratio")["CellQuality"],bins=50,range=(0,5))
    ax[1].set_title("aspect_ratio")
    ax[1].set_xlabel("# cells")
    fig.savefig("mesh_quality.png",bbox_inches="tight")
