Tutorial
=============

LISA is used to link chromatin profile to gene set from any stimuls experiment of gene expression, the input is a gene set, the output is the ranking of the transcription factor, it is based on the large-scale dataset from Cistrome database. User can use the online version or local standalone version.

LISA includes 4 methods: In silico knockout (the best), cluster method, BETA method, baseline method. Only knockout and BETA methods are supported for online version. For users with gene set more than 200, consider install the local version.


Standalone version
~~~~~~~~~~~~~~~~~~~~

The LISA framework has three pipeline represented with three sub-parser, `model`, `multiple_fastq2bigwig`, and `multiple_bigwig2hdf`;
The TF rank method is run through the `model` sub-parser.

Run all the methods
------------------------

.. code-block:: bash
   :linenos:

   lisa model --method='all' --web=False --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome "['H3K27ac']" --cluster=True --covariates=False --random=True --prefix test_function1 --threads 8 test.gene_symbol

Options:
The `test.gene_symbol` is the gene set user input, which is a text file with one official gene symbol or refseq id, mixture of the both is not supported yet, this is used as a prefix for output, so put the file in a directory with written permission.

--epigenome controls the histone mark or DNase to use in the features.

Run only one method
-------------------------------------
1. run only the knockout or beta method:
   --method option can control the method to run knockout or beta method, use it with the option --web=True to turn off the baseline method.

.. code-block:: bash
   :linenos:

   lisa model --method='knockout' --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome "['H3K27ac']" --cluster=False --covariates=False --random=True --prefix test_function1 --threads 8 test.gene_symbol
   lisa model --method='beta' --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome "['H3K27ac']" --cluster=False --covariates=False --random=True --prefix test_function1 --threads 8 test.gene_symbol

2. run only the cluster method to rank

.. code-block:: bash
   :linenos:

   lisa model --method='none' --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome "['H3K27ac']" --cluster=True --covariates=False --random=True --prefix test_function1 --threads 8 test.gene_symbol

Understanding Output
---------------------
Take *AR.symbol* input and histone mark *H3K4me3* as an example. By using the above command, the key results are as follows,

=======================================================   ===============================================================================  =============================================================================
Output File                                               Content                                                                          Instruction
=======================================================   ===============================================================================  =============================================================================
AR.symbol.premodel_records.txt                            regulatory potential cluster-based regression performance and coefficients       one row is PRAUC,AUC,lambda, 2nd row is coefficients
AR.symbol_motif99_baseline.csv                            baseline method based on motif hit between differential & control gene           one row is motif_id|TF_name,p-value
AR.symbol_chipseq_baseline.csv                            baseline method based on chip-seq peak hit between differential & control gene   one row is CistromeID|TF_name,p-value
AR.symbol.gene_symbol.H3K4me3.coefs.csv                   Regression coefficients for H3K4me3                                              one row is CistromeID,coefficient,cell type, cell line, tissue
AR.symbol.H3K4me3.lisa_predicted_rp.csv                   predicted differential expression log probability                                one row is refseq,log probability
AR.symbol.H3K4me3.gene_set.performance                    differential gene prediction                                                     one row is AUC,PRAUC
AR.symbol.lisa_direct.csv                                 BETA TF ranks based on random background or epigenetic background                one row is CistromeID|TF_name,p_value
AR.symbol.gene_symbol.H3K4me3.motif99.p_value.csv         motif insilco knockout result for H3K4me3                                        one row is motif_id|TF_name,p-value
AR.symbol.H3K4me3.chipseq.p_value.csv                     TF ChIP-seq insilco knockout result for H3K4me3                                  one row is motif_id|TF_name,p-value
AR.symbol.gene_symbol.H3K4me3.motif99.entropy_rank.csv    motif-based TF ranks from KL divergence method                                   one row is  motif_id|TF_name,KLD,rank
AR.symbol.gene_symbol.H3K4me3.chipseq.entropy_rank.csv    ChIP-seq-based TF ranks from KL divergence method                                one row is  motif_id|TF_name,KLD,rank|
=======================================================   ===============================================================================  =============================================================================

Web Version
~~~~~~~~~~~~~~~~~~~~~~
The web version is intuitive to use, just copy and paste a gene list (one row a gene), and submit your job. One hidden tip is that each p-value in the output table can be click to view the dataset information from Cistrome Data Browser.
