# # Rescale meshes first
# python rescale_mesh.py \
#         --template_dir generated_meshes \
#         --save_dir scaled_meshes \
#         --n_meshes 10 \
#         --scale 30

case="regazzoni_fine"
phase=9
mesh=0
case_dir=cases/LV_$case

# Clean meshes directory
rm -r $case_dir/mesh
mkdir $case_dir/mesh

# Mesh one case
simvascular --python -- sv_mesh.py \
        --template_dir scaled_meshes/ \
        --case $case_dir \
        --mesh_id $mesh\
        --phase $phase \
        --quality 1.\
        --edge_size 0.5\
        --overwrite
python interpolate_meshes.py \
        --input_dir scaled_meshes/mesh_${mesh}/ \
        --output_dir $case_dir/mesh/motion/ \
        --mesh_complete_surface $case_dir/mesh/mesh_complete_surface.vtp\
        --num_interpolation 99\
        --num_cycle 1 \
        --duration 0.8 \
        --phase $phase
# python plot_vol.py --case cases/LV_${case}/ --T_HB 0.8
python save_init_p.py --case $case_dir --init_p 13332.2 # dyn/cm2


# # Mesh multiple cases
# start=0
# end=9
# for case in $(seq $start $end)
# do
#     simvascular --python -- sv_mesh.py \
#         --template_dir scaled_meshes/ \
#         --save_dir cases/ \
#         --case $case \
#         --phase $phase \
#         --mesh_id $case\
#         --quality 1.2\
#         --overwrite
#         # python interpolate_meshes.py \
#         #         --input_dir scaled_meshes/mesh_${mesh}/ \
#         #         --output_dir $case_dir/mesh/motion/ \
#         #         --mesh_complete_surface $case_dir/mesh/mesh_complete_surface.vtp\
#         #         --num_interpolation 99\
#         #         --num_cycle 1 \
#         #         --duration 0.8 \
#         #         --phase $phase
#         # python save_init_p.py --case $case_dir --init_p 8.0
# done

# # Visualize 
# python vis_meshes.py
