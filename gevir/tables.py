import django_tables2 as tables
from django_tables2.export.views import ExportMixin
from django_tables2.views import SingleTableMixin
from gevir.models import GeneScore
from collections import OrderedDict

C_DARK_GREEN = '#5c7943'
C_LIGHT_GREEN = '#abcb42'
C_YELLOW = '#fee71b'
C_ORANGE = '#feae17'
C_RED = '#f35001'

def get_column_attr(fold_enrichment, p_value):
    column_attr = {'td': {'align': 'center'}}
    if p_value < 0.00001:
        column_attr['td']['style'] = 'font-weight:bold'

    if fold_enrichment < 0.33:
        column_attr['td']['bgcolor'] = C_DARK_GREEN
    elif fold_enrichment < 0.66:
        column_attr['td']['bgcolor'] = C_LIGHT_GREEN
    elif fold_enrichment < 1.5:
        column_attr['td']['bgcolor'] = C_YELLOW
    elif fold_enrichment < 3:
        column_attr['td']['bgcolor'] = C_ORANGE
    else:
        column_attr['td']['bgcolor'] = C_RED
    return column_attr


class GeneScoreTable(ExportMixin, tables.Table):
    class Meta:
        model = GeneScore
        template_name = 'django_tables2/gene_score_table.html'

        exclude = ['id', 'gevir_ad_p', 'oe_lof_ad_p', 'gevir_and_oe_lof_ad_p',
                   'gevir_ar_p', 'oe_lof_ar_p', 'gevir_and_oe_lof_ar_p']

        export_name = 'gevir_results'

    column_attr = {'td': {'align': 'center'}}


    def render_gevir_percentile(self, record, column):
        column.attrs = self.column_attr
        return '%.2f' % record.gevir_percentile

    def render_oe_lof_percentile(self, record, column):
        column.attrs = self.column_attr
        return '%.2f' % record.oe_lof_percentile

    def render_gevir_and_oe_lof_percentile(self, record, column):
        column.attrs = self.column_attr
        return '%.2f' % record.gevir_and_oe_lof_percentile

    def render_gevir_ad_enrichment(self, record, column):
        column.attrs = get_column_attr(record.gevir_ad_enrichment, record.gevir_ad_p)
        return '%.2f' % record.gevir_ad_enrichment

    def render_oe_lof_ad_enrichment(self, record, column):
        column.attrs = get_column_attr(record.oe_lof_ad_enrichment, record.oe_lof_ad_p)
        return '%.2f' % record.oe_lof_ad_enrichment

    def render_gevir_and_oe_lof_ad_enrichment(self, record, column):
        column.attrs = get_column_attr(record.gevir_and_oe_lof_ad_enrichment, record.gevir_and_oe_lof_ad_p)
        return '%.2f' % record.gevir_and_oe_lof_ad_enrichment

    def render_gevir_ar_enrichment(self, record, column):
        column.attrs = get_column_attr(record.gevir_ar_enrichment, record.gevir_ar_p)
        return '%.2f' % record.gevir_ar_enrichment

    def render_oe_lof_ar_enrichment(self, record, column):
        column.attrs = get_column_attr(record.oe_lof_ar_enrichment, record.oe_lof_ar_p)
        return '%.2f' % record.oe_lof_ar_enrichment

    def render_gevir_and_oe_lof_ar_enrichment(self, record, column):
        #column.attrs = self.column_attr
        column.attrs = get_column_attr(record.gevir_and_oe_lof_ar_enrichment, record.gevir_and_oe_lof_ar_p)
        return '%.2f' % record.gevir_and_oe_lof_ar_enrichment

class VariantVir():
    def __init__(self):
        self.variant_id = ''
        self.flag = ''
        '''
        self.chrom = ''
        self.strand = ''
        self.start = 0
        self.stop = 0
        '''
        self.region = ''
        self.canonical_transcript = ''
        self.exome_coverage = 0.0
        self.region_filter = ''
        self.length = 0
        self.gerp_mean = 0.0
        self.percentile = 100

    def get_dictionary(self):
        dictionary = OrderedDict()
        dictionary['variant_id'] = self.variant_id
        dictionary['flag'] = self.flag
        '''
        dictionary['chrom'] = self.chrom
        dictionary['strand'] = self.strand
        dictionary['start'] = self.start
        dictionary['stop'] = self.stop
        '''
        dictionary['region'] = self.region
        dictionary['canonical_transcript'] = self.canonical_transcript
        dictionary['exome_coverage'] = self.exome_coverage
        dictionary['region_filter'] = self.region_filter
        dictionary['length'] = self.length
        dictionary['gerp_mean'] = self.gerp_mean
        dictionary['percentile'] = self.percentile
        return dictionary


class VirTable(ExportMixin, tables.Table):
    class Meta:
        template_name = 'django_tables2/vir_table.html'

    variant_id = tables.Column(verbose_name='Variant ID')
    flag = tables.Column(verbose_name='Flag')
    '''
    chrom = tables.Column()
    strand = tables.Column()
    start = tables.Column()
    stop = tables.Column()
    '''
    region = tables.Column(verbose_name='Location')
    canonical_transcript = tables.Column(verbose_name='Canonical Transcript')
    exome_coverage = tables.Column(verbose_name='Coveage')
    region_filter = tables.Column(verbose_name='Filter')
    length = tables.Column(verbose_name='Length')
    gerp_mean = tables.Column(verbose_name='GERP++')
    percentile = tables.Column(verbose_name='Percentile %')

    column_attr = {'td': {'align': 'center'}}

    def render_exome_coverage(self, record, column):
        #column.attrs = self.column_attr
        return '%.2f' % record['exome_coverage']

    def render_length(self, record, column):
        #column.attrs = self.column_attr
        return '%.2f' % record['length']

    def render_gerp_mean(self, record, column):
        #column.attrs = self.column_attr
        return '%.2f' % record['gerp_mean']

    def render_percentile(self, record, column):
        #column.attrs = self.column_attr
        return '%.2f' % record['percentile']