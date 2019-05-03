#!/usr/bin/env python
from jinja2 import Environment, FileSystemLoader, select_autoescape
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, redirect, url_for, send_from_directory, abort, jsonify
import pandas as pd
import os
import json

df = pd.read_table('lisa_results_meta_table_mouse_with_gene_sets.xls')
df.drop('GEO_id', inplace=True, axis=1)
df.drop('DE_col', inplace=True, axis=1)
index = [ i for i in range(0, df.shape[0], 2) ]
df = df.iloc[index,:]
df = df.iloc[:,:-2]
inc = pd.read_table('lisa_results_meta_table_mouse_new_selected.xls')
df = df.loc[df.ID.isin(inc.loc[:, 'ID']), :]

print(df.head())
labels  = [ "%s_%s" % (i, j) for i, j in zip(df.iloc[:, 0], df.iloc[:, -1]) ]
labels2 = [ "%s_up" % (i) for i, j in zip(df.iloc[:, 0], df.iloc[:, -1]) ]
df.iloc[:, -1] = list(map(lambda x, y: '<a href=http://lisa.cistrome.org/gallery/{0}.txt>{1}</a><span> & </span><a href=http://lisa.cistrome.org/gallery/{2}.txt>{3}</a>'.format(x, x.split('_')[1], y, y.split('_')[1]), labels, labels2))
combined = list(map(lambda x:'<div class="col"><a class="" href="http://lisa.cistrome.org/new_gallery_mm/%s_combined.html">Combined</a></div>' %(x), df.iloc[:,0]))
df.drop(['Accession'], inplace=True, axis=1)
df.drop(['geo_id'], inplace=True, axis=1)
ids = df.ID
df.drop(['ID'], inplace=True, axis=1)
df['Combined'] = combined

def generate_page():
    loader = FileSystemLoader('.')
    env = Environment(loader=loader) #autoescape=select_autoescape(['html']))
    template = env.get_template('gallery_template.html')
    #print(template)
    x = template.render(header=df.columns, table=df.values)
    with open('new_gallery_mm.html', 'w') as outf:
        outf.write(x)
    os.system('cp new_gallery_mm.html ../templates/new_gallery_mm.html')

def clean_coef(x, mark, prefix):
    x.columns = ['id', 'coefficients', 'cell_type', 'cell_line', 'tissue']
    print(x.coefficients)
    x.coefficients = x.coefficients.map(lambda x: "%.2E" % x)
    x.loc[:, "coefficient"] = x.apply(lambda x: "%s|%s" % (x[0], x[1]), axis=1)
    x.loc[:, "download"] = ["http://lisa.cistrome.org/gallery/download/%s_gs1.txt.%s.%s.csv"%(prefix, mark, i) for i in x.id]
    x.drop(["id", "coefficients"], axis=1, inplace=True)
    x.to_csv(os.path.join('.', '%s.%s.coefs1.csv' % (prefix, mark)), index=False)

def get_collapse_tf(z, prefix, mark, t):
    a = {}
    p = {}
    
    z = z.sort_values('0.1') # pick the top five ones
    
    for i in range(z.shape[0]):
        a[z.iloc[i, 0].split('|')[1]] = a.get(z.iloc[i, 0].split('|')[1], []) + [z.iloc[i,0].split('|')[0]]
        p[z.iloc[i, 0].split('|')[1]] = p.get(z.iloc[i, 0].split('|')[1], []) + [z.iloc[i,1]]
        # p[z.iloc[i, 0].split('|')[1]] = min(p.get(z.iloc[i, 0].split('|')[1],1000), z.iloc[i,1])

    out = os.path.join('.', "%s.%s.%scsv" % (prefix, mark, t))
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
    
def generate_htmls(ids):
    bench = '/data5/home/jfan/projects/LISA/lisa_results/fixed_background/mouse/'
    bench = '/data/home/qqin/lisa_web/figure1/mouse_combined/'

    #bench = '/data5/home/jfan/projects/LISA/lisa_results/fixed_background/mouse'
    loader = FileSystemLoader('.')
    env = Environment(loader=loader) #autoescape=select_autoescape(['html']))
    template = env.get_template('combined_gallery_multiple_display.html')
    for i in ids:
        # /data/home/qqin/lisa_web/figure1/combined/123_down.gene_symbol_chipseq_cauchy_combine_raw.csv
        with open('%s_combined.html' % (i), 'w') as fout:
            fout.write(template.render(method='all', task_id=i))
#        d1 = os.path.join(bench, "%s_down.gene_symbol_chipseq_cauchy_combine_raw.csv" % (i))
#        if (not os.path.exists(d1)):
#            print('%s not exists!' % d1)
#            continue
#        d2 = os.path.join(bench, "%s_up.gene_symbol_chipseq_cauchy_combine_raw.csv" % (i))
#        if (not os.path.exists(d2)):
#            print('%s not exists!' % d2)
#            continue
#
#        os.system('python ../../plotly_scatter.py %s %s %s Combined_TR_ChIP-seq down-regulated up-regulated' % (d1, d2, '%s_combined.fig1' % i))
#        d1 = pd.read_csv(d1)
#        d2 = pd.read_csv(d2)
#        di1 = get_collapse_tf(d1, '%s_down' % i, 'combined', 'chipseq.')
#        di2 = get_collapse_tf(d2, '%s_up' % i, 'combined', 'chipseq.')
#
#        json_dict = {}
#        json_dict['status'] = '100%'
#        json_dict['result'] = di1
#        json_dict['result_2'] = di2
#        json_dict['result1_fig'] = '%s_combined.fig1.html' % i
#
#        m1 = os.path.join(bench, '%s_up.gene_symbol_motif_cauchy_combine_raw.csv' % i)
#        m2 = os.path.join(bench, '%s_down.gene_symbol_motif_cauchy_combine_raw.csv' % i)
#        os.system('python ../../plotly_scatter.py %s %s %s Combined_TR_motif down-regulated up-regulated' % (m1, m2, '%s_combined.fig2' % i))
#
#        m1 = pd.read_csv(m1)
#        m2 = pd.read_csv(m2)
#        mo1 = get_collapse_tf(m1, '%s_down' % i, 'combined', 'motif.')
#        mo2 = get_collapse_tf(m2, '%s_up' % i, 'combined', 'motif.')
#        json_dict['result2'] = mo1
#        json_dict['result2_2'] = mo2
#        json_dict['result2_fig'] = '%s_combined.fig2.html' % i
#
#        test = '%s_combined.json' % (i)
#        with open(test, 'w') as jsonf:
#            json.dump(json_dict, jsonf)

#generate_page()
generate_htmls(ids)

