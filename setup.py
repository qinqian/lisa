"""lisa: a bioinformatics software
epigenome analysis to rank TFs from gene set
"""
import os
from glob import glob
from setuptools import setup, find_packages, Extension
from numpy.distutils.misc_util import get_numpy_include_dirs

def get_extension():
    """ get extension for computing regulatory potential from bigwig """
    bigwig_src = ['bigWigRegPotential.c', 'pybw.c',
                  'ffScore.c', 'rbTree.c', 'rangeTree.c', 'ffAli.c', 'ffAliHelp.c', 'fuzzyFind.c', 'bwgValsOnChrom.c', 'tokenizer.c', 'asParse.c', 'aliType.c', 'dnaseq.c', 'dnautil.c', 'gfxPoly.c', 'psl.c', 'binRange.c', 'sqlList.c', 'basicBed.c', 'bPlusTree.c','base64.c','bbiRead.c','bbiWrite.c', 'bits.c','bwgQuery.c','cheapcgi.c','cirTree.c','common.c','dlist.c','dystring.c','errAbort.c','hash.c','hex.c','hmmstats.c','https.c','intExp.c','internet.c','kxTok.c','linefile.c','localmem.c','memalloc.c','mime.c','net.c','obscure.c','options.c','osunix.c','pipeline.c','portimpl.c','servBrcMcw.c','servCrunx.c','servcis.c','servcl.c','servmsII.c','servpws.c','sqlNum.c','udc.c','verbose.c','wildcmp.c','zlibFace.c']

    bigwig_src = list(map(lambda x: os.path.join('lisa', 'regpotential', x), bigwig_src))
    ext = Extension('lisa._bw',
                    sources=bigwig_src,
                    extra_compile_args=['-O3', '-std=c99'], #, '-Wall'],
                    libraries=['ssl', 'z', 'crypto'])
    return ext

def main():
    """setup entry
    """
    setup(
        name='lisa',
        version='1.0',
        url='http://lisa.cistrome.org',
        author='Qian Qin',
        description=__doc__,
        packages=find_packages(),
        ext_modules=[get_extension(), ],
        include_dirs=['lisa/regpotential'] + get_numpy_include_dirs(),
        install_requires=['numpy==1.22.0', 
                          'scikit-learn', 'theano', 'fire',
                          'h5py', 'pandas==0.25.2',
                          'scipy',
                          'snakemake', 'PyYAML', 'yappi', 'mpmath'
                          ],
        include_package_data=True,
        package_data={'lisa': ['rules/*', 'workflows/*', 'lisa.ini']},
        scripts=glob('bin/*'),
        classifiers=[
            'Environment::Console',
            'Operating System:: POSIX',
            "Programming Language :: Python :: 3",
            "Topic :: Scientific/Engineering :: Bio-Informatics"],
        keywords='ChIP-seq',
        license='OTHER',
        zip_safe=False)

if __name__ == '__main__':
    main()
