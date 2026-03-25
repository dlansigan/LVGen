# This script sets up the meshes for the mesh convergence study.
# Run simulations using workflow_sim.sh, e.g.:
#     bash workflow_sim.sh cases/LV_regazzoni

cases=("regazzoni_coarse" "regazzoni" "regazzoni_fine" "regazzoni_finer")
quality=(1.6 1.2 1.0 1.0)
edge=(1.0 1.0 0.5 0.2)
phase=9
mesh=0

# Rescale meshes first
python rescale_mesh.py \
        --template_dir generated_meshes \
        --save_dir scaled_meshes \
        --n_meshes 10 \
        --scale 30

for i in "${!cases[@]}"; do
        case=${cases[i]}
        q=${quality[i]}
        e=${edge[i]}
        case_dir=cases/LV_$case

        ### GENERATE MESHES ###

        # Clean meshes directory
        rm -r $case_dir/mesh
        mkdir $case_dir/mesh

        # Mesh one case
        simvascular --python -- sv_mesh.py \
                --template_dir scaled_meshes/ \
                --case $case_dir \
                --mesh_id $mesh\
                --phase $phase \
                --quality $q\
                --edge_size $e\
                --overwrite > $case_dir/mesh/mesh.log
        python interpolate_meshes.py \
                --input_dir scaled_meshes/mesh_${mesh}/ \
                --output_dir $case_dir/mesh/motion/ \
                --mesh_complete_surface $case_dir/mesh/mesh_complete_surface.vtp\
                --num_interpolation 99\
                --num_cycle 1 \
                --duration 0.8 \
                --phase $phase
        python save_init_p.py --case $case_dir --init_p 13332.2 # dyn/cm2
done
