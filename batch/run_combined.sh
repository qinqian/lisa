#!/bin/bash
#SBATCH -J lisa_GEO # A single job name for the array
#SBATCH -n 8 # Number of cores
#SBATCH -N 1 # All cores on one machine
#SBATCH -p serial_requeue # Partition
#SBATCH --mem 10000 # Memory request (4Gb)
#SBATCH -t 0-8:00 # Maximum execution time (D-HH:MM)
#SBATCH -o lisa_%A_%a.out # Standard output
#SBATCH -e lisa_%A_%a.err # Standard error

# module load gcc/7.1.0-fasrc01 openmpi/2.1.0-fasrc01 hdf5/1.10.1-fasrc01

export PATH=/n/home08/cliffmeyer/Jingyu/miniconda3/bin:$PATH
source activate lisa_python3_env

cd /n/home08/cliffmeyer/projects/lisa/gene_num_sample_size
python run_combined.py -s "${SLURM_ARRAY_TASK_ID}" -n $1

