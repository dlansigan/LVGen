case=$1
echo $case

# Convert JSON
python ../convert_json.py --case $case

# Navigate to case directory
cd $case
pwd

# Clean case
rm -r 4-procs P_svZeroD Q_svZeroD svZeroD_data LV_volume.npy 

date

# Run case
mpiexec -n 4 svmultiphysics solver.xml 

date
