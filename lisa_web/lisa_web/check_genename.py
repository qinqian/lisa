import pandas as pd

def check_available_genes(genes, species='hg38'):
    if genes[0].startswith('ENSG'):
        genes = list(map(lambda x: x.split('.')[0], genes))
        if species == 'hg38':
            ensemble = pd.read_csv('/project/Cistrome/LISA/lisa_web/download/Homo97_Ensembl.txt', sep='\t')
        else:
            ensemble = pd.read_csv('/project/Cistrome/LISA/lisa_web/download/Mus97_Ensembl.txt', sep='\t')
        ensemble.iloc[:, 0] = ensemble.iloc[:, 0].map(lambda x: x.split('.')[0])
        symbols = ensemble.loc[ensemble.iloc[:, 0].isin(genes), 'gene_name']
        return list(set(symbols))
    else:
        return list(set(genes))

def clean_empty_lins(genes):
    filtered_genes = filter(lambda x:x!='', genes)
    return list(set(filtered_genes))


if __name__ == '__main__':
#    print(clean_empty_lins(['a', 'b', 'c', '']))
    # print(check_available_genes(['ENSG00000174837',
    #                              'ENSG00000232702',
    #                              'ENSG00000172738'], 'human'))
    print(check_available_genes(['AR',
                                 'FOXA1',
                                 'TP53'], 'mouse'))
