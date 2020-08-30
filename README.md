### LISA

![](https://zenodo.org/badge/DOI/10.5281/zenodo.3583466.svg)
![](https://anaconda.org/qinqian/lisa/badges/version.svg)
![](https://anaconda.org/qinqian/lisa_minimal/badges/license.svg)

Web version and documentation is hosted at http://lisa.cistrome.org. For large scale gene set analysis, we recommend user to install local version, only OSX and Linux system have been tested. 

### Preparation of Anaconda environment and Installation

``` sh
wget -c https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
export PATH="${HOME}/miniconda3/bin:$PATH"

conda config --add channels defaults && conda config --add channels conda-forge && conda config --add channels bioconda && conda install mamba -c conda-forge && mamba create -n lisa -c qinqian lisa_minimal python=3.6.6

#or 

conda config --add channels defaults && conda config --add channels conda-forge && conda config --add channels bioconda && conda install mamba -c conda-forge && mamba create -n lisa -c qinqian lisa=1.0 python=3.6.6

export MKL_THREADING_LAYER=GNU

```

### Update package

use `git clone https://github.com/qinqian/lisa && cd lisa && python setup.py develop`.

### Get pre-computed datasets from CistromeDB

User can download hg38 or mm10 datasets based on their experiments for human or mouse.

``` sh
wget -c http://lisa.cistrome.org/cistromedb_data/lisa_v1.2_hg38.tar.gz

# or

wget -c http://lisa.cistrome.org/cistromedb_data/lisa_v1.2_mm10.tar.gz
```

Then, user need to uncompress the datasets, and update the configuration for lisa. 

``` sh
tar xvfz lisa_v1.2_hg38.tar.gz
lisa_update_conf --folder absolute_path_hg38/ --species hg38

# or

tar xvfz lisa_v1.2_mm10.tar.gz
lisa_update_conf --folder absolute_path_mm10/ --species mm10
```

### Usage

First, activate the conda environment:

``` sh
conda activate lisa_minimal

# or 

conda activate lisa
```

Given multiple gene set file `gene_set1`, `gene_set2`, `gene_set3` et al., each file has one gene (RefSeq id or gene symbol) for each row, user can predict transcriptional regulator ranking using the following commands with random background genes

``` sh 
time lisa model --clean=True --method="all" --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome "['DNase', 'H3K27ac']" --cluster=False --covariates=False --random=True --prefix first_run --background=None --stat_background_number=1000 --threads 4 gene_set1 gene_set2 gene_set3 ...
```

Alternatively, user can generate a fixed background genes based on TAD and promoter activity, and input it to lisa,

``` sh
lisa_premodel_background_selection --species hg38 --epigenomes="['DNase']" --gene_set=None --prefix=test --random=None --background=dynamic_auto_tad
cut -f 5 -d: test.background_gene.3000 > test.fixed.background_gene

time lisa model --clean=True --method="all" --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome "['DNase', 'H3K27ac']" --cluster=False --covariates=False --random=True --prefix first_run --background=test.fixed.background_gene --stat_background_number=1000 --threads 4 gene_set1 gene_set2 gene_set3 ...
```

User can also input a customized background genes, which should include more than 30 unique RefSeq genes, all input genes are used for modeling and computing statistics, so `--stat_background_number` is ignored.

``` sh
time lisa model --method="all" --clean=True --web=True --new_rp_h5=None --new_count_h5=None --species hg38 --epigenome "['DNase', 'H3K27ac']" --cluster=False --covariates=False --random=True --prefix first_run --background=test.fixed.background_gene --threads 4 gene_set1 gene_set2 gene_set3 ...
```

### Uninstall LISA

``` sh
conda env remove -n lisa

or 

conda env remove -n lisa_minimal

rm -r absolute_path_mm10/ absolute_path_hg38/
```

### Preprocessing datasets to update the database

This [repository](https://bitbucket.org/Alvin_Qin/marge2/src/default/) includes scripts for preprocessing CistromeDB datasets, includes Peak-RP and Chrom-RP.


### Troubleshooting

Sometimes the numpy and pandas would have conflicts version after installation of Lisa, the way to fix that is to uninstall both numpy and pandas, and reinstall the fixed versions of the two packages, these versions include: numpy 1.15.4 with pandas 0.23.4 (thanks @ChangliangWang), numpy 1.15.1 with pandas 0.25.2, numpy 1.15.1 with pandas 1.0.5, numpy 1.17.2 with pandas 1.0.5.

### Citation 

Now Lisa is online at Genome biology, Qin Q, Fan J, Zheng R, Wan C, Mei S, Wu Q, et al. [Inferring transcriptional regulators through integrative modeling of public chromatin accessibility and ChIP-seq data. Genome Biology;(2020)21:32](https://rdcu.be/b1nyZ)

