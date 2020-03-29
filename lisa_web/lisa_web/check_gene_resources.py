import pandas as pd
import re
#import mygene
#mg = mygene.MyGeneInfo()
#df = mg.getgenes([1017, '1018', 'ENSG00000254556', 'NM_003466'], as_dataframe=True)
#print(df.columns)
#print(df.symbol.tolist())

def is_ensembl(genelist):
    flag = False
    for gene in genelist:
        if gene.startswith('ENSG') or gene.startswith('ENSM'):
            flag = True
            break
    return flag

def is_refseq(genelist):
    flag = False
    for gene in genelist:
        if len(re.findall('NM_\d*', gene)) > 0 or len(re.findall('XR_\d*', gene)) > 0 or len(re.findall('NR_\d*', gene)) > 0:
            flag = True
            break
    return flag

def is_entrez(genelist):
    flag = False
    for gene in genelist:
        if gene.isnumeric():
            flag = True
            break
    return flag

def is_genename(genelist):
    ensembleh = pd.read_csv('/project/Cistrome/LISA/lisa_web/download/Homo97_Ensembl.txt', sep='\t')
    print(ensembleh.head())
    ensemblem = pd.read_csv('/project/Cistrome/LISA/lisa_web/download/Mus97_Ensembl.txt', sep='\t')
    return (ensembleh.gene_name.isin(genelist).sum() > 0) or (ensemblem.gene_name.isin(genelist).sum() > 0)

if __name__ == '__main__':
    is_genename(['TP53'])
