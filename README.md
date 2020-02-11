### LISA

![](https://zenodo.org/badge/DOI/10.5281/zenodo.3583466.svg)
![](https://anaconda.org/qinqian/lisa/badges/version.svg)
![](https://anaconda.org/qinqian/lisa_minimal/badges/license.svg)

Web version and documentation is hosted at http://lisa.cistrome.org. For large scale gene set analysis, we recommend user to install local version.

### Preparation of Anaconda environment

``` sh
wget -c https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
export PATH="${HOME}/miniconda3/bin:$PATH"

conda create -n lisa python=3.6 && conda config --add channels conda-forge && conda config --add channels bioconda

```

### Installation

``` sh
conda activate lisa
# or for old conda
source activate lisa
export MKL_THREADING_LAYER=GNU

conda install -c qinqian lisa
```

Another minimal version without preprocessing fastq to hdf5 can be installed with, 

```
conda install -c qinqian lisa_minimal
```

### Update package

use `git clone https://github.com/qinqian/lisa && cd lisa && python setup.py develop`.

### Get pre-computed datasets from CistromeDB

User can download hg38 or mm10 datasets based on their experiments for human or mouse, the password can be obtained after LISA is published.

``` sh
wget -c http://lisa.cistrome.org/cistromedb_data/lisa_v1.2_hg38.tar.gz

# or

wget -c http://lisa.cistrome.org/cistromedb_data/lisa_v1.2_mm10.tar.gz
```

Then, user need to uncompress the datasets, and update the configuration for lisa. 

``` sh
tar xvfz lisa_v1.2_hg38.tar.gz
lisa_update_conf --folder hg38/ --species hg38

# or

tar xvfz lisa_v1.2_mm10.tar.gz
lisa_update_conf --folder mm10/ --species mm10
```

### Usage

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

### Update LISA

``` sh
git clone http://github.com/qinqian/lisa/
source activate lisa
cd lisa && python setup.py develop
lisa_update_conf --folder hg38/ --species hg38
lisa_update_conf --folder mm10/ --species mm10
```

### Remove LISA

``` sh
conda env remove -n lisa
rm -r mm10/ hg38/
```

### Preprocessing datasets

This [repository](https://bitbucket.org/Alvin_Qin/marge2/src/default/) includes scripts for preprocessing CistromeDB datasets, includes Peak-RP and Chrom-RP.

### Citation 

Please note that the reference is a preprint hosted at [biorxiv](https://www.biorxiv.org/content/10.1101/846139v1),
Qin Q, Fan J, Zheng R, Wan C, Mei S, Wu Q, et al. Inferring transcriptional regulators through integrative modeling of public chromatin accessibility and ChIP-seq data. 2019.

Now Lisa is online at Genome biology, Qin Q, Fan J, Zheng R, Wan C, Mei S, Wu Q, et al. [Inferring transcriptional regulators through integrative modeling of public chromatin accessibility and ChIP-seq data. Genome Biology;(2020)21:32](https://rdcu.be/b1nyZ)

