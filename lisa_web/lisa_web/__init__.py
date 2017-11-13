import logging
import os, sys
import subprocess
from logging.handlers import RotatingFileHandler
import time
import numpy as np
import pandas as pd
import re

from flask import Flask, render_template, redirect, url_for, send_from_directory, abort, jsonify
from flask import request
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from celery import Celery
import random
from flask import flash


# initialize an application
app = Flask(__name__, instance_relative_config = True)


app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

from .form import LISAForm


app.secret_key = 's3cr3t' # crsf
download = '/data/home/qqin/lisa_web/download'
upload = '/data/home/qqin/lisa_web/upload'

# debug mode on
app.debug = False
if not app.debug:
    app.logger.setLevel(logging.INFO)
    handler = RotatingFileHandler('/data/home/qqin/lisa_web/lisa.log', maxBytes=10000000, backupCount=20)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

@app.errorhandler(500)
def internal_error(exception):
    app.logger.exception(exception)
    return "Sorry internal program error", 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def submit_lisa():
    form = LISAForm()
    app.logger.info(form.validate_on_submit())
    if form.validate_on_submit():
        genes = form.genes.data
        job_name = form.name.data
        species = form.species.data.encode('utf-8')
        marks = form.mark.data.encode('utf-8')

        app.logger.info("%s %s %s at %s" % (str(genes), marks, species, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        label = round(random.random(), 3)
        prefix = "%s_%s" % (job_name, secure_filename(time.strftime('%Y_%m_%d %H:%M:%S', time.localtime())) + str(label))
        app.logger.info("%s %s %s at %s from %s" % (str(genes), marks, species, prefix,
                                                    request.remote_addr))
        gsf = os.path.join(upload, '%s.txt' % prefix)
        gene_set = open(gsf, 'w')
        for i in genes.split('\n'):
            i = i.strip()
            print >>gene_set, i
        gene_set.close()

        target = os.path.join(download, "%s.chipseq.p_value.csv" % (prefix+'.txt'))
        app.logger.info(target)
        app.logger.info("%s lisa modeling finished %s" % (prefix, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
        task = run_lisa.apply_async(args=(species, marks, prefix), countdown=1, expires=3600)
        cc = render_template('display.html', epigenome=marks, task_id=prefix)
        with open('%s/%s%s' % (download, prefix, "_result.html"), 'w') as outf:
            outf.write(cc)
        #return render_template('display.html', epigenome=marks, task_id=prefix)
        return redirect('/download/%s_result.html'%prefix)
    return render_template('index.html', form = form)

@celery.task(bind=True)
def run_lisa(self, species, mark, prefix):
    # issues: chmod 777 of lisa2 anaconda library and lisa_web root directory
    # chmod 777 /var/www/.theano
    # is not a good idea...
    cmd = "/data/home/qqin/lisa_web/run_lisa.sh %s %s %s %s" % (species, str([mark]), prefix, "%s.txt" %  os.path.join(upload, prefix))
    app.logger.info(cmd)
    with open('/data/home/qqin/lisa_web/upload/%s_snakemake_output.txt' % prefix, 'a') as fout:
        p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
        out, err = p.communicate()
        fout.flush()
        app.logger.info(out)
        app.logger.info(err)

    chipp = '%s.txt.%s.chipseq.p_value.csv' % (prefix, mark)
    c = pd.read_csv(os.path.join(upload, chipp), header=None)
    m = pd.read_csv(os.path.join(upload, '%s.txt.%s.motif99.p_value.csv' % (prefix, mark)), header=None)
    d = pd.read_csv(os.path.join(upload, '%s.txt.lisa_direct.csv' % (prefix)), header=None)

    ch = get_collapse_tf(c, prefix, mark, 'chip.')
    mo = get_collapse_tf(m, prefix, mark, 'motif.')
    di = get_collapse_tf(d, prefix, 'direct', '')

    z=pd.read_csv(os.path.join(upload, '%s.txt.%s.coefs.csv' % (prefix, mark)))
    z.columns = ['id', 'coefficients', 'cell_type', 'cell_line', 'tissue']
    z.coefficients = z.coefficients.map(lambda x: "%.2E" % x)

    z.to_csv(os.path.join(upload, '%s.%s.coefs.csv' % (prefix, mark)), index=False)

    cmd = "/data/home/qqin/lisa_web/run_browser.sh %s %s %s" % ('%s.txt.%s.coefs.csv' % (prefix, mark), chipp, '%s.txt.foreground_gene' % prefix)
    app.logger.info(cmd)
    os.system(cmd)

def get_collapse_tf(z, prefix, mark, t):
    a = {}
    p = {}
    z = z.sort_values(1) # pick the top five ones
    for i in range(z.shape[0]):
        a[z.iloc[i, 0].split('|')[1]] = a.get(z.iloc[i, 0].split('|')[1], []) + [z.iloc[i,0].split('|')[0]]
        p[z.iloc[i, 0].split('|')[1]] = min(p.get(z.iloc[i, 0].split('|')[1],1000), z.iloc[i,1])

    out = os.path.join(upload, "%s.%s.%scsv" % (prefix, mark, t))
    with open(out, 'w') as fout:
        fout.write("%s,%s,%s\n" % ("TF", "ID", "p"))
        for j in p:
            fout.write("%s,%s,%s\n" % (j, " | ".join(a[j][:5]), p[j])) # pick the top five ones

    z = pd.read_csv(out)
    z = z.sort_values('p')
    z.p = z.p.map(lambda x: "%.2E" % x)
    z.to_csv(out, index=False)
    return out

@app.route('/lisa_status/<epigenome>/<task_id>', methods=['GET', 'POST'])
def lisa_taskstatus(epigenome, task_id):
    # external process do not record state in celery task
    # task = long_task.AsyncResult(task_id)

    # parse snakemake log to get the state
    snakelogs = os.path.join(upload, '%s_snakemake_output.txt' % task_id)
    response = {}
    response['status'] = '0%'
    response['state'] = 'PENDING'

    if not os.path.exists(snakelogs):
        return jsonify(response)
    with open(snakelogs) as fin:
        loglist = fin.readlines()
        if len(loglist) <= 10:
            return jsonify(response)

        loglist = loglist[::-1]
        for l in loglist:
            if 'steps' in l:
                response['state'] = 'PROGRESS'
                f = re.findall('(\d*)\%', l)
                if len(f) == 1:
                    f = int(f[0])
                    if f == 100:
                        response['state'] = 'Taskcompleted'
                        response['status'] = '100%'
                        response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct.csv' % (task_id))
                        response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs.csv' % (task_id, epigenome))
                        response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip.csv" % (task_id, epigenome))
                        response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif.csv" % (task_id, epigenome))
                        ## upload/2017_10_12_2213360.84006.txt.H3K27ac.url
                        ## http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/upload/2017_10_12_2223360.31016.txt.H3K27ac.url&gftk=refGene,full
                        response['resultl'] = "http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"

                        # upload/2017-08-17_0759290.51314.txt.H3K27ac.chipseq.p_value.csv
                    else:
                        response['state'] = 'PROGRESS'
                        response['status'] = "{0}%".format(str(f))
                    return jsonify(response)
            elif 'failed' in l:
                response['state'] = 'Failed, check option and input'
                response['status'] = '0%'
    return jsonify(response)


@app.route('/upload/<path:filename>')
def custom_upload(filename):
    return send_from_directory(upload, filename)

# add new static folder
@app.route('/download/<path:filename>')
def custom_download(filename):
    return send_from_directory(download, filename)

Bootstrap(app)
