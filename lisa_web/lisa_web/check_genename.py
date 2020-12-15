import pandas as pd
from check_gene_resources import is_ensembl, is_refseq, is_entrez, is_genename
#import mygene
#mg = mygene.MyGeneInfo()

def check_available_genes(genes, species='hg38'):
    isens = is_ensembl(genes)
    isent = is_entrez(genes)
    issym = is_genename(genes)
    isref = is_refseq(genes)

    if isens + isent + issym + isref > 1: # a mixture of genes ids
        import mygene
        mg = mygene.MyGeneInfo()
        df = mg.querymany(genes, as_dataframe=True, scopes='refseq,symbol,entrezgene,reporter,uniprot,ensemblgene')
        df = df.loc[~pd.isnull(df.symbol), :]
        return list(set(df.symbol.str.upper().tolist()))

    if isens: # pure ensemble ids
        genes = list(map(lambda x: x.split('.')[0], genes))
        if species == 'hg38':
            ## lisa path of the gene ensemble annotation
            ensemble = pd.read_csv('lisa_web/Homo97_Ensembl.txt', sep='\t')
        else:
            ensemble = pd.read_csv('lisa_web/Mus97_Ensembl.txt', sep='\t')
        ensemble.iloc[:, 0] = ensemble.iloc[:, 0].map(lambda x: x.split('.')[0])
        #symbols = ensemble.loc[ensemble.iloc[:, 0].isin(genes), 'gene_name'].str.upper()
        symbols = ensemble.loc[ensemble.iloc[:, 0].isin(genes), 'gene_name']
        return list(set(symbols))
    elif isent: # pure entrez ids
        import mygene
        mg = mygene.MyGeneInfo()
        df = mg.getgenes(genes, as_dataframe=True)
        return df.symbol.tolist()
    else: # pure symbol, or refseq
        return list(set(genes))


def clean_empty_lins(genes):
    filtered_genes = filter(lambda x:x!='', genes)
    filtered_genes = list(set(filtered_genes))
    return list(map(lambda x: x.strip(), filtered_genes))


if __name__ == '__main__':
    print(check_available_genes(['ENSG00000174837',
                                 'ENSG00000232702',
                                 'ENSG00000172738'], 'hg38'))
    #print(check_available_genes(['AR',
    #                             'FOXA1',
    #                             'TP53'], 'mouse'))
    #print(check_available_genes(['ENSMUSG00000000916',
    #                             'ENSMUSG00000000732',
    #                             'ENSMUSG00000000948'], 'mouse'))
    #print('\n'.join(check_available_genes(['ENSMUSG00000000214',
    #'ENSMUSG00000000631',
    #'ENSMUSG00000000794',
    #'ENSMUSG00000001525',
    #'ENSMUSG00000002028',
    #'ENSMUSG00000003814',
    #'ENSMUSG00000008348',
    #'ENSMUSG00000008489',
    #'ENSMUSG00000013089',
    #'ENSMUSG00000013236',
    #'ENSMUSG00000014602',
    #'ENSMUSG00000015291',
    #'ENSMUSG00000015656',
    #'ENSMUSG00000016349',
    #'ENSMUSG00000018451',
    #'ENSMUSG00000018474',
    #'ENSMUSG00000018707',
    #'ENSMUSG00000018846',
    #'ENSMUSG00000019505',
    #'ENSMUSG00000020176',
    #'ENSMUSG00000020182',
    #'ENSMUSG00000020315',
    #'ENSMUSG00000020612',
    #'ENSMUSG00000020889',
    #'ENSMUSG00000020893',
    #'ENSMUSG00000020894',
    #'ENSMUSG00000020900',
    #'ENSMUSG00000021061',
    #'ENSMUSG00000021250',
    #'ENSMUSG00000021268',
    #'ENSMUSG00000021313',
    #'ENSMUSG00000021609',
    #'ENSMUSG00000021700',
    #'ENSMUSG00000022044',
    #'ENSMUSG00000022263'], 'mouse')))

    #print('\n'.join(check_available_genes(['ENSMUSG00000001930',
    #'ENSMUSG00000002265',
    #'ENSMUSG00000002748',
    #'ENSMUSG00000002910',
    #'ENSMUSG00000002985',
    #'ENSMUSG00000003657',
    #'ENSMUSG00000003660',
    #'ENSMUSG00000003934',
    #'ENSMUSG00000004328',
    #'ENSMUSG00000004558',
    #'ENSMUSG00000004892',
    #'ENSMUSG00000005089',
    #'ENSMUSG00000005198',
    #'ENSMUSG00000005360',
    #'ENSMUSG00000005871',
    #'ENSMUSG00000005873',
    #'ENSMUSG00000006205',
    #'ENSMUSG00000006301',
    #'ENSMUSG00000006522',
    #'ENSMUSG00000006782',
    #'ENSMUSG00000006930',
    #'ENSMUSG00000007021',
    #'ENSMUSG00000007097',
    #'ENSMUSG00000007892',
    #'ENSMUSG00000008393',
    #'ENSMUSG00000008489',
    #'ENSMUSG00000009291',
    #'ENSMUSG00000010064',
    #'ENSMUSG00000010095',
    #'ENSMUSG00000010663',
    #'ENSMUSG00000010803',
    #'ENSMUSG00000011884',
    #'ENSMUSG00000013089',
    #'ENSMUSG00000013921',
    #'ENSMUSG00000014602'], 'mouse')))
    #df = mg.getgenes([u'ENSMUSG00000019505', u'ENSMUSG00000015291', u'ENSMUSG00000018451', u'ENSMUSG00000016349', u'ENSMUSG00000021700', u'ENSMUSG00000020893', u'ENSMUSG00000021250', u'ENSMUSG00000020612', u'ENSMUSG00000020315', u'ENSMUSG00000020176', u'ENSMUSG00000020894', u'ENSMUSG00000021609', u'ENSMUSG00000022263', u'ENSMUSG00000020900', u'ENSMUSG00000008489', u'ENSMUSG00000018707', u'ENSMUSG00000000794', u'ENSMUSG00000013236', u'ENSMUSG00000002028', u'ENSMUSG00000003814', u'ENSMUSG00000013089', u'ENSMUSG00000021268', u'ENSMUSG00000018474', u'ENSMUSG00000020182', u'ENSMUSG00000021313', u'ENSMUSG00000001525', u'ENSMUSG00000000631', u'ENSMUSG00000000214', u'ENSMUSG00000018846', u'ENSMUSG00000022044', u'ENSMUSG00000015656', u'ENSMUSG00000008348', u'ENSMUSG00000020889', u'ENSMUSG00000021061', u'ENSMUSG00000014602'], as_dataframe=True)
    #df = mg.getgenes(['ENSG00000004059'], as_dataframe=True)
    #df = mg.getgenes(['SLC39A9'], as_dataframe=True)
    #df = mg.querymany(['NM_001256306', 'ENSMUSG00000019505', 'SLC39A9'], as_dataframe=True, scopes='refseq,symbol,entrezgene,reporter,uniprot,ensemblgene')
    #print(df)
    #print(df.symbol.str.upper())
    #print(check_available_genes(['NM_001256306', 'ENSMUSG00000019505', 'SLC39A9']))
    print(check_available_genes(['MAST2']))

