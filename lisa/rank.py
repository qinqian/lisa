""" two methods to rank TFs
"""
import theano
import theano.tensor as T

def get_insilico_knockout_tensor_op(lisa_prediction, precompute, coef):
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
    # sample x (gene1_bin1, gene1_bin2...gene2_bin1,gene2_bin2...)
    y = T.extra_ops.repeat(x, precompute.shape[0], axis=0)
    tensor_del = y * precomp # sample x (gene,bin)
    tensor_del = T.reshape(tensor_del, (c.shape[0],r.shape[0],200)) # sample x gene x bin
    tensor_del = T.transpose(T.sum(tensor_del, axis=2), (1,0)) + T.constant(1) # one motif
    tensor_del_med = T.mean(tensor_del, axis=0)  # one motif
    log_tensor_del = T.log2(tensor_del) - T.log2(tensor_del_med)
    tensor_delta = r - T.dot(log_tensor_del, c)

    mode = theano.Mode(linker='cvm', optimizer='fast_run')
    theano.config.exception_verbosity = 'high'
    # theano.config.openmp = True
    theano_delta_rp = theano.function([x], tensor_delta, mode=mode)
    return theano_delta_rp

def rank_by_cluster_kl_divergence():
    """ first cluster, then evaluate kl divergence, wasserstein distance
    """
    return
