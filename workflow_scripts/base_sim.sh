case="regazzoni"
phase=9
mesh=0


### GENERATE MESHES ###

# Rescale meshes first
python rescale_mesh.py \
        --template_dir generated_meshes \
        --save_dir scaled_meshes \
        --n_meshes 10 \
        --scale 30

# Clean meshes directory
rm -r cases/LV_$case/mesh

# Mesh one case
simvascular --python -- sv_mesh.py \
        --template_dir scaled_meshes/ \
        --save_dir cases/ \
        --case $case \
        --mesh_id $mesh\
        --phase $phase \
        --quality 1.2\
        --overwrite
python interpolate_meshes.py \
        --input_dir scaled_meshes/mesh_${mesh}/ \
        --output_dir cases/LV_$case/mesh/motion/ \
        --mesh_complete_surface cases/LV_$case/mesh/mesh_complete_surface.vtp\
        --num_interpolation 99\
        --num_cycle 1 \
        --duration 0.8 \
        --phase $phase
# python plot_vol.py --case cases/LV_${case}/ --T_HB 0.8
python save_init_p.py --case cases/LV_$case --init_p 13332.2 # dyn/cm2

### RUN SIMULATION ###

# Convert JSON
python convert_json.py --case $case

# Navigate to case directory
cd $case
pwd

# Clean case
rm -r 4-procs P_svZeroD Q_svZeroD svZeroD_data LV_volume.npy 

# Run case
mpiexec -n 4 ../../../build/svMultiPhysics-build/bin/svmultiphysics solver.xml 