### Installation

#### Mac

``` bash
brew install openssl
export C_INCLUDE_PATH=${C_INCLUDE_PATH}:/usr/local/Cellar/openssl/your_version/include
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/Cellar/openssl/your_version/lib/"
```

#### Linux
``` bash
sudo apt-get install openssl
```

#### Install conda python 3.6

Follow the instruction: https://conda.io/miniconda.html to install python 3.6

``` bash
wget -c https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

#### other dependency

``` bash
conda install anaconda-client
conda create -n lisa anaconda python=3
source activate lisa
pip install theano
```

### Install the module using:

``` bash
python setup.py install
```

#### Start to use

``` bash
lisa model --species hg38 --epigenome '['H3K4me3','H3K27ac','H3K4me1','DNase']' --cluster=True --covariates=True --prefix test --threads 12 AR.symbol ESR1.symbol
```


#### Output instructions

Take *AR.symbol* input and histone mark *H3K4me3* as an example. By using the above command, the key results are as follows, 

| Output File        | Content           | Instruction  |
| ------------- |:-------------:| -----:|
| AR.symbol.premodel_records.txt | regulatory potential cluster-based regression performance and coefficients |  one row is PRAUC,AUC,lambda, 2nd row is coefficients | 
| AR.symbol_motif99_baseline.csv | baseline method based on motif hits between differential gene and control gene | one row is motif_id|TF_name,p-value  | 
| AR.symbol_chipseq_baseline.csv | baseline method based on chip-seq peak number between differential gene and control gene | one row is CistromeID|TF_name,p-value |
| AR.symbol.gene_symbol.H3K4me3.coefs.csv     | Regression coefficients for H3K4me3 | one row is CistromeID,coefficient,cell type, cell line, tissue | 
| AR.symbol.H3K4me3.lisa_predicted_rp.csv | predicted differential expression log probability    |  one row is refseq,log probability |
| AR.symbol.H3K4me3.gene_set.performance | differential gene prediction | one row is AUC,PRAUC|
| AR.symbol.lisa_direct.csv |BETA TF ranks based on random background or epigenetic background |one row is CistromeID|TF_name,p_value|
| AR.symbol.gene_symbol.H3K4me3.motif99.p_value.csv     | motif insilco knockout result for H3K4me3 | one row is motif_id|TF_name,p-value |
| AR.symbol.H3K4me3.chipseq.p_value.csv | TF ChIP-seq insilco knockout result for H3K4me3 | one row is motif_id|TF_name,p-value |
| AR.symbol.gene_symbol.H3K4me3.motif99.entropy_rank.csv      | motif-based TF ranks from KL divergence method  |   one row is  motif_id|TF_name,KLD,rank|
| AR.symbol.gene_symbol.H3K4me3.chipseq.entropy_rank.csv      | ChIP-seq-based TF ranks from KL divergence method  |   one row is  motif_id|TF_name,KLD,rank|

#### Issues
Genes in the gene set should not be less than 20.
