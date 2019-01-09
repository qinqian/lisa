#!/bin/bash -ex

#python generate_gallery.py

#python generate_gallery2.py

while read line; do
    fs=($line)
    echo ${fs[2]} | tr ',' '\n' > ${fs[0]}_${fs[1]}.txt
done < <(cut -f 1,9,12 lisa_results_meta_table_mouse_with_gene_sets.xls | sed 1d | sort -k 1 | uniq)

