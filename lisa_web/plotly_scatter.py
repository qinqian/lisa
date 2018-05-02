#!/usr/bin/env python

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

up=pd.read_csv(up_r, header=None)
up=up.sort_values(by=1)
up.loc[:, 'name'] = up.iloc[:, 0].map(lambda x:x.split('|')[1])

dn=pd.read_csv(dn_r, header=None)
dn=dn.sort_values(by=1)
dn.loc[:, 'name'] = dn.iloc[:, 0].map(lambda x:x.split('|')[1])

up.drop_duplicates('name', inplace=True, keep='first')
dn.drop_duplicates('name', inplace=True, keep='first')
#print(up.head())
#print(dn.head())

final = up.merge(dn, on=0, how='outer')
final = final.loc[(final.iloc[:, 1]<=0.01) | (final.iloc[:, 3]<=0.01), :]

xlim = -np.log10(np.min(final.iloc[:, 1]))*1.25
ylim = -np.log10(np.min(final.iloc[:, 3]))*1.25

final.iloc[np.where(pd.isnull(final.iloc[:, 3]))[0], 3] = 1
final.iloc[np.where(pd.isnull(final.iloc[:, 1]))[0], 1] = 1

#print(final.shape)
top_index = np.union1d(np.argsort(final.iloc[:, 1])[:5], np.argsort(final.iloc[:, 3])[:5])
final_top = final.iloc[top_index, :]
#print(final_top.shape)

#print(top_index)
final = final.drop(final.index[top_index])
#print(final.shape)
x = -np.log10(final.iloc[:, 1])
y = -np.log10(final.iloc[:, 3])

top_trace0 = Scatter(x=x,
                    y=y, 
                    name='other TF with p-value < 0.01',
                    mode='markers',
                    text=final.iloc[:, 0], 
                    marker= dict(size= 8,
                                 opacity= 0.7,
                                 ))

x = -np.log10(final_top.iloc[:, 1])
y = -np.log10(final_top.iloc[:, 3])
trace1 = Scatter(x=x,
                 y=y,
                 name='top TFs',
                 # mode='markers+text',
                 mode='markers',
                 marker=dict(size= 6,
                             opacity= 0.90,
                             ),
                 textfont=dict(
                    family='sans serif',
                    size=18,
                    color='black'
                 ),
                 text = list(map(lambda x: "%s\n%s" % ('Cistrome ID|TF', x), final_top.iloc[:, 0])),
                 hoverinfo = 'text',
                 textposition='topright')

layout = Layout(
    title=title,
    xaxis=dict(
        title='-log10(p-value) of Gene Set 1',
        showgrid=False,
        titlefont=dict(
            family='Arial',
            size=18),
        range=[-2, xlim]
    ),
    yaxis=dict(
        title='-log10(p-value) of Gene Set 2',
        showgrid=False,
        titlefont=dict(
            family='Arial',
            size=18
        ),
        range=[-2, ylim]
    ),
    width=750,
    height=650
)

fig = Figure(data=[top_trace0, trace1], layout=layout)
plot(fig, filename='%s.html' % prefix, show_link=False, auto_open=False)
