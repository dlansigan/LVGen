# This script runs simulations for the different geometry cases.
# Generate meshes using workflow_setup_batch.sh.

cases_dir=$1
start=$2
end=$3

ROOT_DIR=/sv/LVGen

for case in $(seq $start $end); do
        case_dir=$ROOT_DIR/$cases_dir/LV_$case
	cd $case_dir

        rm -r *-procs P_svZeroD Q_svZeroD svZeroD_data LV_volume.npy 

done
