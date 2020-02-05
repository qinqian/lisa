import logging
import os, sys
import subprocess
#from logging.handlers import RotatingFileHandler, FileHandler
from logging import FileHandler
import time
import numpy as np
import pandas as pd
import re
import glob
from check_genename import clean_empty_lins, check_available_genes

from flask import Flask, render_template, redirect, url_for, send_from_directory, abort
from flask import make_response, jsonify

from flask import request
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from celery import Celery
import random
from flask import flash
from .mail import send_localhost_mail
from flask_httpauth import HTTPBasicAuth,HTTPDigestAuth

# initialize an application
app = Flask(__name__, instance_relative_config = True)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

from .form import LISAForm

app.secret_key = 's3cr3t' # crsf
dir_prefix = '/project/Cistrome/LISA/lisa_web/'
download = dir_prefix + 'download/'
gallery = dir_prefix + 'lisa_web/gallery'
new_gallery = dir_prefix + 'lisa_web/new_gallery'
new_gallery_mm = dir_prefix + 'lisa_web/new_gallery_mm'
upload = dir_prefix + 'upload/'

# debug mode on
app.debug = False
if not app.debug:
    app.logger.setLevel(logging.DEBUG)
    #handler = RotatingFileHandler(dir_prefix + '/lisa.log', maxBytes=10000000, backupCount=20)
    handler = FileHandler(dir_prefix + '/lisa.log')
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
    handler.setLevel(logging.DEBUG)
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
        labels = form.labels.data
        if labels == '':
            labels = 'gene_set_1'

        genes2 = form.genes2.data
        labels2 = form.labels2.data
        if labels2 == '':
            labels2 = 'gene_set_2'

        ## fix space isssue
        labels = labels.replace(' ', '_')
        labels2 = labels2.replace(' ', '_')

        job_name = form.name.data
        job_name = job_name.replace(' ', '_')
        job_name = job_name.replace('(', '')  # incase user input ( or )
        job_name = job_name.replace(')', '')
        job_name = job_name.replace('#', '')  # user input weird character 
        job_name = job_name.replace("\'", "")  # user input weird character 
        job_name = job_name.replace('-', '')  # user input weird character 

        method = form.method.data

        species = form.species.data.encode('utf-8')
        marks = form.mark.data.encode('utf-8')
        if marks == 'All':
            marks = ['DNase','H3K27ac']
        else:
            marks = [marks]

        label = round(random.random(), 3)
        prefix = "%s_%s" % (job_name, secure_filename(time.strftime('%Y_%m_%d %H:%M:%S', time.localtime())) + str(label))
        background = form.background.data

        if background == '':
            background_file = 'dynamic_auto_tad'
        else:
            if len(background.split('\n')) > 500 or len(background.split('\n')) < 20:
                return render_template('index.html', form=form, message='inline-block')
            background_file = os.path.join(upload, '%s_user_background.txt' % (prefix+"__"+species))
            background_file_handler = open(background_file, 'w')
            for i in background.split('\n'):
                i = i.strip().split(",") # comma is ok
                for j in i:
                    print >>background_file_handler, j
            background_file_handler.close()

        if genes2 == '':
            app.logger.info("%s %s %s at %s" % (str(genes), marks, species, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            app.logger.info("%s %s %s at %s from %s" % (str(genes), marks, species, prefix,
                                                        request.remote_addr))
            gsf = os.path.join(upload, '%s.txt' % (prefix+"__"+species))
            if job_name == '':
                return render_template('index.html', form=form, message_job='inline-block')

            genes = genes.split('\n')
            genes = clean_empty_lins(genes)

            ## support ensemble
            genes = check_available_genes(genes, species)

            if len(genes) > 500 or len(genes) < 20:
                return render_template('index.html', form=form, message='inline-block')

            gene_set = open(gsf, 'w')
            for i in genes:
                i = i.strip().split(",") # comma is ok
                for j in i:
                    print >>gene_set, j
            gene_set.close()
            app.logger.info("%s lisa modeling finished %s" % (prefix, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))
            task = run_lisa.apply_async(args=(method, species, marks, prefix+"__"+species, background_file, to_user), countdown=1, expires=3600)
            cc = render_template('display.html', epigenome='_'.join(marks),
                                 task_id=prefix+"__"+species, method=method, download_zip = os.path.join('/download', prefix+"__"+species+'.zip'))
            with open('%s/%s%s' % (download, prefix+"__"+species, "_result.html"), 'w') as outf:
                outf.write(cc)
            return redirect('/download/%s_result.html'%(prefix+"__"+species))
        else:
            if job_name == '':
                return render_template('index.html', form=form, message_job='inline-block')
            genes = genes.split('\n')
            genes2 = genes2.split('\n')
            genes = clean_empty_lins(genes)
            genes2 = clean_empty_lins(genes2)

            genes = check_available_genes(genes, species)
            genes2 = check_available_genes(genes2, species)
            if len(genes) > 500 or len(genes) < 20:
                return render_template('index.html', form=form, message='inline-block')
            if len(genes2) > 500 or len(genes2) < 20:
                return render_template('index.html', form=form, message='inline-block')

            app.logger.info("%s %s %s at %s" % (str(genes), marks, species, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())))

            app.logger.info("%s %s %s at %s from %s" % (str(genes), marks, species, prefix,
                                                        request.remote_addr))
            gsf1 = os.path.join(upload, '%s_gs1.txt' % (prefix+"__"+species))
            gene_set1 = open(gsf1, 'w')
            for i in genes:
                i = i.strip().split(",") # comma is ok
                for j in i:
                    print >>gene_set1, j
            gene_set1.close()

            gsf2 = os.path.join(upload, '%s_gs2.txt' % (prefix+"__"+species))
            gene_set2 = open(gsf2, 'w')
            for i in genes2:
                i = i.strip().split(",") # comma is ok
                for j in i:
                    print >>gene_set2, j
            gene_set2.close()

            task = multiple_run_lisa.apply_async(args=(method, species, marks, prefix+"__"+species, background_file, to_user, labels, labels2), countdown=1, expires=3600)
            cc = render_template('multiple_display.html', epigenome='_'.join(marks),
                                 task_id=prefix+"__"+species, method=method, labels1=labels, labels2=labels2, download_zip = os.path.join('/download', prefix+"__"+species+'.zip'))
            with open('%s/%s%s' % (download, prefix+"__"+species, "_result.html"), 'w') as outf:
                outf.write(cc)
            #return render_template('display.html', epigenome=marks, task_id=prefix)
            return redirect('/download/%s_result.html'%(prefix+"__"+species))

    return render_template('index.html', form = form, message="none")

@celery.task(bind=True)
def multiple_run_lisa(self, method, species, mark, prefix, background_file, to_user, labels1, labels2):
    # issues: chmod 777 of lisa2 anaconda library and lisa_web root directory
    # chmod 777 /var/www/.theano
    # is not a good idea...
    # cmd = "/data/home/qqin/lisa_web/run_lisa2.sh %s %s %s %s %s %s" % (species, str([mark]), prefix, str(method), "%s_gs1.txt" % os.path.join(upload, prefix), "%s_gs2.txt" %  os.path.join(upload, prefix))
    cmd = dir_prefix + "run_lisa2.sh %s %s %s %s %s %s %s" % (species, str(mark).replace(' ',''), prefix, str(method), "%s_gs1.txt" % os.path.join(upload, prefix), "%s_gs2.txt" %  os.path.join(upload, prefix), background_file)
    app.logger.info(cmd)
    with open(upload + '/%s_snakemake_output.txt' % prefix, 'a') as fout:
        p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
        out, err = p.communicate()
        fout.flush()
        app.logger.info(out)
        app.logger.info(err)

    # z=pd.read_csv(os.path.join(upload, '%s_gs1.txt.%s.coefs.csv' % (prefix, mark)))
    # z.columns = ['id', 'coefficients', 'cell_type', 'cell_line', 'tissue']
    # z.coefficients = z.coefficients.map(lambda x: "%.2E" % x)
    # z.loc[:, "coefficient"] = z.apply(lambda x: "%s|%s" % (x[0], x[1]), axis=1)
    # z.loc[:, "download"] = ["http://lisa.cistrome.org/upload/%s_gs1.txt.%s.%s.csv"%(prefix, mark, i) for i in z.id]
    # z.drop(["id", "coefficients"], axis=1, inplace=True)
    # z.to_csv(os.path.join(upload, '%s.%s.coefs1.csv' % (prefix, mark)), index=False)
    # z=pd.read_csv(os.path.join(upload, '%s_gs2.txt.%s.coefs.csv' % (prefix, mark)))
    # z.columns = ['id', 'coefficients', 'cell_type', 'cell_line', 'tissue']
    # z.coefficients = z.coefficients.map(lambda x: "%.2E" % x)
    # z.loc[:, "coefficient"] = z.apply(lambda x: "%s|%s" % (x[0], x[1]), axis=1)

    # z.loc[:, "download"] = ["http://lisa.cistrome.org/upload/%s_gs2.txt.%s.%s.csv"%(prefix, mark, i) for i in z.id]
    # z.drop(["id", "coefficients"], axis=1, inplace=True)
    # z.to_csv(os.path.join(upload, '%s.%s.coefs2.csv' % (prefix, mark)), index=False)

    ## if method == 'all' or method == 'knockout':
    ##     ## recovery by setting Require not ip in apache
    ##     for m in mark:
    ##         chipp1 = '%s_gs1.txt.%s.chipseq.p_value.csv' % (prefix, m)
    ##         chipp2 = '%s_gs2.txt.%s.chipseq.p_value.csv' % (prefix, m)
    ##         motif1 = '%s_gs1.txt.%s.motif99.p_value.csv' % (prefix, m)
    ##         motif2 = '%s_gs2.txt.%s.motif99.p_value.csv' % (prefix, m)
    ##         cmd = dir_prefix + "run_browser.sh %s %s %s" % ('%s_gs1.txt.%s.coefs.csv' % (prefix, m), chipp1, '%s_gs1.txt.foreground_gene' % prefix)
    ##         app.logger.info(cmd)
    ##         os.system(cmd)
    ##         cmd = dir_prefix + "run_browser.sh %s %s %s" % ('%s_gs2.txt.%s.coefs.csv' % (prefix, m), chipp2, '%s_gs2.txt.foreground_gene' % prefix)
    ##         app.logger.info(cmd)
    ##         os.system(cmd)

    ##     with open(os.path.join(upload, '%s_browser_link.txt' % prefix), 'w') as out_browser:
    ##         for m in mark:
    ##             out_browser.write("http://cistrome.org/browser/?genome=" + species + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs1.txt.%s.url' % (prefix, m)) + "&gftk=refGene,full \n")
    ##             out_browser.write("http://cistrome.org/browser/?genome=" + species + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs2.txt.%s.url' % (prefix, m)) + "&gftk=refGene,full \n")

    # upload/AR12_2017_11_12_0017060.299.txt.DNase.chipseq.csv
    ## turn off the heatmap
    # cmd = "/data/home/qqin/lisa_web/run_heatmap.sh %s" % (os.path.join(upload, '%s.txt.%s.chipseq.csv' % (prefix, mark)))
    # app.logger.info(cmd)
    # os.system(cmd)

    def output_collapse(geneset, type, label):
        combined_result = os.path.join(upload, "%s_%s.txt_%s_cauchy_combine_raw.csv" % (prefix, geneset, type))
        combined_result_df = pd.read_csv(combined_result, header=0)
        get_collapse_tf(combined_result_df, prefix, label, '%s.' % type)
        return combined_result

    gs1_chipseq = output_collapse('gs1', 'chipseq', 'combined')
    gs2_chipseq = output_collapse('gs2', 'chipseq', 'combined2')
    cmd = dir_prefix + "run_plot.sh %s %s %s_chip Combined_LISA_Model_ChIP-seq %s %s" % (gs1_chipseq, gs2_chipseq, os.path.join(upload, prefix), labels1, labels2)
    app.logger.info(cmd)
    with open(upload + '%s_chip_plot_output.txt' % prefix, 'a') as fout:
        p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
        out, err = p.communicate()
        fout.flush()

    if method == 'all' or method == 'knockout':
        gs1_motif   = output_collapse('gs1', 'motif', 'combined')
        gs2_motif   = output_collapse('gs2', 'motif', 'combined2')
        cmd = dir_prefix + "run_plot.sh %s %s %s_motif Combined_LISA_Model_Motif %s %s" % (gs1_motif, gs2_motif, os.path.join(upload, prefix), labels1, labels2)
        app.logger.info(cmd)
        with open(upload + '/%s_motif_plot_output.txt' % prefix, 'a') as fout:
            p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
            out, err = p.communicate()
            fout.flush()

    download_zip = os.path.join(download, '%s.zip' % prefix)
    os.system('cd %s && zip -r %s %s*' % (upload, download_zip, prefix))
    send_localhost_mail('html', 'LISA Result', to_user, 'Hi %s, the LISA results is ready at http://lisa.cistrome.org/download/%s_result.html.' % (to_user.split('@')[0], prefix), '')


@celery.task(bind=True)
def run_lisa(self, method, species, mark, prefix, background_file, to_user):
    # issues: chmod 777 of lisa2 anaconda library and lisa_web root directory
    # chmod 777 /var/www/.theano
    # is not a good idea...
    app.logger.info(prefix)
    cmd = "%srun_lisa.sh %s %s %s %s %s %s" % (dir_prefix, species, str(mark).replace(' ', ''), prefix, "%s.txt" %  os.path.join(upload, prefix), str(method), background_file)
    app.logger.info(cmd)
    with open(upload + '/%s_snakemake_output.txt' % prefix, 'a') as fout:
        p = subprocess.Popen(cmd.split(), stdout=fout, stderr=fout)
        out, err = p.communicate()
        fout.flush()
        app.logger.info(out)
        app.logger.info(err)

    ## TODO: wait for WashU installation
    ##if method == 'all' or method == 'knockout':
    ##    for m in mark:
    ##       chipp = '%s.txt.%s.chipseq.p_value.csv' % (prefix, m)
    ##       cmd = dir_prefix + "run_browser.sh %s %s %s" % ('%s.txt.%s.coefs.csv' % (prefix, m), chipp, '%s.txt.foreground_gene' % prefix)
    ##       app.logger.info(cmd)
    ##       os.system(cmd)

    ##    with open(os.path.join(upload, '%s_browser_link.txt' % prefix), 'w') as out_browser:
    ##        for m in mark:
    ##            out_browser.write("http://cistrome.org/browser/?genome=" + species + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s.txt.%s.url' % (prefix, m)) + "&gftk=refGene,full \n")

    # compress all output for download
    combined_result = os.path.join(upload, "%s.txt_chipseq_cauchy_combine_raw.csv" % prefix)
    combined_result = pd.read_csv(combined_result, header=0)
    collapse_combined_result = get_collapse_tf(combined_result, prefix, 'combined', 'chipseq.')

    if method == 'all' or method == 'knockout':
        combined_result = os.path.join(upload, "%s.txt_motif_cauchy_combine_raw.csv" % prefix)
        combined_result = pd.read_csv(combined_result, header=0)
        collapse_combined_result = get_collapse_tf(combined_result, prefix, 'combined', 'motif.')

    #zip test.zip upload//test1_2019_03_12_0018340.666__hg38*
    download_zip = os.path.join(download, '%s.zip' % prefix)
    os.system('cd %s && zip -r %s %s*' % (upload, download_zip, prefix))

    ## turn off the heatmap
    # cmd = "/data/home/qqin/lisa_web/run_heatmap.sh %s" % (os.path.join(upload, '%s.txt.%s.chipseq.csv' % (prefix, mark)))
    # app.logger.info(cmd)
    # os.system(cmd)
    send_localhost_mail('html', 'LISA Result', to_user, 'Hi %s, the LISA results is ready at http://lisa.cistrome.org/download/%s_result.html.' % (to_user.split('@')[0], prefix), '')

def get_collapse_tf(z, prefix, mark, t):
    a = {}
    p = {}
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
                        download_zip = os.path.join(download, '%s.zip' % task_id)
                        if os.path.exists(download_zip) and os.path.getsize(download_zip) > 0:
                            response['state'] = 'finished'
                            percent = 100
                        else:
                            percent = 99
                        response['status'] = '%s%%' % percent
                        response['result'] = os.path.join("/upload", '%s.combined.chipseq.csv' % (task_id))
                        response['result2'] = os.path.join("/upload", '%s.combined.motif.csv' % (task_id))
                        response['result_zip'] = os.path.join("/download", '%s.zip' % (task_id))
                        # response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct.csv' % (task_id))
                        # response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs.csv' % (task_id, epigenome))
                        # response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip.csv" % (task_id, epigenome))
                        # response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif.csv" % (task_id, epigenome))
                        ## http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/upload/2017_10_12_2223360.31016.txt.H3K27ac.url&gftk=refGene,full
                        ## http://cistrome.org/browser/?genome=mm10wugb&datahub=http://lisa.cistrome.org//upload/mouse_test1_2019_01_03_0831000.263_gs1.txt.DNase.url&gftk=refGene,full
                        # response['resultl'] = "http://cistrome.org/browser/?genome=" + task_id.split('__')[-1] + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
                    else:
                        response['state'] = 'PROGRESS'
                        response['status'] = "{0}%".format(str(f))
                    return jsonify(response)
            elif 'failed' in l:
                response['state'] = 'Failed, check option and input'
                response['status'] = '0%'
            elif 'accomplished!!' in l:
                download_zip = os.path.join(download, '%s.zip' % task_id)
                if os.path.exists(download_zip) and os.path.getsize(download_zip) > 0:
                    response['state'] = 'finished'
                    percent = 100
                else:
                    percent = 99
                response['status'] = '%s%%' % percent
                response['result'] = os.path.join("/upload", '%s.combined.chipseq.csv' % (task_id))
                response['result2'] = os.path.join("/upload", '%s.combined.motif.csv' % (task_id))
                response['result_zip'] = os.path.join("/download", '%s.zip' % (task_id))
                #response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct.csv' % (task_id))
                #response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs.csv' % (task_id, epigenome))
                #response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip.csv" % (task_id, epigenome))
                #response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif.csv" % (task_id, epigenome))
                #response['resultl'] = "http://cistrome.org/browser/?genome=" + task_id.split('__')[-1] + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
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
                        download_zip = os.path.join(download, '%s.zip' % task_id)
                        if os.path.exists(download_zip) and os.path.getsize(download_zip) > 0:
                            response['state'] = 'finished'
                            percent = 100
                        else:
                            percent = 99
                        response['status'] = '%s%%' % percent
                        response['result'] = os.path.join("/upload", '%s.combined.chipseq.csv' % (task_id))
                        response['result2'] = os.path.join("/upload", '%s.combined.motif.csv' % (task_id))
                        response['result_2'] = os.path.join("/upload", '%s.combined2.chipseq.csv' % (task_id))
                        response['result2_2'] = os.path.join("/upload", '%s.combined2.motif.csv' % (task_id))
                        response['result1_fig'] = os.path.join("/upload", '%s_chip.html' % (task_id))
                        if os.path.exists(os.path.join("/upload", '%s_motif.html' % (task_id))):
                            response['result2_fig'] = os.path.join("/upload", '%s_motif.html' % (task_id))
                        #response['resultl'] = "http://cistrome.org/browser/?genome=" + task_id.split('__')[-1] + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs1.txt.%s.url' % (task_id, epigenome.split('_')[0])) + "&gftk=refGene,full"
                        #response['resultl_1'] = "http://cistrome.org/browser/?genome=" + task_id.split('__')[-1] + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs2.txt.%s.url' % (task_id, epigenome.split('_')[0])) + "&gftk=refGene,full"
                        #response['resultl'] = "http://cistrome.org/browser/?genome=" + task_id.split('__')[-1] + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs1.txt.%s.url' % (task_id, epigenome.split('_')[0])) + "&gftk=refGene,full"
                        #response['resultl_1'] = "http://cistrome.org/browser/?genome=" + task_id.split('__')[-1] + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs2.txt.%s.url' % (task_id, epigenome.split('_')[0])) + "&gftk=refGene,full"

                        response['result_zip'] = os.path.join("/download", '%s.zip' % (task_id))
                        # response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct1.csv' % (task_id))
                        # response['result_1'] = os.path.join("/"+os.path.basename(upload), '%s.direct2.csv' % (task_id))
                        # response['result_fig'] = os.path.join("/"+os.path.basename(upload), '%s_direct.html' % (task_id))
                        # response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs1.csv' % (task_id, epigenome))
                        # response['result0_1'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs2.csv' % (task_id, epigenome))
                        # response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip1.csv" % (task_id, epigenome))
                        # response['result1_1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip2.csv" % (task_id, epigenome))
                        # response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif1.csv" % (task_id, epigenome))
                        # response['result2_1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif2.csv" % (task_id, epigenome))
                        ## upload/2017_10_12_2213360.84006.txt.H3K27ac.url
                        ## http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/upload/2017_10_12_2223360.31016.txt.H3K27ac.url&gftk=refGene,full
                    else:
                        response['state'] = 'PROGRESS'
                        response['status'] = "{0}%".format(str(f))
                    return jsonify(response)
            elif 'failed' in l:
                response['state'] = 'Failed, check option and input'
                response['status'] = '0%'
            elif 'accomplished!!' in l:
                download_zip = os.path.join(download, '%s.zip' % task_id)
                if os.path.exists(download_zip) and os.path.getsize(download_zip) > 0:
                    response['state'] = 'finished'
                    percent = 100
                else:
                    percent = 99

                response['status'] = '%s%%' % percent
                response['result'] = os.path.join("/upload", '%s.combined.chipseq.csv' % (task_id))
                response['result2'] = os.path.join("/upload", '%s.combined.motif.csv' % (task_id))
                response['result_2'] = os.path.join("/upload", '%s.combined2.chipseq.csv' % (task_id))
                response['result2_2'] = os.path.join("/upload", '%s.combined2.motif.csv' % (task_id))
                response['result1_fig'] = os.path.join("/upload", '%s_chip.html' % (task_id))
                if os.path.exists(os.path.join("/upload", '%s_motif.html' % (task_id))):
                    response['result2_fig'] = os.path.join("/upload", '%s_motif.html' % (task_id))
                response['result_zip'] = os.path.join("/download", '%s.zip' % (task_id))
                # response['result'] = os.path.join("/"+os.path.basename(upload), '%s.direct1.csv' % (task_id))
                # response['result_1'] = os.path.join("/"+os.path.basename(upload), '%s.direct2.csv' % (task_id))
                # if (os.path.exists(os.path.join(upload, '%s_direct.html' % (task_id)))):
                #     response['result_fig'] = os.path.join("/"+os.path.basename(upload), '%s_direct.html' % (task_id))
                # else:
                #     response['result_fig'] = False
                # response['result0'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs1.csv' % (task_id, epigenome))
                # response['result0_1'] = os.path.join("/"+os.path.basename(upload), '%s.%s.coefs2.csv' % (task_id, epigenome))
                # response['result1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip1.csv" % (task_id, epigenome))
                # response['result1_1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.chip2.csv" % (task_id, epigenome))
                # if (os.path.exists(os.path.join(upload, '%s_chip.html' % (task_id)))):
                #     response['result1_fig'] = os.path.join("/"+os.path.basename(upload), '%s_chip.html' % (task_id))
                # else:
                #     response['result1_fig'] = False
                # # '%s_gs1.txt.%s.coefs
                # response['result0_auc'] = os.path.join("/"+os.path.basename(upload), '%s_gs1.txt.%s.roc_curve.json' % (task_id, epigenome))
                # response['result1_auc'] = os.path.join("/"+os.path.basename(upload), '%s_gs2.txt.%s.roc_curve.json' % (task_id, epigenome))
                # response['result2'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif1.csv" % (task_id, epigenome))
                # response['result2_1'] = os.path.join("/"+os.path.basename(upload), "%s.%s.motif2.csv" % (task_id, epigenome))
                # if (os.path.exists(os.path.join(upload, '%s_motif.html' % (task_id)))):
                #     #response['result2_fig'] = os.path.join("/"+os.path.basename(upload), '%s_motif.html' % (task_id))
                #     response['result2_fig'] = False
                # else:
                #     response['result2_fig'] = False
                # response['resultl'] = "http://cistrome.org/browser/?genome=" + task_id.split('__')[-1] + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs1.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
                # response['resultl_1'] = "http://cistrome.org/browser/?genome=" + task_id.split('__')[-1] + "wugb&datahub=http://lisa.cistrome.org/" + os.path.join("/"+os.path.basename(upload), '%s_gs2.txt.%s.url' % (task_id, epigenome)) + "&gftk=refGene,full"
                return jsonify(response)
    return jsonify(response)

@app.route('/stat', methods=['GET'])
def get_stat():
    return render_template('stat.html')

@app.route('/doc', methods=['GET'])
def get_docs():
    return render_template('doc.html')

@app.route('/lisa_gallery', methods=['GET'])
def get_gallery():
    return render_template('gallery.html')

@app.route('/lisa_gallery_mm', methods=['GET'])
def get_gallery2():
    return render_template('gallery_mm.html')

@app.route('/gallery/<path:filename>')
def download_gallery(filename):
    return send_from_directory(gallery, filename)

@app.route('/new_gallery/<path:filename>')
def download_new_gallery(filename):
    return send_from_directory(new_gallery, filename)

@app.route('/new_gallery_mm/<path:filename>')
def download_new_gallery_mm(filename):
    return send_from_directory(new_gallery_mm, filename)

@app.route('/upload/<path:filename>')
def custom_upload(filename):
    return send_from_directory(upload, filename)

# add new static folder
@app.route('/download/<path:filename>')
def custom_download(filename):
    return send_from_directory(download, filename)

#auth = HTTPBasicAuth()
###users = {'lisa': '2cis@(trome)9'}
#
#@auth.get_password
#def get_pw(username):
#    if username in users:
#        return users.get(username)
#    return None
#
#@app.route('/cistromedb_data/<path:filename>')
##@auth.login_required
#def data(filename):
#    return send_from_directory('/data/home/qqin/lisa_web/cistromedb_data/', filename)

#@auth.error_handler
#def unauthorized():
#    return make_response(jsonify({'error': '!!Sorry, Unauthorized access'}), 403)

#@app.route('/testsec')
#@auth.login_required
#def testsec():
#    return "Hello, %s!" % auth.username()

Bootstrap(app)
