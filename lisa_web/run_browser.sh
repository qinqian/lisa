#!/bin/bash -ex

#python make_session.py upload/2017-08-22_0830220.34508.H3K27ac.coefs.csv upload/2017-08-18_1107470.10356.txt.H3K27ac.chipseq.p_value.csv upload/2017-08-24_0952320.67641.txt.foreground_gene
links=$1
links=${links/.coefs.csv/}

## http://lisa.cistrome.org//data5/lisa_browser/test.bed

shuf /data/home/qqin/lisa_web/upload/$3 | head -20 > /data/home/qqin/lisa_web/upload/${3}.20
python make_session.py /data/home/qqin/lisa_web/upload/$1 /data/home/qqin/lisa_web/upload/$2 /data/home/qqin/lisa_web/upload/${3}.20 > /data/home/qqin/lisa_web/upload/${links}.url

