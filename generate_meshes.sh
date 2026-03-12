# # Rescale meshes first
# python rescale_mesh.py \
#         --template_dir generated_meshes \
#         --save_dir scaled_meshes \
#         --n_meshes 10 \
#         --scale 27

case="regazzoni_1"
phase=9
mesh=1

# Clean meshes directory
rm -r cases/LV_$case/mesh

# Mesh one case
simvascular --python -- sv_mesh.py \
        --template_dir scaled_meshes/ \
        --save_dir cases/ \
        --case $case \
        --phase $phase \
        --mesh_id $mesh\
        --quality 1.6\
        --overwrite
python interpolate_meshes.py \
        --input_dir scaled_meshes/mesh_${mesh}/ \
        --output_dir cases/LV_$case/mesh/motion/ \
        --mesh_complete_surface cases/LV_$case/mesh/mesh_complete_surface.vtp\
        --num_interpolation 99\
        --num_cycle 1 \
        --duration 0.8 \
        --phase $phase
python plot_vol.py --case cases/LV_${case}/ --T_HB 0.8
python save_init_p.py --case cases/LV_$case --init_p 8.0


# Mesh multiple cases
start=0
end=9
for case in $(seq $start $end)
do
    simvascular --python -- sv_mesh.py \
        --template_dir scaled_meshes/ \
        --save_dir cases/ \
        --case $case \
        --phase $phase \
        --mesh_id $case\
        --quality 1.6\
        --overwrite
        # python interpolate_meshes.py \
        #         --input_dir scaled_meshes/mesh_${mesh}/ \
        #         --output_dir cases/LV_$case/mesh/motion/ \
        #         --mesh_complete_surface cases/LV_$case/mesh/mesh_complete_surface.vtp\
        #         --num_interpolation 99\
        #         --num_cycle 1 \
        #         --duration 0.8 \
        #         --phase $phase
        # python save_init_p.py --case cases/LV_$case --init_p 8.0
done

# Visualize 
python vis_meshes.py
