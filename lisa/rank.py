""" two methods to rank TFs
"""
import theano
import theano.tensor as T
import pandas as pd
import numpy as np
import scipy.stats as stats
from numpy.linalg import norm

def get_insilico_knockout_tensor_op(lisa_prediction, precompute, coef, original_median=None):
    """ use theano tensor operation to speed up
    return a theano.function

    lisa_prediction: numpy array
    precompute: numpy array
    coef: pandas DataFrame
    """
    x = T.imatrix('E') # each motif tensor
    precomp = theano.shared(precompute.astype(theano.config.floatX), name='precompute')
    r = theano.shared(lisa_prediction.astype(theano.config.floatX), name='Lisa RP')
    c = theano.shared(coef.iloc[:, 0].values.astype(theano.config.floatX), name='coefficients')
    m = theano.shared(original_median.astype(theano.config.floatX), name='original_rp_median')

    # sample x (gene1_bin1, gene1_bin2...gene2_bin1,gene2_bin2...)
    y = T.extra_ops.repeat(x, precompute.shape[0], axis=0)
    tensor_del = y * precomp # sample x (gene,bin)
    tensor_del = T.reshape(tensor_del, (c.shape[0],r.shape[0],200)) # sample x gene x bin
    tensor_del = T.transpose(T.sum(tensor_del, axis=2), (1,0)) + T.constant(1) # one motif

    ##tensor_del_med = T.mean(tensor_del, axis=0)  # one motif
    ##log_tensor_del = T.log2(tensor_del) - T.log2(tensor_del_med)

    log_tensor_del = T.log2(tensor_del) - m # original median already take log2
    tensor_delta = r - T.dot(log_tensor_del, c)

    mode = theano.Mode(linker='cvm', optimizer='fast_run')
    theano.config.exception_verbosity = 'high'
    # theano.config.openmp = True
    theano_delta_rp = theano.function([x], tensor_delta, mode=mode)
    return theano_delta_rp

def rank_by_entropy(pq, kl=True):
    """ evaluate kl divergence, wasserstein distance
    wasserstein: http://pythonhosted.org/pyriemann/_modules/pyriemann/utils/distance.html
    """
    # to avoid Inf cases
    pq = pq + 0.0000001
    pq = pq/pq.sum(axis=0)

    if kl:     # entropy actually can calculate KL divergence
        final=pq.iloc[:, :-1].apply(
            lambda x: stats.entropy(x, pq.iloc[:, -1], base=2), axis=0)
        label = 'KL'
    else:      # JS divergence
        final=pq.iloc[:, :-1].apply(
            lambda x: JSD(x, pq.iloc[:, -1]), axis=0)
        label = 'JSD'
    final.sort_values(ascending=False, inplace=True)
    rank = final.rank(ascending=False)
    final = pd.concat([final, rank], axis=1)
    final.columns = [label, 'rank']
    return final

def JSD(P, Q):
    """ compute JS divergence
    JSD:  http://stackoverflow.com/questions/15880133/jensen-shannon-divergence
    """
    P = P / norm(P, ord=1)
    Q = Q / norm(Q, ord=1)
    M = 0.5 * (P + Q)
    return 0.5 * (stats.entropy(P, M) + stats.entropy(Q, M))
