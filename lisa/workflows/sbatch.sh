#!/bin/bash

export PATH=/n/home04/xiaoleliu/ChiLin/alvin/xiaoleliu_lab/marge2/phaseI_init/miniconda3/bin:$PATH
source activate lisa

mkdir -p logs/cluster
snakemake --unlock
snakemake -j 3 --cluster-config cluster.json --immediate-submit --cluster "sbatch --time={cluster.time} --mem={cluster.memory} --partition={cluster.queue} --cpus-per-task={cluster.nCPUs} -J {cluster.name} -o {cluster.output} -e {cluster.error}"

