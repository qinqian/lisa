#!/bin/bash -ex
source /project/dev/qqin/miniconda3/bin/activate base
/project/dev/qqin/miniconda3/bin/python /project/Cistrome/LISA/lisa_web/plotly_scatter.py $1 $2 $3 $4 $5 $6
