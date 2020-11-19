* How to setup a local server for Lisa web application


- First install lisa command line version in the conda environment with python3.6

- Second setup a python2.7 conda environment


0. git clone https://github.com/qinqian/lisa
1. cd lisa/lisa_web
2. conda create -n lisa_web python=2.7
3. pip install -r lisa_web_requirement.txt, if you have global flask installed, please uninstall that version
4. The simplest local test server I found is to use gunicorn, pip install gunicorn and gunicorn --pythonpath . lisa_web:app --timeout 300
5. start redis by bash run-redis.sh, this needs gcc and g++ to compile the redis code.
6. start celery by bash run_celery.sh
7. change all harcoded paths to your local paths
   * check_genename.py: 
       1. download the reference annotation from iris server
       2. change 22th and 24th ensemble to the downloaded file paths
   * run_lisa.sh and run_lisa2.sh: 
       1. 3th line: conda activate your lisa command line environment 
       2. 6th and 7th line: change upload directory for users gene set
       3. 13th line: snakemake log file for displaying the progress percentage on html pages
   * The main interface lisa_web/__init__.py:
       1. 37th line dir_prefix
       2. mkdir for all path from 40th to 44th lines
       3. calling lisa command line at 206th line for two gene sets, and parse the results
          a) parse progress percentage at 208th line
          b) parse the hard-coded lisa output csv file names at lines 256th-263th and lines 272-273th, this should be changed to the new version lisa output file names.
          c) generate figure at 264th line and 274th line and parse logs at lines 266th and 276th
          d) package all results into zip and send email at 282th to 283th lines, change url to the new web site.
       6. call lisa command line at 292th line for one gene set, and parse results 
          a) parse the progress percentage at 294th line
          b) parse the hard-coded lisa output csv file at lines 314th to 321th
          c) package all results into zip at 325th line, and send email at 331th, change url to the new web site.
       7. One gene set output file download url path
          a) parse status of snakemake log at 369th line, change to new lisa output logs 
          b) download csv files at 394th to 395th and 419th to 420th line this is the json key to be updated to new version of lisa output file name
          c) download zip file at lines 396th and 421th 
       8. Two gene set output file download url path
          a) parse snakemake log at 435th line, change to new lisa output logs 
          b) download csv files at 461th to 464th lines, and 501th to 504th lines
          c) download zip files at 473th line and 508th line
          d) download figure of scatterplot at lines 465th to 467th, and 505th to 507th
