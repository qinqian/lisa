""" interface for loading lisa config file
"""
from configparser import ConfigParser

class Config(ConfigParser):
    """ data input interface"""
    def __init__(self, f, s):
        """
        f: configuration file
        s: species
        """
        super().__init__()
        self.read(f)
        self.s = s

    @property
    def get_meta(self):
        """ get annotation
        """
        if hasattr(self, "s"):
            return self.get(self.s, 'meta')

    @property
    def get_basic_meta(self):
        if hasattr(self, "s"):
            return self.get('basics', 'meta')

    @property
    def get_annotation(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'tssbin')

    @property
    def get_tss_refseq(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'tss')

    def get_rp(self, factor):
        if hasattr(self, "s"):
            if factor == 'H3K4me3':
                return self.get(self.s, '%s_1kbRP' % factor)
            return self.get(self.s, '%s_RP' % factor)

    @property
    def get_dnase_bin(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'DNase_bin')

    def genome_count(self, factor):
        if hasattr(self, "s"):
            return self.get(self.s, '%s_count' % factor)

    @property
    def genome_window_map(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'genome_window_map')

    @property
    def genome_window(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'genome_window')

    @property
    def genome_100bp_window(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'genome_100bp_window')

    @property
    def tf_chipseq(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'tf_chipseq')

    @property
    def tf_chipseq_meta(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'tf_chipseq_meta')

    @property
    def chrom(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'chrom_len')

    @property
    def get_motif_meta(self):
        if hasattr(self, "s"):
            return self.get('basics', 'motif')

    def get_motif_index(self, cutoff=99):
        """ 100bp for deletion """
        if hasattr(self, "s"):
            return self.get(self.s, 'genome_100bp_motif_index%s' % cutoff)

    def get_motif_1kb(self, cutoff=99):
        """ 1kb for cluster """
        if hasattr(self, "s"):
            return self.get(self.s, 'genome_motif%s' % cutoff)

    @property
    def get_motif_sim(self):
        if hasattr(self, "s"):
            return self.get("basics", "motif_similarity")

    @property
    def get_beta(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'tf_chipseq_beta')

    @property
    def get_udhs(self):
        if hasattr(self, "s"):
            return self.get(self.s, 'udhs_100bp_index')

    @property
    def get_index(self):
        """genome index
        """
        if hasattr(self, "s"):
            return self.get(self.s, 'bwa_index')

    @property
    def get_cluster(self):
        """only for hg38 now......"""
        if hasattr(self, "s"):
            return self.get(self.s, 'cluster')
