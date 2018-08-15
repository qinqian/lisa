#!/bin/bash 
for i in `seq 1 18`; do
    echo $i
    sbatch --array=3-100:2 --constraint="amd" --open-mode=append run_combined.sh $i
done
