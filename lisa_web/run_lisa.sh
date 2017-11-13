#!/bin/bash -ex

source /data/home/qqin/miniconda3/envs/lisa2/bin/activate lisa2

outdir=$3
mkdir -p /data/home/qqin/lisa_web/upload/${outdir}
cd /data/home/qqin/lisa_web/upload/${outdir}

###nice -n 15 lisa model --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome '['H3K27ac']' --cluster=False --covariates=False --random=True --prefix test --threads 3 AR.symbol

nice -n 15 lisa model --web=True --new_rp_h5=None --new_count_h5=None --species $1 --epigenome "$2" --cluster=False --covariates=False --random=True --prefix ${outdir} --threads 3 $4

