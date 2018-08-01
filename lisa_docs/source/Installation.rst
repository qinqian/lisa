Installation
===============

Mac
---------

.. code-block:: bash
   :linenos:

   brew install openssl
   export C_INCLUDE_PATH=${C_INCLUDE_PATH}:/usr/local/Cellar/openssl/your_version/include
   export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/Cellar/openssl/your_version/lib/"

Linux
---------

.. code-block:: bash
   :linenos:

   sudo apt-get install openssl

Install conda python 3.6
~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow the instruction: https://conda.io/miniconda.html to install python 3.6.

other dependency
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash
   :linenos:

   wget -c https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh

.. code-block:: bash
   :linenos:

   # install miniconda3
   export PATH="${HOME}/miniconda3/bin:$PATH"
   conda install anaconda-client
   conda create -n lisa anaconda python=3
   source activate lisa
   conda install -c anaconda openssl
   conda install -c anaconda curl

   conda config --add channels defaults
   conda config --add channels conda-forge
   conda config --add channels bioconda
   conda install blas mkl-service

   # this is for curl and openssl header files
   export C_INCLUDE_PATH=${C_INCLUDE_PATH}:/usr/include/:${HOME}/.local/include:${HOME}/miniconda3/envs/lisa/include
   
   pip install deeptools
   pip install theano
   pip install fire
   pip install psutil
   pip install numpy
   pip install scipy
   pip install sklearn


Install the module using:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash
   :linenos:
 
   git clone https://github.com/qinqian/lisa
   cd lisa
   python setup.py install --user


Get dependent data
~~~~~~~~~~~~~~~~~~~~~~~~~
The related chromatin profile dataset will be released later, use LISA_ now.

.. _LISA: http://lisa.cistrome.org
