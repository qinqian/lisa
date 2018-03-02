#!/bin/bash -ex


mkdir -p macro_ape_cistrome
for i in cistrome/*pwm;do
    pi=$(basename ${i/.pwm/})
    for j in cistrome/*pwm;do
        pj=$(basename ${j/.pwm/})
        java -cp ape-2.0.1.jar ru.autosome.macroape.EvalSimilarity $i $j 1>macro_ape_cistrome/${pi}_${pj}_macro_ape.txt
    done
done
