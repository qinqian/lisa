### LISA
Web version and documentation is hosted at http://lisa.cistrome.org.

### Preparation of Anaconda environment
wget -c https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
export PATH="${HOME}/miniconda3/bin:$PATH"
conda create -n lisa python=3.6 && conda config --add channels conda-forge && conda config --add channels bioconda
conda activate lisa

### Installation
conda install -c qinqian lisa 

### Remove LISA
conda env remove -n lisa

### LICENSE
LISA is freely available for non-commercial use. If you may use it for a
commercial application, please inquire at qinqian89@outlook.com. By
downloading the software you agree to the following EULA.

End User License Agreement (EULA)
Your access to and use of the downloadable code (the 'Code') for LISA is
subject to a non-exclusive, revocable, non-transferable, and limited right to
use the Code for the exclusive purpose of undertaking academic, governmental,
or not-for-profit research. Use of the Code or any part thereof for commercial
or clinical purposes is strictly prohibited in the absence of a Commercial
License Agreement from Qian Qin.

