# This script runs simulations for the different geometry cases.
# Generate meshes using workflow_setup_batch.sh.

cases_dir=$1
start=$2
end=$3

for case in $(seq $start $end); do
        case_dir=$cases_dir/LV_$case
	echo $case_dir

        bash workflow_scripts/run_sim.sh $case_dir > $case_dir/sim.log
done
