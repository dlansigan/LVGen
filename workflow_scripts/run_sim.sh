case=$1
echo $case

# Convert JSON
python convert_json.py --case $case

# Navigate to case directory
cd $case
pwd

# Clean case
rm -r *-procs P_svZeroD Q_svZeroD svZeroD_data LV_volume.npy 

date

# Run case
mpiexec -n 16 ../../../build/svMultiPhysics-build/bin/svmultiphysics solver.xml 

date
