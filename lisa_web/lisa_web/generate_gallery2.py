#!/usr/bin/env python
from jinja2 import Environment, FileSystemLoader, select_autoescape
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, redirect, url_for, send_from_directory, abort, jsonify
import pandas as pd
import os
import json

#df = pd.read_table('lisa_results_meta_table_human_with_gene_sets.xls')
df = pd.read_table('lisa_results_meta_table_mouse_with_gene_sets.xls')

## /data5/home/jfan/projects/LISA/lisa_examples/lisa_results_meta_table_human_with_gene_sets.xls 

df.drop('GEO_id', inplace=True, axis=1)
df.drop('DE_col', inplace=True, axis=1)
index = [ i for i in range(0, df.shape[0], 2)] 

df = df.iloc[index,:]
df = df.iloc[:,:-2]

inc = pd.read_table('lisa_results_meta_table_mouse_new_selected.xls')
df = df.loc[df.ID.isin(inc.loc[:, 'ID']), :]

#exc = pd.read_table('exclude.ids', sep=',', header=None)
#df = df.loc[~df.ID.isin(exc.iloc[0]), :]

print(df.head())

labels = [ "%s_%s" % (i, j) for i, j in zip(df.iloc[:, 0], df.iloc[:, -1]) ]
labels2 = [ "%s_up" % (i) for i, j in zip(df.iloc[:, 0], df.iloc[:, -1]) ]
df.iloc[:,-1] = list(map(lambda x, y: '<a href=http://lisa.cistrome.org/gallery/{0}.txt>{1}</a><span> & </span><a href=http://lisa.cistrome.org/gallery/{2}.txt>{3}</a>'.format(x, x.split('_')[1], y, y.split('_')[1]), labels, labels2))

#result = list(map(lambda x: '<div class="row"><div class="col"><a  class="btn" href="http://lisa.cistrome.org/gallery/%s_H3K27ac.html">H3K27ac</a><a class="btn btn-primary" href="http://lisa.cistrome.org/gallery/%s_DNase.html">DNase-seq</a><a class="btn btn-secondary" href="http://lisa.cistrome.org/gallery/%s_H3K4me3.html">H3K4me3</a><a  class="btn btn btn-info" href="http://lisa.cistrome.org/gallery/%s_H3K27me3.html">H3K27me3</a><a href="http://lisa.cistrome.org/gallery/%s_H3K4me1.html" class="btn btn-warning">H3K4me1</a></div></div>' %(x,x,x,x, x), df.iloc[:,0]))
result1 = list(map(lambda x: '<div class="col"><a class="" href="http://lisa.cistrome.org/gallery/%s_H3K27ac.html">H3K27ac</a></div>' %(x), df.iloc[:,0]))
result0 = list(map(lambda x: '<div class="col"><a class="" href="http://lisa.cistrome.org/gallery/%s_DNase.html">DNase-seq</a></div>' %(x), df.iloc[:,0]))
print(df.shape)
print(df.columns)
df.drop(['Accession'], inplace=True, axis=1)
df.drop(['geo_id'], inplace=True, axis=1)
ids = df.ID
df.drop(['ID'], inplace=True, axis=1)
###df['LISA_results'] =  result
df['LISA_DNase'] = result0
df['LISA_H3K27ac'] = result1

def generate_page():
    loader = FileSystemLoader('.')
    env = Environment(loader=loader) #autoescape=select_autoescape(['html']))
    template = env.get_template('gallery_template.html')
    #print(template)
    x = template.render(header=df.columns, table=df.values)
    with open('gallery.html', 'w') as outf:
        outf.write(x)
    #os.system('cp gallery.html ../templates/gallery.html')
    os.system('cp gallery.html ../templates/gallery_mm.html')

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
    z = z.sort_values(1) # pick the top five ones
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
    #tcga = '/data5/home/jfan/projects/TCGA/lisa_results'
    #bench = '/data5/home/chenfei/JingyuFan/data_collection/MARGE/LISA_figures/human_ebi_random'
    bench = '/data5/home/chenfei/JingyuFan/data_collection/MARGE/LISA_figures/mouse_ebi_random'
   
    loader = FileSystemLoader('.')
    env = Environment(loader=loader) #autoescape=select_autoescape(['html']))
    template = env.get_template('multiple_display.html')
    for i in ids:
        print(i)
        d1 = os.path.join(bench, "%s_down.gene_symbol.lisa_direct.csv"%(i))
        if (not os.path.exists(d1)):
            print('%s not exists!' % d1)
            continue
        d2 = os.path.join(bench, "%s_up.gene_symbol.lisa_direct.csv"%(i))
        if (not os.path.exists(d2)):
            print('%s not exists!' % d2)
            continue

        os.system('python ../../plotly_scatter.py %s %s %s TFChIP-seq down-regulated up-regulated' % (d1, d2, '%s.fig1' % i))
        d1 = pd.read_csv(d1, header=None)
        d2 = pd.read_csv(d2, header=None)
        di1 = get_collapse_tf(d1, '%s_down' % i, 'direct', '')
        di2 = get_collapse_tf(d2, '%s_up' % i, 'direct', '')
        #for j in ['H3K27ac', 'H3K4me3', 'H3K4me1', 'H3K27me3', 'DNase']:
        for j in ['H3K27ac', 'DNase']:
            test = '%s_%s.json' % (i,j)
            with open('%s_%s.html' % (i, j), 'w') as fout:
                fout.write(template.render(epigenome=j, method='all', task_id="%s_%s" % (i,j)))

            json_dict = {}
            json_dict['result'] = di1
            json_dict['result_1'] = di2

            json_dict['result_fig'] = '%s.fig1.html' % i
            ##coefficients page
            json_dict['result0_1'] = '%s.%s.coefs1.csv' % ("%s_up" % i, j)
            json_dict['result0'] = '%s.%s.coefs1.csv' % ("%s_down" % i, j)

            #'data5/home/chenfei/JingyuFan/data_collection/MARGE/LISA_figures/human_ebi_random/294_down.gene_symbol.lisa_direct.csv'
            chipp1 = os.path.join(bench, "%s_down.gene_symbol.%s.chipseq.p_value.csv"%(i,j))
            chipp2 = os.path.join(bench, "%s_up.gene_symbol.%s.chipseq.p_value.csv"%(i,j))
            if (not os.path.exists(chipp1)):
                print('%s not exists' % chipp1)
                continue
            if (not os.path.exists(chipp2)):
                print('%s not exists' % chipp2)
                continue
          
            os.system('python ../../plotly_scatter.py %s %s %s InSilicoChIP-seq down-regulated up-regulated' % (chipp1, chipp2, '%s.%s.fig2' % (i,j)))
            json_dict['result1_fig'] = '%s.%s.fig2.html' % (i, j)

            if (os.path.exists(os.path.join(bench, "%s_down.gene_symbol.%s.coefs.csv" %(i,j)))):
                coef1 = pd.read_csv(os.path.join(bench, "%s_down.gene_symbol.%s.coefs.csv" %(i,j)))
                clean_coef(coef1, j, "%s_down" % i)

                # 3_down.gene_symbol.foreground_gene
                cmd1 = "./run_browser_local.sh %s %s %s" % (os.path.join(bench, "%s_down.gene_symbol.%s.coefs.csv" %(i,j)), chipp1, os.path.join(bench, '%s_down.gene_symbol.foreground_gene' % i))
                os.system(cmd1)
                #json_dict['resultl'] = "http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/gallery/%s_down.gene_symbol.%s.url&gftk=refGene,full" % (i,j) 
                json_dict['resultl'] = "http://cistrome.org/browser/?genome=mm10wugb&datahub=http://lisa.cistrome.org/gallery/%s_down.gene_symbol.%s.url&gftk=refGene,full" % (i,j) 
            if (os.path.exists(os.path.join(bench, "%s_up.gene_symbol.%s.coefs.csv" %(i,j)))):
                coef2 = pd.read_csv(os.path.join(bench, "%s_up.gene_symbol.%s.coefs.csv" %(i,j)))
                clean_coef(coef2, j, "%s_up" % i)

                cmd2 = "./run_browser_local.sh %s %s %s" % (os.path.join(bench, "%s_up.gene_symbol.%s.coefs.csv" %(i,j)), chipp2, os.path.join(bench, '%s_up.gene_symbol.foreground_gene' % i))
                os.system(cmd2)
                #json_dict['resultl_1'] = "http://cistrome.org/browser/?genome=hg38wugb&datahub=http://lisa.cistrome.org/gallery/%s_up.gene_symbol.%s.url&gftk=refGene,full" % (i,j) 
                json_dict['resultl_1'] = "http://cistrome.org/browser/?genome=mm10wugb&datahub=http://lisa.cistrome.org/gallery/%s_up.gene_symbol.%s.url&gftk=refGene,full" % (i,j) 

            c1 = pd.read_csv(chipp1, header=None)
            ch1 = get_collapse_tf(c1, '%s_down' % i, j, 'chip.')
            json_dict['result1'] = ch1
            c2 = pd.read_csv(chipp2, header=None)
            ch2 = get_collapse_tf(c2, '%s_up' % i, j, 'chip.')
            json_dict['result1_1'] = ch2

            m1 = pd.read_csv(os.path.join(bench, '%s_up.gene_symbol.%s.motif99.p_value.csv' % (i, j)), header=None)
            m2 = pd.read_csv(os.path.join(bench, '%s_down.gene_symbol.%s.motif99.p_value.csv' % (i, j)), header=None)
            mo1 = get_collapse_tf(m1, '%s_down'%i, j, 'motif.')
            mo2 = get_collapse_tf(m2, '%s_up'%i, j, 'motif.')
            json_dict['result2'] = mo1
            json_dict['result2_1'] = mo2

            with open(test, 'w') as jsonf:
                json.dump(json_dict, jsonf)
#            return

generate_page()
#print(df.head())
#generate_htmls(ids)
#####generate_htmls(df.iloc[:,0])
