#!/bin/bash -ex

###source /data/home/qqin/miniconda3/envs/lisa2/bin/activate lisa2
#source /data/home/qqin/miniconda3/envs/lisa2/bin/activate lisa2018
source /data/home/qqin/miniconda3/envs/lisa2/bin/activate test

outdir=$3
mkdir -p /data/home/qqin/lisa_web/upload/${outdir}
cd /data/home/qqin/lisa_web/upload/${outdir}

###nice -n 15 lisa model --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome '['H3K27ac']' --cluster=False --covariates=False --random=True --prefix test --threads 3 AR.symbol

nice -n 15 lisa model --method="$5" --web=True --new_rp_h5=None --new_count_h5=None --species $1 --epigenome "$2" --cluster=False --covariates=False --random=True --background=/data/home/qqin/lisa_web/download/data/${1}.fix_background.genes --stat_background_number=300 --background=$6 --prefix ${outdir} --threads 4 $4

echo "accomplished!!.."  >> /data/home/qqin/lisa_web/upload/${outdir}_snakemake_output.txt
sleep 1
