import sys
import os

cols = [(165,0,38),
(215,48,39),
(244,109,67),
(253,174,97),
(254,224,144),
(224,243,248),
(171,217,233),
(116,173,209),
(69,117,180),
(49,54,149)]


def read_DC(fp):
    d = {}
    for line in fp.readlines():
        f = line.split()
        d[f[0]] = f[1]
    return d

def read_genes(fp):
    gene_list = []
    for line in fp.readlines():
        line = line.strip()
        f = line.split(':')
        chrom,start,end,name = f[0], int(f[1]), int(f[2]), f[-1]
        gene_list += [(chrom,start-1e5,end+1e5,name)]
    return gene_list

def read_coefs(fp):
    "40543  -4.708595450932237  Activated_Treg      Blood"
    sample_list = []
    name_list = []
    val_list = []

    i = 0
    for line in fp.readlines():
        try:
            line = line.replace('\"','')
            f = line.split(',')
            val_list    += [float(f[1])] 
            sample_list += [f[0]]
            if f[2]:
                name_list   += ['%s-%d' % (f[2],i)]
            else:
                name_list   += ['%s-%d' % ('NA',i)]
            i += 1
        except:
            pass

    return sample_list, name_list, val_list

def read_tfs(fp,ntop=20):
    "161|PPARA,6.57E-12"
    sample_list = []
    name_list = []
    val_list = []

    for i in range(ntop):
        line = fp.readline()
        line = line.strip()
        line = line.replace('|',',')
        #print(line)
        f = line.split(',')
        sample_list += [f[0]]
        name_list   += ['%s-%d' % (f[1],i)]
        val_list    += [float(f[2])] 

    return sample_list, name_list, val_list


def write_url(sample_list, TF_sample_list ):
    """
    sample_coef_file  tf_result_file  gene_file
    """
    url = "http://dc2.cistrome.org/api/batchview/m/%s/w/" % '_'.join(TF_sample_list + sample_list)

def write_session(dc,sample_list,name_list,val_list,  TF_sample_list,TF_name_list,TF_val_list,   chrom,start,end,gene_list):
    """
    sample_coef_file  tf_result_file  gene_file
    """

    max_abs_val = max( [abs(x) for x in val_list] )

    s = "["

    for i,sample in enumerate(TF_sample_list):
        #print(sample,dc[sample])
        name = TF_name_list[i]
        blue_val  = 0
        green_val = 0
        red_val   = 0
        os.system("cp -r %s/*treat.bw /data5/lisa_browser/" % dc[sample])
        url = "http://lisa.cistrome.org//data5/lisa_browser/%s_treat.bw" % (sample)
        # http://lisa.cistrome.org//data5/lisa_browser/test.bed
        s += "{\"type\":\"bigwig\",\"name\":\"%s\",\"url\":\"%s\",\"mode\":1,\"qtc\":{\"anglescale\":1,\"pr\":%d,\"pg\":%d,\"pb\":%d,\"nr\":0,\"ng\":0,\"nb\":0,\"pth\":\"#000099\",\"nth\":\"#800000\",\"thtype\":0,\"thmin\":0,\"thmax\":10,\"thpercentile\":90,\"height\":50,\"summeth\":1},\"metadata\":{}},\n" % (name,url,blue_val,green_val,red_val) 

    for i,sample in enumerate(sample_list):
        name = name_list[i]
        val  = val_list[i]
        idx  = 9 - int(9.0*(max_abs_val-val)/(2*max_abs_val))
        #print(max_abs_val,val,idx)
        blue_val  = cols[idx][2]
        green_val = cols[idx][1]
        red_val   = cols[idx][0]
        os.system("cp -r %s/*treat.bw /data5/lisa_browser/" % dc[sample])
        url = "http://lisa.cistrome.org//data5/lisa_browser/%s_treat.bw" % (sample)
        s += "{\"type\":\"bigwig\",\"name\":\"%s\",\"url\":\"%s\",\"mode\":1,\"qtc\":{\"anglescale\":1,\"pr\":%d,\"pg\":%d,\"pb\":%d,\"nr\":0,\"ng\":0,\"nb\":0,\"pth\":\"#000099\",\"nth\":\"#800000\",\"thtype\":0,\"thmin\":0,\"thmax\":10,\"thpercentile\":90,\"height\":50,\"summeth\":1},\"metadata\":{}},\n" % (name,url,blue_val,green_val,red_val) 


    s += """{"type":"native_track","list":[{"name":"refGene","mode":3,"qtc":{"anglescale":1,"pr":255,"pg":0,"pb":0,"nr":0,"ng":0,"nb":230,"pth":"#800000","nth":"#000099","thtype":0,"thmin":0,"thmax":10,"thpercentile":95,"height":50,"summeth":1,"textcolor":"#000000","fontsize":"8pt","fontfamily":"sans-serif","fontbold":false,"bedcolor":"#002EB8"},"metadata":{},"details":{"source":"UCSC Genome Browser","download date":"Nov. 28, 2013"}}]},
{"type":"metadata","vocabulary_set":{}},"""

    #s +=  "{\"type\":\"coordinate_override\",\"coord\":\"%s,%d,%s,%d\"}" % (chrom,start,chrom,end)

    s += """{"type":"run_genesetview","list":["""
    t = []
    for i,elem in enumerate(gene_list):
        chrom,start,end,name = elem[0],elem[1],elem[2],elem[3]
        t += ["{\"c\":\"%s\",\"a\":%d,\"a1\":%d,\"b\":%d,\"b1\":%d,\"isgene\":true,\"name\":\"%s\",\"strand\":\"+\"}" % (chrom,start,start,end,end,name) ]

    s += ',\n'.join(t)
    s += "],"
    s += "\"viewrange\":[\"%s\",%d,\"%s\",%d]}" % ( gene_list[0][3], gene_list[0][1], gene_list[-1][3], gene_list[-1][2] ) 
    s += "]"
    print(s)

if __name__ == "__main__":
    """
    make_session.py coeffile.csv tfpval.csv genelist.txt 
    """

    chrom = 'chr7'
    tss   = 35056565
    start = tss - 1e5
    end   = tss + 1e5

    DC = read_DC(open('DC_table.txt'))
    #print(DC)

    sample_list,name_list,val_list = read_coefs( open(sys.argv[1]) ) 
    #print(val_list)
    TF_list,TF_name,TF_val_list = read_tfs( open(sys.argv[2] ), ntop=10 )

    write_url(TF_list,sample_list)
    #genelist = [('chr1',10000000,10100000,'test1'),('chr2',10000000,10100000,'test2')]
    genelist = read_genes( open(sys.argv[3] ) )
    write_session(DC,sample_list,name_list,val_list, TF_list[0:5],TF_name[0:5],TF_val_list[0:5],chrom,start,end,genelist)
 
