import os
import pyvista as pv
import argparse

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=str)
    parser.add_argument("--scale", type=float, default=1)
    parser.add_argument("--init_p", type=float, default=None)
    args = parser.parse_args()

    faces = ["wall","av","mv"]

    # Set up directories for saving
    case_dir = args.case
    vol_fn = os.path.join(case_dir,"mesh/mesh_complete.vtu")
    surf_fn = os.path.join(case_dir,"mesh/mesh_complete_surface.vtp")

    # Faces
    for name in faces:
        face_fn = os.path.join(case_dir,"mesh/mesh-surfaces","{}.vtp".format(name))
        face = pv.read(face_fn)
        face.points *= args.scale
        face.save(face_fn)

    # Scale, if needed
    vol_mesh = pv.read(vol_fn)
    surf_mesh = pv.read(surf_fn)
    vol_mesh.points*=args.scale
    surf_mesh.points*=args.scale

    # Initialize pressure, if needed
    if args.init_p:
        vol_mesh.point_data["Pressure"] = args.init_p

    vol_mesh.save(vol_fn)
    surf_mesh.save(surf_fn)
