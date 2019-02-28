""" lisa utlity functions """
from multiprocessing import Pool, cpu_count
import math
import numpy as np

from scipy.stats import wilcoxon, ks_2samp
import scipy
import pandas as pd

def multiple_apply(func, df, x, y, num_processes=None):
    ''' Apply a function separately to each column in a dataframe, in parallel.'''
    # If num_processes is not specified, default to minimum(#columns, #machine-cores)
    if num_processes==None:
        #num_processes = min(df.shape[1], cpu_count())
        num_processes = 5
    
    # 'with' context manager takes care of pool.close() and pool.join() for us
    with Pool(num_processes) as pool:
        # we need a sequence of columns to pass pool.map
        seq = [[df[col_name][x].values, df[col_name][y].values] for col_name in df.columns]
        # pool.map returns results as a list
        results_list = pool.map(func, seq)
        # return list of processed columns, concatenated together as a new dataframe
        return pd.DataFrame(results_list, index=df.columns)


def convert_name(name):
    try:
        name = name.decode('utf-8').replace("tf_", "")
    except:
        name = name.replace("tf_", "")
    return name

def one_side_ks_test(x, y):
    """ http://stackoverflow.com/questions/16296225/one-sided-wilcoxon-signed-rank-test-using-scipy
    So, to get one-side p value, you just need prob/2. or 1-prob/2.

    here: one-side significant less x < y
    """
    test = ks_2samp(x, y)
    d = test[0]
    p = test[1]/2
    return p

def mannwhitneyu_test(x,y,how="two-sided"):
    try:
        return scipy.stats.mannwhitneyu(x,y,alternative=how)[1]
    except:
        return 1

def binarize_gene_set(gene_set, *args):
    """ gene_set: one gene per line
    """
    #print(gene_set)
    refseq, symbol = args
    with open(gene_set) as fin:
        gene_set = list(set([line.strip().upper() for line in fin]))
    gene_vec = np.zeros(len(refseq))
    if len(np.intersect1d(refseq, gene_set)) > 5:
        #print('input refseq ...')
        gene_vec[np.in1d(refseq, gene_set)] = 1
    elif len(np.intersect1d(symbol, gene_set)) > 5:
        #print('input symbol ...')
        gene_vec[np.in1d(symbol, gene_set)] = 1
    else:
        raise Exception("no genes found in referenence...")
    return gene_vec

class Weight:
    """ Exponential decay function """
    def __init__(self, bin_length=1000):
        padding = int(1e5)            # TSS +/- 100kb
        assert bin_length > 0
        assert (2*padding+bin_length)%bin_length == 0

        self.bin_length = bin_length
        self.bin_num = (2*padding+bin_length)/bin_length      # bin number

        distances = np.array([z + bin_length/2 for z in
                              range(int(-padding-bin_length/2),
                                    int(padding+bin_length/2), bin_length)],
                             dtype=np.float32)
        self.alpha = -math.log(1.0/3.0)*10                    # 1e5/1e4, 1e4: half decay
        self.balance_weight(distances)                        # weight

    def get_weight(self):
        """ get the weight """
        return self.weight

    def get_binnum(self):
        """ get the bin number around TSS """
        return self.bin_num

    def balance_weight(self, distances):
        """ function to balance weight according the TSS and bin center offset
        """
        weight = np.exp(-np.fabs(distances) * self.alpha/1e5)
        self.weight = 2*weight/ (1+weight)
