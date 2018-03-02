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

   conda install anaconda-client
   conda create -n lisa anaconda python=3
   source activate lisa
   pip install theano

.. code-block:: bash
   :linenos:

   wget -c https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh


Install the module using:
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash
   :linenos:
 
   git clone https://github.com/qinqian/lisa
   cd lisa
   python setup.py install

