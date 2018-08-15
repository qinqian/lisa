import argparse
import os
import time
import glob

filenames=glob.glob('/n/home08/cliffmeyer/projects/lisa/gene_num_sample_size/output/*gene_symbol')
file_path="/n/home08/cliffmeyer/projects/lisa/gene_num_sample_size"

if __name__ == "__main__":
    start = time.time()
    try:
        parser = argparse.ArgumentParser(description="""lisa TCGA gene sets.""")
        #parser.add_argument( '-c', dest='chip',   type=str, required=True, help='input bed file' )
        parser.add_argument( '-n', dest='number',   type=int, required=True)
        parser.add_argument( '-s', dest='sample',   type=int, required=True)
        args = parser.parse_args()
        filename=filenames[args.number-1]
        os.chdir(file_path)
        os.system("mkdir -p %s_%s" % (filename, args.sample))
        os.chdir("%s_%s" % (filename, args.sample))
        os.system("cp %s ." % filename)
        os.system("lisa model --method='all' --web=False --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome \'[\'DNase\']\' --cluster=False --covariates=False --random=True --prefix %s --threads 8 --sample-number %s %s" % (os.path.basename(filename)+"_"+str(args.sample), args.sample, os.path.basename(filename)))
    except KeyboardInterrupt:
        sys.stderr.write("User interrunpt me! ;-) Bye!\n")
