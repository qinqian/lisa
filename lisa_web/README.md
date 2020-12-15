* How to setup a local server for Lisa web application


- First setup a lisa command line conda environment with python3.6, see lisa1(https://github.com/qinqian/lisa) or lisa2(https://github.com/liulab-dfci/lisa2)

- Second setup a lisa_web conda environment with python2.7
 
  a. If you have global flask installed, please uninstall that version
  
  b. setup environment
  ```sh
  git clone https://github.com/qinqian/lisa
  cd lisa/lisa_web
  conda create -n lisa_web python=2.7
  conda activate lisa_web
  pip install -r lisa_web_requirement.txt
  mkdir -p upload 
  mkdir -p download
  ```
  
  c. Start a new terminal session to run redis by `bash run-redis.sh`, this needs `gcc` and `g++` to compile the redis code.
  
  d. Start another teminal session to run celery by `bash run_celery.sh`
  
  e. Start a third terminal session to run the web server by `gunicorn --pythonpath . lisa_web:app --timeout 300`
  
  f. change the necessary harcoded paths manually to your local paths
  
   * run_lisa.sh and run_lisa2.sh: 
       1. 4th line: conda activate your lisa command line conda environment 
   * The main interface lisa_web/__init__.py:
       1. 37th line dir_prefix: CHANGE THIS TO your local lisa_web lib PATH
   * Files should be refactored to the output of lisa2 command line.
       1. calling lisa command line at 206th line for two gene sets, and parse the results
          a) parse progress percentage at 208th line
          b) parse the hard-coded lisa output csv file names at lines 256th-263th and lines 272-273th, this should be changed to the new version lisa output file names.
          c) generate figure at 264th line and 274th line and parse logs at lines 266th and 276th
          d) package all results into zip and send email at 282th to 283th lines, change url to the new web site.
       2. call lisa command line at 292th line for one gene set, and parse results 
          a) parse the progress percentage at 294th line
          b) parse the hard-coded lisa output csv file at lines 314th to 321th
          c) package all results into zip at 325th line, and send email at 331th, change url to the new web site.
       3. One gene set output file download url path
          a) parse status of snakemake log at 369th line, change to new lisa output logs 
          b) download csv files at 394th to 395th and 419th to 420th line this is the json key to be updated to new version of lisa output file name
          c) download zip file at lines 396th and 421th 
       4. Two gene set output file download url path
          a) parse snakemake log at 435th line, change to new lisa output logs 
          b) download csv files at 461th to 464th lines, and 501th to 504th lines
          c) download zip files at 473th line and 508th line
          d) download figure of scatterplot at lines 465th to 467th, and 505th to 507th
       5. If no snakemake log is available for lisa2, consider the tqdm for generating the progress bar.

