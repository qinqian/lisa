#!/usr/bin/env python
import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--tf')
parser.add_argument('--genes')
args = parser.parse_args()

df = pd.read_csv(args.genes, header=None)
df.loc[:, 'TF' ] = df.iloc[:, 0].map(lambda x: x.split('|')[1])
df.drop_duplicates('TF', inplace=True)
print(np.where(df.loc[:, 'TF'] == args.tf)[0][0])
