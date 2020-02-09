#!/project/dev/qqin/miniconda3/bin/python
import sys
import pandas as pd
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly import tools
from plotly.graph_objs import Scatter, Heatmap, Layout, Figure

up_r = sys.argv[1]
dn_r = sys.argv[2]
prefix = sys.argv[3]
title = sys.argv[4]
labels1 = sys.argv[5]
labels2 = sys.argv[6]


def dedup_rank(csv):
    up=pd.read_csv(csv, header=0, index_col=0)
    if 'pval' in up.columns:
        up=up.sort_values(by='pval')
        #up.loc[:, 'name'] = up.iloc[:, [2, 4, 5, 6]].apply(lambda x: ','.join([y for y in list(map(str, x)) if y!='None']), axis=1)
    if 'tissue' in up.columns:
        up.loc[:, 'name'] = up.iloc[:, [2, 4, 5, 6]].apply(lambda x: ','.join([y for y in list(map(str, x)) if y!='None']), axis=1)
        #up.loc[:, 'name'] = up.loc[:, 'name'].map(lambda x: up.index.map(lambda x: x.split('|')[0]) +','+x)
    else:
        up.loc[:, 'name'] = up.index.values
    print(up.head())
    return up, up.drop_duplicates('name', inplace=False, keep='first')

up, up_dedup = dedup_rank(up_r)
dn, dn_dedup = dedup_rank(dn_r)

print(up.head())
print(up_dedup.head())

uniq_selection = list(up_dedup.index) + list(dn_dedup.index)

final = up.merge(dn, left_index=True, right_index=True, how='outer')
final = final.loc[uniq_selection, :]

print(final.head())
final = final.loc[(final.loc[:, 'pval_x']<=0.05) | (final.loc[:, 'pval_y']<=0.05), :]
xlim = -np.log10(np.min(final.loc[:, 'pval_x']))*1.1
ylim = -np.log10(np.min(final.loc[:, 'pval_y']))*1.1
print(xlim)
print(ylim)

top_index = np.union1d(np.argsort(final.loc[:, 'pval_x'])[:10], np.argsort(final.loc[:, 'pval_y'])[:10])
final_top = final.iloc[top_index, :]

final = final.drop(final.index[top_index])
x = -np.log10(final.loc[:, 'pval_x'])
y = -np.log10(final.loc[:, 'pval_y'])

top_trace0 = Scatter(x=x,
                     y=y, 
                     name='other TFs with p-value < 0.05',
                     mode='markers',
                     text=final.loc[:, 'name_y'], 
                     marker= dict(size= 6,
                                  opacity= 0.7))

x = -np.log10(final_top.loc[:, 'pval_x'])
y = -np.log10(final_top.loc[:, 'pval_y'])
trace1 = Scatter(x=x,
                 y=y,
                 name='top 10 TFs with p-value < 0.05',
                 mode='markers',
                 marker=dict(size= 9,
                             opacity= 0.8),
                 textfont=dict(
                    family='sans serif',
                    size=11,
                    color='black'
                 ),
                 text = list(map(lambda x: "%s\n%s" % ('Cistrome ID|TF', x), final_top.loc[:, 'name_y'])),
                 hoverinfo = 'text',
                 textposition='top right')

layout = Layout(
    title=title,
    xaxis=dict(
        title='-log10(p-value) of Gene Set 1' if labels1.strip() == '' else '-log10(p-value) of %s' % labels1,
        showgrid=False,
        titlefont=dict(
            family='Arial',
            size=20),
        rangemode='tozero',
        range=[0, xlim]
    ),
    yaxis=dict(
        title='-log10(p-value) of Gene Set 2' if labels2.strip() == '' else '-log10(p-value) of %s' % labels2,
        showgrid=False,
        titlefont=dict(
            family='Arial',
            size=20
        ),
        rangemode='tozero',
        range=[0, ylim]
    ),
    hovermode = 'closest',
    width=850,
    height=650
)

fig = Figure(data=[top_trace0, trace1], layout=layout)
plot(fig, filename='%s.html' % prefix, show_link=False, auto_open=False)
