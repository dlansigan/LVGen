import pyvista as pv
import numpy as np
import os

if __name__ == "__main__":

    template_path = 'data/template_meshes/LV.vtp'
    template_mesh = pv.read(template_path)
    save_path = 'data/template_LV/'
    os.makedirs(save_path,exist_ok=True)

    # Define sphere for selecting points
    radius = 0.053
    center = (0.58,0.47,0.38)
    sph = pv.Sphere(radius=radius, center=center) # For visualization purposes

    # Get distances of points in template to center
    template_pts = template_mesh.points
    dist = np.linalg.norm(template_pts-np.array(center),axis=1)
    pidx = np.argwhere(dist<=radius)
    cidx = []
    for i in pidx:
        cidx.append(template_mesh.point_cell_ids(i[0]))
    cidx = np.concatenate(cidx)
    template_mesh['ModelFaceID'][cidx] = 3
    print(np.unique(template_mesh.cell_data['ModelFaceID']))

    print(template_mesh)

    template_mesh.save(save_path + 'LV.vtp')
    
    pl = pv.Plotter()
    pl.add_mesh(template_mesh,scalars='ModelFaceID',opacity=1,show_edges=True)
    pl.add_mesh(sph,opacity=0.5)
    pl.show_axes()
    pl.show()
