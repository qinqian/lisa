import pandas as pd
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly import tools

from plotly.graph_objs import Scatter, Heatmap

up=pd.read_csv('3_down.gene_symbol.lisa_direct.csv', header=None)
dn=pd.read_csv('3_up.gene_symbol.lisa_direct.csv', header=None)

print(up.head())
final = up.merge(dn, on=0)
print(final.head())
trace0 = Scatter(x=-np.log10(final.iloc[:, 1]),
                 y=-np.log10(final.iloc[:, 2]), mode= 'markers',
                 marker= dict(size= 9,
                              opacity= 0.9,
                              line = dict(width = 0.8)
                             ),
                 text=final.iloc[:, 0],
                 xaxis="Up-regulated gene set results", yaxis="Down-regulated gene set results")

plot([trace0], filename='test.html')
