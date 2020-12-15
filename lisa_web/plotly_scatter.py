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

up=pd.read_csv(up_r, header=0)
if '1' in up.columns:
    up=up.sort_values(by='1')
if '0.1' in up.columns:
    up=up.sort_values(by='0.1')
up.loc[:, 'name'] = up.iloc[:, 0].map(lambda x:x.split('|')[1])
up.drop_duplicates('name', inplace=True, keep='first')

dn=pd.read_csv(dn_r, header=0)
if '1' in dn.columns:
    dn=dn.sort_values(by='1')
if '0.1' in dn.columns:
    dn=dn.sort_values(by='0.1')
dn.loc[:, 'name'] = dn.iloc[:, 0].map(lambda x:x.split('|')[1])
dn.drop_duplicates('name', inplace=True, keep='first')

final = up.merge(dn, on='name', how='outer')
print(final.head())
final = final.loc[(final.iloc[:, 1]<=0.05) | (final.loc[:, 'pval_y']<=0.05), :]

xlim = -np.log10(np.min(final.iloc[:, 1]))*1.2
ylim = -np.log10(np.min(final.loc[:, 'pval_y']))*1.2
print(xlim)
print(ylim)

top_index = np.union1d(np.argsort(final.iloc[:, 1])[:10], np.argsort(final.loc[:, 'pval_y'])[:10])
final_top = final.iloc[top_index, :]

final = final.drop(final.index[top_index])
x = -np.log10(final.iloc[:, 1])
y = -np.log10(final.loc[:, 'pval_y'])

top_trace0 = Scatter(x=x,
                     y=y, 
                     name='other TF with p-value < 0.01',
                     mode='markers',
                     text=final.iloc[:, 0], 
                     marker= dict(size= 8,
                                  opacity= 0.7,
                                  ))

x = -np.log10(final_top.iloc[:, 1])
y = -np.log10(final_top.loc[:, 'pval_y'])
trace1 = Scatter(x=x,
                 y=y,
                 name='top TFs',
                 # mode='markers+text',
                 mode='markers',
                 marker=dict(size= 6,
                             opacity= 0.8),
                 textfont=dict(
                    family='sans serif',
                    size=18,
                    color='black'
                 ),
                 text = list(map(lambda x: "%s\n%s" % ('Cistrome ID|TF', x), final_top.iloc[:, 0])),
                 hoverinfo = 'text',
                 textposition='top right')

layout = Layout(
    title=title,
    xaxis=dict(
        title='-log10(p-value) of Gene Set 1' if labels1.strip() == '' else '-log10(p-value) of %s' % labels1,
        showgrid=False,
        titlefont=dict(
            family='Arial',
            size=18),
        rangemode='tozero',
        range=[0, xlim]
    ),
    yaxis=dict(
        title='-log10(p-value) of Gene Set 2' if labels2.strip() == '' else '-log10(p-value) of %s' % labels2,
        showgrid=False,
        titlefont=dict(
            family='Arial',
            size=18
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
