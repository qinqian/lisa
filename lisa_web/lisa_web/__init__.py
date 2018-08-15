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

from .mail import send_localhost_mail

# initialize an application
app = Flask(__name__, instance_relative_config = True)


app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

from .form import LISAForm


app.secret_key = 's3cr3t' # crsf
download = '/data/home/qqin/lisa_web/download'
gallery = '/data/home/qqin/lisa_web/lisa_web/gallery'
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
        to_user = form.mail.data

        genes = form.genes.data
        genes2 = form.genes2.data

        if genes2 == '':
            job_name = form.name.data
            method = form.method.data

            species = form.species.data.encode('utf-8')
            marks = form.mark.data.encode('utf-8')

            app.logger.info("%s %s %s at %s" % (str(genes), marks, species, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            label = round(random.random(), 3)
            prefix = "%s_%s" % (job_name, secure_filename(time.strftime('%Y_%m_%d %H:%M:%S', time.localtime())) + str(label))
            app.logger.info("%s %s %s at %s from %s" % (str(genes), marks, species, prefix,
                                                        request.remote_addr))
            gsf = os.path.join(upload, '%s.txt' % prefix)

            if len(genes.split('\n')) > 300:
                return render_template('index.html', form=form, message='inline-block')

            gene_set = open(gsf, 'w')
            for i in genes.split('\n'):
                i = i.strip().split(",") # comma is ok
                for j in i:
                    print >>gene_set, j
            gene_set.close()

            # target = os.path.join(download, "%s.chipseq.p_value.csv" % (prefix+'.txt'))
            # app.logger.info(target)
            app.logger.info("%s lisa modeling finished %s" % (prefix, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))

            task = run_lisa.apply_async(args=(method, species, marks, prefix, to_user), countdown=1, expires=3600)
            cc = render_template('display.html', epigenome=marks,
                                 task_id=prefix, method=method)
            with open('%s/%s%s' % (download, prefix, "_result.html"), 'w') as outf:
                outf.write(cc)
            #return render_template('display.html', epigenome=marks, task_id=prefix)
            return redirect('/download/%s_result.html'%prefix)
        else:
            if len(genes.split('\n')) > 300:
                return render_template('index.html', form=form, message='inline-block')
            if len(genes2.split('\n')) > 300:
                return render_template('index.html', form=form, message='inline-block')

            job_name = form.name.data
            method = form.method.data

            species = form.species.data.encode('utf-8')
            marks = form.mark.data.encode('utf-8')

            app.logger.info("%s %s %s at %s" % (str(genes), marks, species, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            label = round(random.random(), 3)

            prefix = "%s_%s" % (job_name, secure_filename(time.strftime('%Y_%m_%d %H:%M:%S', time.localtime())) + str(label))
            app.logger.info("%s %s %s at %s from %s" % (str(genes), marks, species, prefix,
                                                        request.remote_addr))
            gsf1 = os.path.join(upload, '%s_gs1.txt' % prefix)
            gene_set1 = open(gsf1, 'w')
            for i in genes.split('\n'):
                i = i.strip().split(",") # comma is ok
                for j in i:
                    print >>gene_set1, j
            gene_set1.close()

            gsf2 = os.path.join(upload, '%s_gs2.txt' % prefix)
            gene_set2 = open(gsf2, 'w')
            for i in genes2.split('\n'):
                i = i.strip().split(",") # comma is ok
                for j in i:
                    print >>gene_set2, j
            gene_set2.close()

            task = multiple_run_lisa.apply_async(args=(method, species, marks, prefix, to_user), countdown=1, expires=3600)

            cc = render_template('multiple_display.html', epigenome=marks,
                                 task_id=prefix, method=method)

            with open('%s/%s%s' % (download, prefix, "_result.html"), 'w') as outf:
                outf.write(cc)
            #return render_template('display.html', epigenome=marks, task_id=prefix)
            return redirect('/download/%s_result.html'%prefix)
            # return

    return render_template('index.html', form = form, message="none")

@celery.task(bind=True)
def multiple_run_lisa(self, method, species, mark, prefix, to_user):
    # issues: chmod 777 of lisa2 anaconda library and lisa_web root directory
    # chmod 777 /var/www/.theano
    # is not a good idea...
    cmd = "/data/home/qqin/lisa_web/run_lisa2.sh %s %s %s %s %s %s" % (species, str([mark]), prefix, str(method), "%s_gs1.txt" % os.path.join(upload, prefix), "%s_gs2.txt" %  os.path.join(upload, prefix))
    app.logger.info(cmd)
    with open('/data/home/qqin/lisa_web/upload/%s_snakemake_output.txt' % prefix, 'a') as fout:
        p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
        out, err = p.communicate()
        fout.flush()
        app.logger.info(out)
        app.logger.info(err)


    chipp1 = '%s_gs1.txt.%s.chipseq.p_value.csv' % (prefix, mark)
    chipp2 = '%s_gs2.txt.%s.chipseq.p_value.csv' % (prefix, mark)

    motif1 = '%s_gs1.txt.%s.motif99.p_value.csv' % (prefix, mark)
    motif2 = '%s_gs2.txt.%s.motif99.p_value.csv' % (prefix, mark)

    if method == 'all' or method == 'knockout':
        cmd = "/data/home/qqin/lisa_web/run_plot.sh %s %s %s_chip InSilicoChIP-seq" % (os.path.join(upload, chipp1), os.path.join(upload, chipp2), os.path.join(upload, prefix))
        app.logger.info(cmd)
        with open('/data/home/qqin/lisa_web/upload/%s_chip_plot_output.txt' % prefix, 'a') as fout:
            p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
            out, err = p.communicate()
            fout.flush()

        cmd = "/data/home/qqin/lisa_web/run_plot.sh %s %s %s_motif InSilicoMotif" % (os.path.join(upload, motif1), os.path.join(upload, motif2), os.path.join(upload, prefix))
        app.logger.info(cmd)
        with open('/data/home/qqin/lisa_web/upload/%s_motif_plot_output.txt' % prefix, 'a') as fout:
            p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
            out, err = p.communicate()
            fout.flush()

        c = pd.read_csv(os.path.join(upload, chipp1), header=None)
        m = pd.read_csv(os.path.join(upload, motif1), header=None)

        ch = get_collapse_tf(c, prefix, mark, 'chip1.')
        mo = get_collapse_tf(m, prefix, mark, 'motif1.')

        c = pd.read_csv(os.path.join(upload, chipp2), header=None)
        m = pd.read_csv(os.path.join(upload, motif2), header=None)

        ch = get_collapse_tf(c, prefix, mark, 'chip2.')
        mo = get_collapse_tf(m, prefix, mark, 'motif2.')

    if method == 'all' or method == 'beta':
        g1_beta = os.path.join(upload, '%s_gs1.txt.lisa_direct.csv' % (prefix))
        g2_beta = os.path.join(upload, '%s_gs2.txt.lisa_direct.csv' % (prefix))

        cmd = "/data/home/qqin/lisa_web/run_plot.sh %s %s %s_direct TFChIP-seq" % (g1_beta, g2_beta, os.path.join(upload, prefix))
        app.logger.info(cmd)
        with open('/data/home/qqin/lisa_web/upload/%s_direct_plot_output.txt' % prefix, 'a') as fout:
            p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
            out, err = p.communicate()
            fout.flush()

        d = pd.read_csv(g1_beta, header=None)
        di = get_collapse_tf(d, prefix, 'direct1', '')

        d = pd.read_csv(g2_beta, header=None)
        di = get_collapse_tf(d, prefix, 'direct2', '')

    z=pd.read_csv(os.path.join(upload, '%s_gs1.txt.%s.coefs.csv' % (prefix, mark)))
    z.columns = ['id', 'coefficients', 'cell_type', 'cell_line', 'tissue']
    z.coefficients = z.coefficients.map(lambda x: "%.2E" % x)
    z.loc[:, "coefficient"] = z.apply(lambda x: "%s|%s" % (x[0], x[1]), axis=1)

    z.loc[:, "download"] = ["http://lisa.cistrome.org/upload/%s_gs1.txt.%s.%s.csv"%(prefix, mark, i) for i in z.id]

    z.drop(["id", "coefficients"], axis=1, inplace=True)


    z.to_csv(os.path.join(upload, '%s.%s.coefs1.csv' % (prefix, mark)), index=False)

    z=pd.read_csv(os.path.join(upload, '%s_gs2.txt.%s.coefs.csv' % (prefix, mark)))
    z.columns = ['id', 'coefficients', 'cell_type', 'cell_line', 'tissue']
    z.coefficients = z.coefficients.map(lambda x: "%.2E" % x)
    z.loc[:, "coefficient"] = z.apply(lambda x: "%s|%s" % (x[0], x[1]), axis=1)

    z.loc[:, "download"] = ["http://lisa.cistrome.org/upload/%s_gs2.txt.%s.%s.csv"%(prefix, mark, i) for i in z.id]

    z.drop(["id", "coefficients"], axis=1, inplace=True)
    z.to_csv(os.path.join(upload, '%s.%s.coefs2.csv' % (prefix, mark)), index=False)

    if method == 'all' or method == 'knockout':
        ## recovery by setting Require not ip in apache
        cmd = "/data/home/qqin/lisa_web/run_browser.sh %s %s %s" % ('%s_gs1.txt.%s.coefs.csv' % (prefix, mark), chipp1, '%s_gs1.txt.foreground_gene' % prefix)
        app.logger.info(cmd)
        os.system(cmd)

        cmd = "/data/home/qqin/lisa_web/run_browser.sh %s %s %s" % ('%s_gs2.txt.%s.coefs.csv' % (prefix, mark), chipp2, '%s_gs2.txt.foreground_gene' % prefix)
        app.logger.info(cmd)
        os.system(cmd)

    # upload/AR12_2017_11_12_0017060.299.txt.DNase.chipseq.csv
    ## turn off the heatmap
    # cmd = "/data/home/qqin/lisa_web/run_heatmap.sh %s" % (os.path.join(upload, '%s.txt.%s.chipseq.csv' % (prefix, mark)))
    # app.logger.info(cmd)
    # os.system(cmd)
    send_localhost_mail('html', 'LISA Result', to_user, 'Hi %s, the LISA results is ready at http://lisa.cistrome.org/download/%s_result.html.' % (to_user.split('@')[0], prefix), '')

@celery.task(bind=True)
def run_lisa(self, method, species, mark, prefix, to_user):
    # issues: chmod 777 of lisa2 anaconda library and lisa_web root directory
    # chmod 777 /var/www/.theano
    # is not a good idea...
    cmd = "/data/home/qqin/lisa_web/run_lisa.sh %s %s %s %s %s" % (species, str([mark]), prefix, "%s.txt" %  os.path.join(upload, prefix), str(method))
    app.logger.info(cmd)
    with open('/data/home/qqin/lisa_web/upload/%s_snakemake_output.txt' % prefix, 'a') as fout:
        p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
        out, err = p.communicate()
        fout.flush()
        app.logger.info(out)
        app.logger.info(err)

    chipp = '%s.txt.%s.chipseq.p_value.csv' % (prefix, mark)

    if method == 'all' or method == 'knockout':
        c = pd.read_csv(os.path.join(upload, chipp), header=None)
        m = pd.read_csv(os.path.join(upload, '%s.txt.%s.motif99.p_value.csv' % (prefix, mark)), header=None)
        ch = get_collapse_tf(c, prefix, mark, 'chip.')
        mo = get_collapse_tf(m, prefix, mark, 'motif.')

    if method == 'all' or method == 'beta':
        d = pd.read_csv(os.path.join(upload, '%s.txt.lisa_direct.csv' % (prefix)), header=None)
        di = get_collapse_tf(d, prefix, 'direct', '')

    z=pd.read_csv(os.path.join(upload, '%s.txt.%s.coefs.csv' % (prefix, mark)))
    z.columns = ['id', 'coefficients', 'cell_type', 'cell_line', 'tissue']
    z.coefficients = z.coefficients.map(lambda x: "%.2E" % x)
    z.loc[:, "coefficient"] = z.apply(lambda x: "%s|%s" % (x[0], x[1]), axis=1)

    # /data/home/qqin/lisa_web/upload/AR_test10_2018_08_15_0602400.705.txt.H3K27ac.2199.csv
    z.loc[:, "download"] = ["http://lisa.cistrome.org/upload/%s.txt.%s.%s.csv"%(prefix, mark, i) for i in z.id]

    z.drop(["id", "coefficients"], axis=1, inplace=True)
    z.to_csv(os.path.join(upload, '%s.%s.coefs.csv' % (prefix, mark)), index=False)

    if method == 'all' or method == 'knockout':
        cmd = "/data/home/qqin/lisa_web/run_browser.sh %s %s %s" % ('%s.txt.%s.coefs.csv' % (prefix, mark), chipp, '%s.txt.foreground_gene' % prefix)
        app.logger.info(cmd)
        os.system(cmd)

    # upload/AR12_2017_11_12_0017060.299.txt.DNase.chipseq.csv
    ## turn off the heatmap
    # cmd = "/data/home/qqin/lisa_web/run_heatmap.sh %s" % (os.path.join(upload, '%s.txt.%s.chipseq.csv' % (prefix, mark)))
    # app.logger.info(cmd)
    # os.system(cmd)
    send_localhost_mail('html', 'LISA Result', to_user, 'Hi %s, the LISA results is ready at http://lisa.cistrome.org/download/%s_result.html.' % (to_user.split('@')[0], prefix), '')

def get_collapse_tf(z, prefix, mark, t):
    a = {}
    p = {}
    z = z.sort_values(1) # pick the top five ones
    for i in range(z.shape[0]):
        a[z.iloc[i, 0].split('|')[1]] = a.get(z.iloc[i, 0].split('|')[1], []) + [z.iloc[i,0].split('|')[0]]
        p[z.iloc[i, 0].split('|')[1]] = p.get(z.iloc[i, 0].split('|')[1], []) + [z.iloc[i,1]]
        # p[z.iloc[i, 0].split('|')[1]] = min(p.get(z.iloc[i, 0].split('|')[1],1000), z.iloc[i,1])

    out = os.path.join(upload, "%s.%s.%scsv" % (prefix, mark, t))
    nas = []
    with open(out, 'w') as fout:
        fout.write("%s,%s,%s,%s,%s,%s,%s\n" % ("Transcription Factor", "1st Sample p-value", "2nd Sample p-value", "3rd Sample p-value", "4th Sample p-value", "5th Sample p-value","p"))
        for j in p:
            # fout.write("%s,%s,%s\n" % (j, " | ".join(a[j][:5]), p[j])) # pick the top five ones
            temp = []
            if len(a[j]) < 5:
                nas = (5-len(a[j])) * ['NA']
            else:
                nas = []
            for i, k in list(zip(a[j], p[j]))[:5]:
                temp.append("%s;%.2E" % (i, k))
            temp += nas
            fout.write("%s,%s,%s\n" % (j.replace(',',' | '), ','.join(temp), min(p[j])))

    z = pd.read_csv(out)
    z = z.sort_values('p')
    z.drop(['p'], axis=1, inplace=True)
    ##z.p = z.p.map(lambda x: "%.2E" % x)
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
                    f = f[0]
                    if f == '100':
                        response['state'] = 'Taskcompleted'
                        response['status'] = '100%'
                        response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct.csv' % (task_id))
                        response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs.csv' % (task_id, epigenome))
                        response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip.csv" % (task_id, epigenome))
                        response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif.csv" % (task_id, epigenome))
                        ## upload/2017_10_12_2213360.84006.txt.H3K27ac.url
                        ## http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/upload/2017_10_12_2223360.31016.txt.H3K27ac.url&gftk=refGene,full
                        response['resultl'] = "http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
                    else:
                        response['state'] = 'PROGRESS'
                        response['status'] = "{0}%".format(str(f))
                    return jsonify(response)
            elif 'failed' in l:
                response['state'] = 'Failed, check option and input'
                response['status'] = '0%'
            elif 'accomplished!!' in l:
                response['state'] = 'finished'
                response['status'] = '100%'
                response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct.csv' % (task_id))
                response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs.csv' % (task_id, epigenome))
                response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip.csv" % (task_id, epigenome))
                response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif.csv" % (task_id, epigenome))
                response['resultl'] = "http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
                return jsonify(response)
    return jsonify(response)

@app.route('/lisa_status2/<epigenome>/<task_id>', methods=['GET', 'POST'])
def lisa_taskstatus2(epigenome, task_id):
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
                    f = f[0]
                    if f == '100':
                        response['state'] = 'Taskcompleted'
                        response['status'] = '100%'
                        response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct1.csv' % (task_id))
                        response['result_1'] = os.path.join("/"+os.path.basename(upload), '%s.direct2.csv' % (task_id))

                        response['result_fig'] = os.path.join("/"+os.path.basename(upload), '%s_direct.html' % (task_id))

                        response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs1.csv' % (task_id, epigenome))
                        response['result0_1'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs2.csv' % (task_id, epigenome))

                        response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip1.csv" % (task_id, epigenome))
                        response['result1_1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip2.csv" % (task_id, epigenome))
                        response['result1_fig'] = os.path.join("/"+os.path.basename(upload), '%s_chip.html' % (task_id))

                        response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif1.csv" % (task_id, epigenome))
                        response['result2_1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif2.csv" % (task_id, epigenome))
                        response['result2_fig'] = os.path.join("/"+os.path.basename(upload), '%s_motif.html' % (task_id))

                        ## upload/2017_10_12_2213360.84006.txt.H3K27ac.url
                        ## http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/upload/2017_10_12_2223360.31016.txt.H3K27ac.url&gftk=refGene,full
                        response['resultl'] = "http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
                    else:
                        response['state'] = 'PROGRESS'
                        response['status'] = "{0}%".format(str(f))
                    return jsonify(response)
            elif 'failed' in l:
                response['state'] = 'Failed, check option and input'
                response['status'] = '0%'
            elif 'accomplished!!' in l:
                response['state'] = 'finished'
                response['status'] = '100%'

                response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct1.csv' % (task_id))
                response['result_1'] = os.path.join("/"+os.path.basename(upload), '%s.direct2.csv' % (task_id))

                if (os.path.exists(os.path.join(upload, '%s_direct.html' % (task_id)))):
                    response['result_fig'] = os.path.join("/"+os.path.basename(upload), '%s_direct.html' % (task_id))
                else:
                    response['result_fig'] = False

                response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs1.csv' % (task_id, epigenome))
                response['result0_1'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs2.csv' % (task_id, epigenome))
                response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip1.csv" % (task_id, epigenome))
                response['result1_1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip2.csv" % (task_id, epigenome))
                if (os.path.exists(os.path.join(upload, '%s_chip.html' % (task_id)))):
                    response['result1_fig'] = os.path.join("/"+os.path.basename(upload), '%s_chip.html' % (task_id))
                else:
                    response['result1_fig'] = False

                # '%s_gs1.txt.%s.coefs
                response['result0_auc'] = os.path.join("/"+os.path.basename(upload), '%s_gs1.txt.%s.roc_curve.json' % (task_id, epigenome))
                response['result1_auc'] = os.path.join("/"+os.path.basename(upload), '%s_gs2.txt.%s.roc_curve.json' % (task_id, epigenome))

                response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif1.csv" % (task_id, epigenome))
                response['result2_1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif2.csv" % (task_id, epigenome))
                if (os.path.exists(os.path.join(upload, '%s_motif.html' % (task_id)))):
                    #response['result2_fig'] = os.path.join("/"+os.path.basename(upload), '%s_motif.html' % (task_id))
                    response['result2_fig'] = False
                else:
                    response['result2_fig'] = False

                response['resultl'] = "http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs1.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
                response['resultl_1'] = "http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs2.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
                return jsonify(response)
    return jsonify(response)


@app.route('/doc', methods=['GET'])
def get_docs():
    return render_template('doc.html')

@app.route('/lisa_gallery', methods=['GET'])
def get_gallery():
    return render_template('gallery.html')

@app.route('/gallery/<path:filename>')
def download_gallery(filename):
    return send_from_directory(gallery, filename)

@app.route('/upload/<path:filename>')
def custom_upload(filename):
    return send_from_directory(upload, filename)

# add new static folder
@app.route('/download/<path:filename>')
def custom_download(filename):
    return send_from_directory(download, filename)

Bootstrap(app)
