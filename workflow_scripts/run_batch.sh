# This script runs simulations for the different geometry cases.
# Generate meshes using workflow_setup_batch.sh.

start=$1
end=$2

for case in $(seq $start $end); do
        case_dir=cases/LV_$case

        bash workflow_sim.sh $case_dir > $case_dir/sim.log
done
