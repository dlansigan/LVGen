start=$1
end=$2

for case in $(seq $start $end); do
    case_dir=cases/LV_$case
    echo $case_dir
    cp -r $case_dir/* /mnt/Active/dlavacot/LV_sims/data/LV_$case
    # cp -r $case_dir /mnt/Active/dlavacot/LV_sims/data/
done