for i in {0..0}; do
    python interpolate_meshes.py \
            --input_dir generated_meshes/mesh_${i}_less_motion/ \
            --output_dir cases/LV_$i/mesh/motion/ \
            --mesh_complete_surface cases/LV_$i/mesh/mesh_complete_surface.vtp\
            --num_interpolation 4\
            --num_cycle 2 \
            --duration 1 \
            --phase 0
done