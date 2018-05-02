#!/usr/bin/env python

import os
import sys
import h5py

with h5py.File(h5) as store:
    gene_annotation = np.array(list(map(lambda x: x.decode('utf-8'),
                                        store['RefSeq'][...])))
    ids = list(map(lambda x: x.decode('utf-8').split('_')[0],
                   store['IDs'][...]))

    high_quality_ids = list(set(high_quality_ids) & set(ids))
    map_id = {}
    for i, c in enumerate(ids):
        map_id[c] = i
        idx = np.array([map_id[str(i)] for i in high_quality_ids])
        sort_index = np.argsort(idx)
        index = idx[sort_index]
        iid = np.array(high_quality_ids)[sort_index]
        return pd.DataFrame(store['RP'][:, index], columns=iid,
                            index=gene_annotation)

with h5py.File("") as store:
    store['RP']
