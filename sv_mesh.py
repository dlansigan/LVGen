import numpy as np
from sv import meshing
import os
import vtk
import argparse
import sys
sys.path.append("interp-src")
import utils
from io_utils import write_vtk_polydata, write_vtu_file
import glob

### VTK writing functions from https://github.com/fkong7/Auto-LV-Modeling/blob/SimVascular/Modeling/src/io_utils.py ###

# def write_vtu_file(ug, fn):
#     print('Writing vts with name:', fn)
#     if (fn == ''):
#         raise ValueError('File name is empty')
#     writer = vtk.vtkXMLUnstructuredGridWriter()
#     writer.SetInputData(ug)
#     writer.SetFileName(fn)
#     writer.Update()
#     writer.Write()

# def write_vtk_polydata(poly, fn):
#     """
#     This function writes a vtk polydata to disk
#     Args:
#         poly: vtk polydata
#         fn: file name
#     Returns:
#         None
#     """
    
#     print('Writing vtp with name:', fn)
#     if (fn == ''):
#         return 0

#     _ , extension = os.path.splitext(fn)

#     if extension == '.vtk':
#         writer = vtk.vtkPolyDataWriter()
#     elif extension == '.vtp':
#         writer = vtk.vtkXMLPolyDataWriter()
#     else:
#         raise ValueError("Incorrect extension"+extension)
#     writer.SetInputData(poly)
#     writer.SetFileName(fn)
#     writer.Update()
#     writer.Write()
#     return

def generate_mesh(fn, ops):
    mesher = meshing.create_mesher(meshing.Kernel.TETGEN)  
    mesher.load_model(fn)
    mesher.set_walls([1])
    face_ids = mesher.get_model_face_ids()
    options = meshing.TetGenOptions(**ops)
    options.no_merge = True
    options.no_bisect = True
    options.optimization = 3
    options.quality_ratio = 1.
    mesher.generate_mesh(options)
    vol_mesh = mesher.get_mesh()
    surf_mesh = mesher.get_surface()
    return vol_mesh, surf_mesh, face_ids

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--template_dir", type=str, required=True)
    parser.add_argument("--save_dir", type=str, required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--case", type=str)
    parser.add_argument("--mesh_id", type=str, default=0)
    parser.add_argument("--phase", type=int, default=-1)
    args = parser.parse_args()

    template_dir = args.template_dir #"../data/template_LV/LV/"
    save_dir = args.save_dir #"meshes/"
    overwrite = args.overwrite
    face_names = ["wall","av","mv"]  

    mesh_ops = {
            'surface_mesh_flag': False,
            'volume_mesh_flag': True,
            'global_edge_size': 1, 
    }

    # Get filename for phase 0
    mesh_dir = "mesh_{}".format(args.mesh_id)
    fns = sorted(glob.glob(os.path.join(template_dir,mesh_dir, "phase*.vtp")))
    # fn = os.path.join(template_dir,mesh_dir,"phase{}.vtp")
    fn = fns[args.phase]

    # Set up directories for saving
    case_dir = "LV_{}/mesh".format(args.case)
    vol_fn = os.path.join(save_dir,case_dir,"mesh_complete.vtu")
    surf_fn = os.path.join(save_dir,case_dir,"mesh_complete_surface.vtp")
    os.makedirs(os.path.join(save_dir,case_dir),exist_ok=True)
    os.makedirs(os.path.join(save_dir,case_dir,"mesh-surfaces"),exist_ok=True)

    if not os.path.exists(vol_fn) or overwrite: # If volume mesh exists, assumes all others do, too

        vol_mesh, surf_mesh, face_ids = generate_mesh(fn,mesh_ops)

        # print(vol_mesh)

        # Extract faces
        for i,id in enumerate(face_ids):
            face_fn = os.path.join(save_dir,case_dir,"mesh-surfaces","{}.vtp".format(face_names[i]))
            face = utils.threshold_polydata(surf_mesh, "ModelFaceID", (id,id))
            write_vtk_polydata(face,face_fn)

        write_vtk_polydata(surf_mesh,surf_fn)
        write_vtu_file(vol_mesh,vol_fn)