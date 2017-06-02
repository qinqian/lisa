#!/usr/bin/env python3
"""
Submit this clustering script for sbatch to snakemake with:
    snakemake -j 99 --debug --immediate-submit --cluster-config cluster.json --cluster 'sbatch_script.py {dependencies}'
"""
## In order to submit all the jobs to the moab queuing system, one needs to write a wrapper.
import sys
import subprocess
import re
import os
from snakemake.utils import read_job_properties
import argparse

parser = argparse.ArgumentParser(description='Snakemake script')
parser.add_argument("dependencies", nargs="*", help="{{dependencies}} string given by snakemake\n")
parser.add_argument("snakescript", help="Snakemake generated shell script with commands to execute snakemake rule\n")

args = parser.parse_args()

dependencies = args.dependencies
jobscript = args.snakescript
print(dependencies, file=sys.stderr)
print(jobscript, file=sys.stderr)

job_properties = read_job_properties(jobscript)
# access property defined in the cluster configuration file (Snakemake >=3.6.0), cluster.json
time = job_properties["cluster"]["time"]
cpu = job_properties["cluster"]["nCPUs"]
mem = job_properties["cluster"]["memory"]
queue = job_properties["cluster"]["queue"]
name = job_properties["cluster"]["name"]
output = job_properties["cluster"]["output"]
error = job_properties["cluster"]["error"]

# all figure out job dependencies, the last argument is the jobscript which is baked in snakemake
if dependencies == None or len(dependencies) < 1:
    deps = " "
else:
    deps = " -d " + ','.join(["afterok:%s" % d for d in dependencies])

print(job_properties['rule'], file=sys.stderr)
if job_properties['rule'].startswith('merge'):
    cmdline = 'sbatch --time={time} {deps} --mem=50 --partition={queue} --cpus-per-task=1 -J {name} -o {output} -e {error} --open-mode=append {job}'.format(name=name, time = time, queue=queue, output=output, error=error, deps=deps, job=jobscript)
else:
    cmdline = 'sbatch --time={time} {deps} --mem={mem} --partition={queue} --cpus-per-task={cpu} -J {name} -o {output} -e {error} --open-mode=append {job}'.format(mem=mem, cpu=cpu, name=name, time = time, queue=queue, output=output, error=error, deps=deps, job=jobscript)

popenrv = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).communicate()

print(cmdline, file=sys.stderr)
#(b'Submitted batch job 86634327\n', None)
print(popenrv, file=sys.stderr)
print("%i" % int(popenrv[0].strip().split()[-1]), file=sys.stderr)
print("%i" % int(popenrv[0].strip().split()[-1]))
