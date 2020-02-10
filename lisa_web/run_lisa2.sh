#!/bin/bash -ex

source /project/dev/qqin/miniconda3/bin/activate lisa3

outdir=$3
mkdir -p /project/Cistrome/LISA/lisa_web/upload/${outdir}
cd /project/Cistrome/LISA/lisa_web/upload/${outdir}

nice -n 15 lisa model --clean=True --method="$4" --web=True --new_rp_h5=None --new_count_h5=None --species $1 --epigenome "$2" --cluster=False --covariates=False --random=True --prefix ${outdir} --background=$7 --stat_background_number=300 --threads 4 $5 $6

echo "accomplished!!.."  >> /project/Cistrome/LISA/lisa_web/upload/${outdir}_snakemake_output.txt
sleep 1
