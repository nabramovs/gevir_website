# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class GeneScore(models.Model):
	gene_name = models.CharField(max_length=128, verbose_name='Gene Name')
	canonical_transcript = models.CharField(db_index=True, max_length=20, unique=True, verbose_name='Canonical Transcript')
	gevir_percentile = models.FloatField(verbose_name='GeVIR %')
	oe_lof_percentile = models.FloatField(verbose_name='LOEUF %')
	gevir_and_oe_lof_percentile = models.FloatField(verbose_name='VIRLoF %')
	gevir_ad_enrichment = models.FloatField(verbose_name='GeVIR AD')
	oe_lof_ad_enrichment = models.FloatField(verbose_name='LOEUF AD')
	gevir_and_oe_lof_ad_enrichment = models.FloatField(verbose_name='VIRLoF AD')
	gevir_ar_enrichment = models.FloatField(verbose_name='GeVIR AR')
	oe_lof_ar_enrichment = models.FloatField(verbose_name='LOEUF AR')
	gevir_and_oe_lof_ar_enrichment = models.FloatField(verbose_name='VIRLoF AR')

	# statistical significance test p-values (Fisher Exact)
	gevir_ad_p = models.FloatField()
	oe_lof_ad_p = models.FloatField()
	gevir_and_oe_lof_ad_p = models.FloatField()
	gevir_ar_p = models.FloatField()
	oe_lof_ar_p = models.FloatField()
	gevir_and_oe_lof_ar_p = models.FloatField()

	def __str__(self):
		return "{:s} (GeVIR %: {:0.2f}; LOEUF %: {:0.2f}; VIRLoF %: {:0.2f})".format(
			self.gene_name, self.gevir_percentile, self.oe_lof_percentile, self.gevir_and_oe_lof_percentile)


class GeneIdentifier(models.Model):
	#gene_identifier = models.CharField(max_length=128)
	gene_identifier_upper = models.CharField(db_index=True, max_length=128)
	canonical_transcript = models.CharField(max_length=20)
	main = models.BooleanField(default=False)

	def __str__(self):
		return "{:s} - {:s}".format(self.gene_identifier_upper, self.canonical_transcript)


class VariantIntolerantRegion(models.Model):
	chrom = models.CharField(max_length=2, verbose_name='Chrom')
	strand = models.CharField(max_length=1, verbose_name='Strand')
	start = models.IntegerField(verbose_name='Start')
	stop = models.IntegerField(verbose_name='Stop')
	canonical_transcript = models.CharField(max_length=20, verbose_name='Canonical Transcript')

	region_filter = models.CharField(max_length=20, verbose_name='Filter')
	length = models.IntegerField(verbose_name='Length')
	exome_coverage = models.FloatField(verbose_name='Exome Coverage')
	gerp_mean = models.FloatField(verbose_name='GERP++ (mean)')
	percentile = models.FloatField(verbose_name='Region Percentile')

	xstart = models.IntegerField(verbose_name='xStart')
	xstop = models.IntegerField(verbose_name='xStart')
	codon_xstart = models.IntegerField(verbose_name='Codon xStart')
	codon_xstop = models.IntegerField(verbose_name='Codon xStop')

	start_variant = models.CharField(max_length=50, verbose_name='Start Variant')
	start_variant_csq = models.CharField(max_length=50, verbose_name='Start Variant Consequence')
	stop_variant = models.CharField(max_length=50, verbose_name='Stop Variant')
	stop_variant_csq = models.CharField(max_length=50, verbose_name='Stop Variant Consequence')

	class Meta:
		indexes = [
			models.Index(fields=['xstart', 'xstop']),
			models.Index(fields=['codon_xstart', 'codon_xstop']),
		]

	def __str__(self):
		return "{}-{}-{}".format(self.chrom, self.start, self.stop)
		#return '-'.join([self.chrom, self.start, self.stop])


class CodingRegion(models.Model):
	canonical_transcript = models.CharField(max_length=20, verbose_name='Canonical Transcript')
	xstart = models.IntegerField(verbose_name='xStart')
	xstop = models.IntegerField(verbose_name='xStart')

	class Meta:
		indexes = [
			models.Index(fields=['xstart', 'xstop']),
		]

	def __str__(self):
		return "{}:{}-{}".format(self.canonical_transcript, self.xstart, self.xstop)