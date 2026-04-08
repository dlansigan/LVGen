# This script sets up the meshes for the different geometry cases.
# Run simulations using workflow_run_batch.sh.

start=$1
end=$2
phase=9

# Rescale meshes first
python rescale_mesh.py \
        --template_dir generated_meshes \
        --save_dir scaled_meshes \
        --n_meshes 100 \
        --target_vol 110 \
        --phase 9

for case in $(seq $start $end); do
        case_dir=cases/LV_$case

        # Clean meshes directory
        rm -r $case_dir/mesh
        mkdir -p $case_dir/mesh

        # Mesh one case
        simvascular --python -- sv_mesh.py \
                --template_dir scaled_meshes/ \
                --case $case_dir \
                --mesh_id $case\
                --phase $phase \
                --quality 1.0\
                --edge_size 0.5\
                --calc_metrics\
                --overwrite > $case_dir/mesh/mesh.log
        python interpolate_meshes.py \
                --input_dir scaled_meshes/mesh_${case}/ \
                --output_dir $case_dir/mesh/motion/ \
                --mesh_complete_surface $case_dir/mesh/mesh_complete_surface.vtp\
                --num_interpolation 99\
                --num_cycle 1 \
                --duration 0.8 \
                --phase $phase
        python save_init_p.py --case $case_dir --init_p 13332.2 # dyn/cm2

        # Get param files
        cp cases/base/* $case_dir
        sed -i "s|<SVZERODSOLVER>|${SV_ZERODSOLVER_INT_PATH}|g" $case_dir/solver.xml
done
