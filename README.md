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
lisa model --species hg38 --epigenome '['H3K4me3','H3K27ac','H3K4me1','DNase']'  --cluster=False --covariates=False --prefix test AR.symbol ESR1.symbol
```
