for i in {0..9}; do
    python interpolate_meshes.py \
            --input_dir ../data/template_LV/LV/mesh_$i/ \
            --output_dir meshes/mesh_$i/motion/ \
            --num_interpolation 4\
            --num_cycle 2 \
            --duration 1 \
            --phase 0
done