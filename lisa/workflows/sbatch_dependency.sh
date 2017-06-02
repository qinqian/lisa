#!/bin/bash

export PATH=/n/home04/xiaoleliu/ChiLin/alvin/xiaoleliu_lab/marge2/phaseI_init/miniconda3/bin:$PATH
source activate lisa

mkdir -p logs/cluster
#snakemake --unlock
#parallel simple job
#snakemake -j 150 --cluster-config ../cluster.json --immediate-submit --cluster "sbatch --time={cluster.time} --mem={cluster.memory} --partition={cluster.queue} --cpus-per-task={cluster.nCPUs} -J {cluster.name} -o {cluster.output} -e {cluster.error} --open-mode=append"

#with dependencies/multi-dependencies on
split -d -l 100 ../creeds_tf.txt ../creeds_tf.txt.
for i in ../creeds_tf.txt.*;do
echo "------"
echo $i
echo "------"
snakemake --config gene_list=${i} -j 50 --immediate-submit --cluster-config ../cluster.json --cluster "export PATH=/n/home04/xiaoleliu/ChiLin/alvin/xiaoleliu_lab/marge2/phaseI_init/miniconda3/bin:$PATH;source activate lisa; ../sbatch_script.py {dependencies}"
break
done

