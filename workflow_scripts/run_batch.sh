# This script runs simulations for the different geometry cases.
# Generate meshes using workflow_setup_batch.sh.

start=$1
end=$2

for case in $(seq $start $end); do
        case_dir=$STORAGE2/Active/dlavacot/LV_sims/LV_$case
	echo $case_dir

        bash workflow_scripts/run_sim.sh $case_dir > $case_dir/sim.log
done
