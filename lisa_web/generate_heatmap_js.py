import pandas as pd
from clustergrammer import Network
import numpy as np
import collections
import argparse 

p = argparse.ArgumentParser()
p.add_argument('-d')
args = p.parse_args()

net = Network()
delta = pd.read_csv(args.d, index_col=0)
status = delta.iloc[:-1, -1].values.reshape(-1)
delta_f = delta.iloc[:-1, :-1]

tf = delta_f.columns.map(lambda x: x.split('|')[1])
tf_dict = collections.OrderedDict()
for i, t in enumerate(tf):
    tf_dict[t] = tf_dict.get(t, []) + [i] 
ids = []
for t in tf_dict:
    ids.append(tf_dict[t][:3])
ids = np.concatenate(ids)

delta_f = delta_f.iloc[:, ids]

target, = np.where(status == 1)
cont, = np.where(status == 0)

print(target.shape)
if len(target) < 100:
     target_n = len(target)
else:
     target_n = 100

index = np.concatenate([np.random.choice(target, target_n), np.random.choice(cont, 100)])
status = status[index]
delta_f = delta_f.iloc[index, :50]

ann = pd.read_table('/data/home/qqin/01_Projects/Programming/dc2/scripts/hg38_best_dc_tfcr_basedon_frip_peak_dhs_all_nonhm_nonca.xls')

ann = ann.iloc[:, [0, 6, 8]]

ann_dict = {}
for i in range(ann.shape[0]):
    ann_dict[str(ann.iloc[i, 0])]= ann.iloc[i, 1:]

tf = delta_f.columns.map(lambda x: "TF: %s"  % x.split('|')[1]) 
genes = delta_f.index.map(lambda x:x.split(':')[-1])

genes, index = np.unique(genes, return_index=True)
status = status[index]

tfs = []
for i,j in enumerate(tf):
    tfs.append("%s.%s" % (j, i))

ids = delta_f.columns.map(lambda x:x.split('|')[0])
fout = open("%s_heatmap_matrix.txt" % args.d, 'w')
fout.write("\t\t%s\n" % ('\t'.join(tfs)))

cls = []
for i in ids:
    if ann_dict.get(i, ['NA'])[0] == 'NA':
        cls.append("Cell Line: %s" % ('NA'))
    else:
        cls.append("Cell Line: %s" % (ann_dict[i][0]))
fout.write("\t\t%s\n" % ('\t'.join(cls)))

ts = []
for i in ids:
    if ann_dict.get(i, ['NA', 'NA'])[1] == 'NA':
        ts.append("Tissue: %s" % ('NA'))
    else:
        ts.append("Tissue: %s" % (ann_dict[i][1]))
fout.write("\t\t%s\n" % ('\t'.join(ts)))

for i in range(status.shape[0]):
    fout.write('%s\t%s\t%s\n' % ("Gene: %s"% genes[i], "Input Gene: %s" % status[i], '\t'.join(delta_f.iloc[i, :].map(str))))
fout.close()

net.load_file("%s_heatmap_matrix.txt" % args.d)
net.cluster()
net.write_json_to_file('viz', '%s_mult_view.json' % args.d)

