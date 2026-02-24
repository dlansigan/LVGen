# Rescale meshes first
# python rescale_mesh.py --template_dir generated_meshes --save_dir scaled_meshes --n_meshes 10

# case="kong"
# simvascular --python -- sv_mesh.py --template_dir scaled_meshes/ --save_dir cases/ --case $case --overwrite
# python interpolate_meshes.py \
#         --input_dir scaled_meshes/mesh_0_less_motion/ \
#         --output_dir cases/LV_$case/mesh/motion/ \
#         --mesh_complete_surface cases/LV_$case/mesh/mesh_complete_surface.vtp\
#         --num_interpolation 99\
#         --num_cycle 1 \
#         --duration 1.0 \
#         --phase 0

case="kong_genBC"
simvascular --python -- sv_mesh.py --template_dir scaled_meshes/ --save_dir cases/ --case $case --overwrite
python interpolate_meshes.py \
        --input_dir scaled_meshes/mesh_0_less_motion/ \
        --output_dir cases/LV_$case/mesh/motion/ \
        --mesh_complete_surface cases/LV_$case/mesh/mesh_complete_surface.vtp\
        --num_interpolation 99\
        --num_cycle 1 \
        --duration 1.0 \
        --phase 0

case="regazzoni"
simvascular --python -- sv_mesh.py --template_dir scaled_meshes/ --save_dir cases/ --case $case --overwrite
python interpolate_meshes.py \
        --input_dir scaled_meshes/mesh_0_less_motion/ \
        --output_dir cases/LV_$case/mesh/motion/ \
        --mesh_complete_surface cases/LV_$case/mesh/mesh_complete_surface.vtp\
        --num_interpolation 99\
        --num_cycle 1 \
        --duration 1.0 \
        --phase 0
