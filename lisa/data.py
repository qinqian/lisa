"""Compute the Delta Regulatory potential upon In silico deletion of TF binding sites"""
import h5py
import os
import sys
import numpy as np
import pandas as pd
from pkg_resources import resource_filename

from .regpotential import regpotential
from . import Config

class EpigenomeData(object):
    """ interface for loading Lisa data with configuration file"""
    def __init__(self, species, epigenome):
        self.config = Config(resource_filename("lisa", "lisa.ini"), species)
        self.epigenome = epigenome

        self.own_data_h5 = None
        self.covariates_h5 = None

    @property
    def high_quality_ids(self):
        """ load ChiLin quality metrics and filter by cutoff
        """
        quality = pd.read_csv(self.config.get_meta, encoding="ISO-8859-1")
        selector = (quality['UniquelyMappedRatio'] > 0.4) \
                 & (quality['MappedReadsNumber'] > 4e6) \
                 & (quality['AllPeaksNumber'] > 1000) \
                 & (quality['PBC'] > 0.7) \
                 & (quality['FactorName'] == self.epigenome)
        sids = quality.ix[selector, 'X']
        # print(sids.shape)
        return list(set(map(str, list(sids))))

    @property
    def get_intersect_ids(self):
        high_quality_ids = self.high_quality_ids
        count_ids = self.get_count(None, None, None)
        high_quality_ids = list(set(high_quality_ids) & set(count_ids))
        return high_quality_ids

    def get_sample_annotation(self, ids, TF=False):
        """get samples tissue, cell type annotation
        ids: DC ids
        TF: TF ChIP-seq or epigenome ChIP-seq
        """
        if not TF:
            #print(ids)
            meta = pd.read_csv(self.config.get_meta, encoding="ISO-8859-1", index_col=0)
            meta.index = meta.index.astype('str')
            return meta.ix[ids, 3:6]
        else:
            return

    def create_RP_h5(self, bigwig, prefix):
        """ create hdf5 from text file for regulatory potential
        """
        output = '%s.%s.%s.reg_potential' % (bigwig, prefix, self.epigenome)
        regpotential.getrp(bigwig, self.config.get_tss_refseq,
                           "%s.txt" % output,
                           1e4, 0, 0)
        gene_rp, refseq = [], []

        with open("%s.txt" % output) as inf:
            for line in inf:
                line = line.split()
                refseq.append(str.encode(':'.join(line[:4]), 'utf-8'))
                gene_rp.append(float(line[4].strip()))
        with h5py.File("%s.h5" % output, 'a') as store:
            refseq_arr = store.create_dataset("RefSeq",
                                              shape=(len(gene_rp), ),
                                              dtype='S200',
                                              compression='gzip',
                                              shuffle=True, fletcher32=True)
            refseq_arr[...] = np.array(refseq)
            ids = store.create_dataset("IDs",
                                       shape=(1, ), dtype='S50',
                                       compression='gzip', shuffle=True, fletcher32=True)
            ids[...] = np.array(str.encode(bigwig, 'utf-8'))
            store.flush()
            reg_potential = store.create_dataset("RP", dtype=np.float32,
                                                 shape=(len(gene_rp), 1),
                                                 compression='gzip',
                                                 shuffle=True, fletcher32=True)
            reg_potential[:, 0] = np.array(gene_rp, dtype=np.float32)
            store.flush()

    @property
    def get_RP(self):
        """ loading hdf5 data of regulatory potential
        epigenome: a epigenome type
        species: mm10 or hg38
        return: pandas DataFrame, column is sample ids, index is gene symbol
        """
        high_quality_ids = self.get_intersect_ids
        h5 = self.config.get_rp(self.epigenome)
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

    @property
    def get_covariates_reg(self):
        """ get GC Covaraites of regulatory potential to build the model
        """
        h5 = self.config.get_rp('GC')
        with h5py.File(h5) as store:
            gene_annotation = np.array(list(map(lambda x: x.decode('utf-8'),
                                                store['RefSeq'][...])))
            return pd.DataFrame(store['RP'][:, 0], columns=['GC'],
                                index=gene_annotation)

    @property
    def gc_covariates_count(self):
        """ get GC Covaraites
        """
        hdf5 = self.config.genome_count('GC')
        with h5py.File(hdf5) as store:
            return store['OrderCount'][:, 0]

    def get_count(self, selected_ids, covariates, new_h5_count, only_newh5=False, selected_bins=[]):
        """ loading hdf5 data of 1kb read count 
        add sorted selected_bins list for faster IO loading
        """
        hdf5 = self.config.genome_count(self.epigenome)
        if new_h5_count != None: # add hdf5 from fastqs or bigwigs for read count
            with h5py.File(new_h5_count) as st:
                eids = np.array(list(map(lambda x: x.decode('utf-8'), st["IDs"][...])))

        with h5py.File(hdf5, mode='r') as store:
            ids = np.array(list(map(lambda x: x.decode('utf-8').split('_')[0],
                                    store['IDs'][...])))
            if not isinstance(selected_ids, list):
                return ids

            print(ids)
            count = np.zeros((store['OrderCount'].shape[0],
                              len(list(selected_ids))), dtype=np.float32)
            print(count.shape)
            for i, sid in enumerate(selected_ids):
                print(i, sid)
                print(type(sid))
                if covariates and sid == 'GC':
                    val = self.gc_covariates_count
                    count[:, i] = val
                    continue
                if sid != 'GC':
                    if not only_newh5:
                        index, = np.where(ids == sid) # n x 1 dimension array, may cause assign error for `count[:, i]`
                    else:
                        index = []
                    if len(index) != 0:
                        index = index[0]              # fix by using the first one
                        print(index)
                        if len(selected_bins) == 0:
                            val = store['OrderCount'][:, index]
                            count[:, i] = val
                        else:
                            val = store['OrderCount'][selected_bins, index]   ## selected_bins should be sorted in ascending order
                            count[selected_bins, i] = val
                        print(val.shape)
                    else: # search hdf5
                        if new_h5_count != None: # add hdf5 from fastqs or bigwigs for read count
                            index, = np.where(eids == sid)
                            with h5py.File(new_h5_count) as st:
                                if len(index) != 0:
                                    index = index[0]              # fix by using the first one
                                    print(index)
                                    val = store['OrderCount'][:, index]
                                    print(val.shape)
                                    count[:, i] = val
                                else: # not found read count ....
                                    print('not found samples in matching samples in read count hdf5')
                                    sys.exit(1)
        return count

    def create_Count_h5(self, bigwig, prefix):
        """ create 1kb read count hdf5 from sample bigwig file
        """
        output = '%s.%s.%s.1kb_read_count' % (bigwig, prefix, self.epigenome)
        os.system("""bigWigAverageOverBed {0} {1} {2}.tab
        cut -f 6 {2}.tab > {2}.value
        cut -f 1 {2}.tab > {2}.index""".format(bigwig, self.config.genome_window, output))

        i = np.loadtxt('{0}.index'.format(output), dtype='int32')-1
        count = np.loadtxt('{0}.value'.format(output), dtype='float32')
        count = count[np.argsort(i)]
        with h5py.File("%s.h5" % output, "a") as store:
            ids = store.create_dataset("IDs", shape=(1, ),
                                       dtype='S50',
                                       compression='gzip', shuffle=True, fletcher32=True)
            ids[...] = np.array(str.encode(bigwig, 'utf-8'))
            count_h5 = store.create_dataset("OrderCount",
                                            dtype=np.float32,
                                            shape=(count.shape[0], 1),
                                            compression='gzip', shuffle=True, fletcher32=True)
            count_h5[:,0] = count
            store.flush()

    @property
    def get_gene_tss_bin(self):
        """ genes: a list of gene annotation, e.g. ['CHR1:1:1000:NM_XXXXX:ABC']
        """
        tss_bin_annotation = self.config.get_annotation
        ann = {}
        with open(tss_bin_annotation) as fin:
            for line in fin:
                line = line.strip().split()
                center = (int(line[-2]) + int(line[-3])) // 2
                bin_index = int(line[-1]) - 1
                # refseq => center cooridinates, 0-based bin index
                ann[':'.join(line[:4])] = (center, bin_index)
        return ann

    @property
    def chrom_boundary_bin(self):
        """ get chromatin boundary bin
        """
        chrom_bin = {}
        with open(self.config.genome_window) as inf:
            for line in inf:
                line = line.strip().split()
                chrom_bin[line[0]] = int(line[-1])-1
        return chrom_bin

    def get_chr_boundary_mask(self, chrs):
        """ for a list of chromosome, get their boundary
        """
        chrom_bin = self.chrom_boundary_bin
        return np.array([chrom_bin[c] for c in chrs])

    def get_beta(self, genes):
        """ get beta score for all TF ChIP-seq data
        get foreground and background gene TF RP
        """
        with h5py.File(self.config.get_beta) as store:
            #ids = np.array(list(map(lambda x: x.decode('utf-8').split('_')[0],
            #                        store['IDs'][...])))
            ids = np.array(list(map(lambda x: x.decode('utf-8'),
                                    store['IDs'][...])))
            gene_annotation = np.array(list(map(lambda x: x.decode('utf-8'),
                                                store['RefSeq'][...])))
            df = pd.DataFrame(store['RP'][...], index=gene_annotation, columns=ids)
            return df.loc[genes, :]

    @property
    def get_cluster_median(self):
        """ get cluster for the 7 cluster for each of the marks """
        folder = self.config.get_cluster
        f = os.path.join(folder, '%s_median_for_each_cluster.h5' % self.epigenome)
        with h5py.File(f) as store:
            vals = store['median_log2RP_minus_1'][...].T
            clusters = store['K_means_cluster_index'][...]
            gene_annotation = np.array(list(map(lambda x: x.decode('utf-8'),
                                                store['RefSeq'][...])))
        return pd.DataFrame(vals, columns=clusters,
                            index=gene_annotation)
