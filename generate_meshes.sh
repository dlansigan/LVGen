# Rescale meshes first
python rescale_mesh.py \
        --template_dir generated_meshes \
        --save_dir scaled_meshes \
        --n_meshes 10 \
        --scale 27

case="regazzoni"
phase=8
mesh=0
simvascular --python -- sv_mesh.py \
        --template_dir scaled_meshes/ \
        --save_dir cases/ \
        --case $case \
        --phase $phase \
        --mesh_id $mesh\
        --overwrite
python interpolate_meshes.py \
        --input_dir scaled_meshes/mesh_${mesh}/ \
        --output_dir cases/LV_$case/mesh/motion/ \
        --mesh_complete_surface cases/LV_$case/mesh/mesh_complete_surface.vtp\
        --num_interpolation 99\
        --num_cycle 1 \
        --duration 0.69 \
        --phase $phase
# python plot_vol.py --case cases/LV_${case}/ --T_HB 0.69
