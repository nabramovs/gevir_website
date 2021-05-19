import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gevir_website.settings')

import django
django.setup()
import csv
import progressbar # pip install progressbar2
from gevir.models import GeneScore, GeneIdentifier
from gevir.models import VariantIntolerantRegion, CodingRegion

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def file_len(fname):
	"""Calculate length of a file."""
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i + 1


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def read_gene_identifiers(other=False):
	if other:
		gene_identifiers_csv = os.path.join(DATA_DIR, 'gene_identifiers_other.csv')
	else:
		gene_identifiers_csv = os.path.join(DATA_DIR, 'gene_identifiers.csv')
	input_file = open(gene_identifiers_csv, 'rt')
	reader = csv.reader(input_file)

	headers = next(reader)
	gene_identifier_upper_index = headers.index('gene_identifier_upper')
	canonical_transcript_index = headers.index('canonical_transcript')
	main_index = headers.index('main')

	gene_identifiers_upper = {}
	gene_identifiers_upper_other = {}
	for row in reader:
		gene_identifier_upper = row[gene_identifier_upper_index]
		canonical_transcript = row[canonical_transcript_index]
		main = str2bool(row[main_index])

		if main: # confident match
			if canonical_transcript not in gene_identifiers_upper:
				gene_identifiers_upper[canonical_transcript] = [gene_identifier_upper]
			else:
				gene_identifiers_upper[canonical_transcript].append(gene_identifier_upper)
		else: # alternative names
			if canonical_transcript not in gene_identifiers_upper_other:
				gene_identifiers_upper_other[canonical_transcript] = [gene_identifier_upper]
			else:
				gene_identifiers_upper_other[canonical_transcript].append(gene_identifier_upper)

	return gene_identifiers_upper, gene_identifiers_upper_other


def populate_gene_scores():
	gene_identifiers_upper_dict, gene_identifiers_upper_other_dict = read_gene_identifiers()

	gene_scores_csv = os.path.join(DATA_DIR, 'gene_scores.csv')
	row_num = file_len(gene_scores_csv)

	input_file = open(gene_scores_csv, 'rt')
	reader = csv.reader(input_file)	
	headers = next(reader)

	gene_name_index = headers.index('gene_name')
	canonical_transcript_index = headers.index('canonical_transcript')
	gevir_percentile_index = headers.index('gevir_percentile')
	oe_lof_percentile_index = headers.index('loeuf_percentile')
	gevir_and_oe_lof_percentile_index = headers.index('virlof_percentile')
	gevir_ad_enrichment_index = headers.index('gevir_ad_enrichment')
	oe_lof_ad_enrichment_index = headers.index('loeuf_ad_enrichment')
	gevir_and_oe_lof_ad_enrichment_index = headers.index('virlof_ad_enrichment')
	gevir_ar_enrichment_index = headers.index('gevir_ar_enrichment')	
	oe_lof_ar_enrichment_index = headers.index('loeuf_ar_enrichment')
	gevir_and_oe_lof_ar_enrichment_index = headers.index('virlof_ar_enrichment')

	gevir_ad_p_index = headers.index('gevir_ad_p')
	oe_lof_ad_p_index = headers.index('loeuf_ad_p')
	gevir_and_oe_lof_ad_p_index = headers.index('virlof_ad_p')
	gevir_ar_p_index = headers.index('gevir_ar_p')
	oe_lof_ar_p_index = headers.index('loeuf_ar_p')
	gevir_and_oe_lof_ar_p_index = headers.index('virlof_ar_p')

	total_lines = row_num
	line_number = 0
	bar = progressbar.ProgressBar(maxval=1.0).start()

	gene_scores = []
	gene_identifiers = []
	for row in reader:
		gene_score = GeneScore(
			gene_name=row[gene_name_index],
			canonical_transcript=row[canonical_transcript_index],
			gevir_percentile=row[gevir_percentile_index],
			oe_lof_percentile=row[oe_lof_percentile_index],
			gevir_and_oe_lof_percentile=row[gevir_and_oe_lof_percentile_index],
			gevir_ad_enrichment=row[gevir_ad_enrichment_index],
			oe_lof_ad_enrichment=row[oe_lof_ad_enrichment_index],
			gevir_and_oe_lof_ad_enrichment=row[gevir_and_oe_lof_ad_enrichment_index],
			gevir_ar_enrichment=row[gevir_ar_enrichment_index],
			oe_lof_ar_enrichment=row[oe_lof_ar_enrichment_index],
			gevir_and_oe_lof_ar_enrichment=row[gevir_and_oe_lof_ar_enrichment_index],

			gevir_ad_p=row[gevir_ad_p_index],
			oe_lof_ad_p=row[oe_lof_ad_p_index],
			gevir_and_oe_lof_ad_p=row[gevir_and_oe_lof_ad_p_index],
			gevir_ar_p=row[gevir_ar_p_index],
			oe_lof_ar_p=row[oe_lof_ar_p_index],
			gevir_and_oe_lof_ar_p=row[gevir_and_oe_lof_ar_p_index],
		)
		#gene_score.save()
		gene_scores.append(gene_score)

		gene_ids = gene_identifiers_upper_dict[gene_score.canonical_transcript]
		for gene_id in gene_ids:
			gene_identifier = GeneIdentifier(
				gene_identifier_upper=gene_id,
				canonical_transcript=gene_score.canonical_transcript, # gene_score use gene score if linked by foreign keys
				main=True
			)
			#gene_identifier.save()
			gene_identifiers.append(gene_identifier)

		# Alternative names
		if gene_score.canonical_transcript in gene_identifiers_upper_other_dict:
			gene_ids = gene_identifiers_upper_other_dict[gene_score.canonical_transcript]
			for gene_id in gene_ids:
				gene_identifier = GeneIdentifier(
					gene_identifier_upper=gene_id,
					canonical_transcript=gene_score.canonical_transcript, # gene_score use gene score if linked by foreign keys
					main=False
				)
				#gene_identifier.save()
				gene_identifiers.append(gene_identifier)

		line_number += 1
		bar.update((line_number + 0.0) / total_lines)
	bar.finish()

	GeneScore.objects.bulk_create(gene_scores)
	GeneIdentifier.objects.bulk_create(gene_identifiers)


def populate_regions():
	# import coding regions
	
	coding_regions_csv = os.path.join(DATA_DIR, 'coding_regions.csv')

	input_file = open(coding_regions_csv, 'rt')
	reader = csv.reader(input_file)
	headers = next(reader)

	canonical_transcript_index = headers.index('transcript_id')
	xstart_index = headers.index('xstart')
	xstop_index = headers.index('xstop')
	coding_regions = []
	for row in reader:
		coding_region = CodingRegion(
			canonical_transcript=row[canonical_transcript_index],
			xstart=row[xstart_index],
			xstop=row[xstop_index],
		)
		coding_regions.append(coding_region)
	CodingRegion.objects.bulk_create(coding_regions)

	# import variant intolerant regions

	regions_csv = os.path.join(DATA_DIR, 'regions.csv')
	row_num = file_len(regions_csv)

	input_file = open(regions_csv, 'rt')
	reader = csv.reader(input_file)	
	headers = next(reader)

	chrom_index = headers.index('chrom')
	strand_index = headers.index('strand')
	start_index = headers.index('start')
	stop_index = headers.index('stop')
	canonical_transcript_index = headers.index('transcript_id')
	region_filter_index = headers.index('region_flag')
	length_index = headers.index('length')
	exome_coverage_index = headers.index('exome_coverage')
	gerp_mean_index = headers.index('gerp_mean')
	percentile_index = headers.index('percentile')
	xstart_index = headers.index('xstart')
	xstop_index = headers.index('xstop')
	codon_xstart_index = headers.index('codon_xstart')
	codon_xstop_index = headers.index('codon_xstop')
	start_variant_index = headers.index('start_variant')
	start_variant_csq_index = headers.index('start_variant_csq')
	stop_variant_index = headers.index('stop_variant')
	stop_variant_csq_index = headers.index('stop_variant_csq')

	virs = []
	total_lines = row_num
	line_number = 0
	bar = progressbar.ProgressBar(maxval=1.0).start()
	for row in reader:
		vir = VariantIntolerantRegion(
			chrom = row[chrom_index],
			strand = row[strand_index],
			start = row[start_index],
			stop = row[stop_index],
			canonical_transcript = row[canonical_transcript_index],
			region_filter = row[region_filter_index],
			length = row[length_index],
			exome_coverage = row[exome_coverage_index],
			gerp_mean = row[gerp_mean_index],
			percentile = row[percentile_index],
			xstart = row[xstart_index],
			xstop = row[xstop_index],
			codon_xstart = row[codon_xstart_index],
			codon_xstop = row[codon_xstop_index],
			start_variant = row[start_variant_index],
			start_variant_csq = row[start_variant_csq_index],
			stop_variant = row[stop_variant_index],
			stop_variant_csq = row[stop_variant_csq_index],
		)
		virs.append(vir)

		line_number += 1
		bar.update((line_number + 0.0) / total_lines)
	bar.finish()

	VariantIntolerantRegion.objects.bulk_create(virs)


# Start execution here!
if __name__ == '__main__':
	# use "python manage.py flush" to clean existing database 
	# use "python manage.py createsuperuser" to create admin
	print("Starting Gevir population script...")
	print("Importing gene scores...")
	#populate_gene_scores()
	print("Importing regions...")
	#populate_regions()