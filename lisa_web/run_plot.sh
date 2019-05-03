#!/bin/bash -ex
source /data/home/qqin/miniconda3/envs/lisa2/bin/activate test
python /data/home/qqin/lisa_web/plotly_scatter.py $1 $2 $3 $4 $5 $6

###nice -n 15 lisa model --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome '['H3K27ac']' --cluster=False --covariates=False --random=True --prefix test --threads 3 AR.symbol

# upload/multi4_2018_04_20_0917250.864_gs1.txt.lisa_direct.csv upload/multi4_2018_04_20_0917250.864_gs2.txt.lisa_direct.benchmark.txt
# python plotly_scatter.py  upload/multi4_2018_04_20_0917250.864_gs1.txt.lisa_direct.csv upload/multi4_2018_04_20_0917250.864_gs2.txt.lisa_direct.csv
