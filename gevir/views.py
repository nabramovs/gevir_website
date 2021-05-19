# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django_tables2 import RequestConfig
from django_tables2.export.export import TableExport
from django_tables2.export.views import ExportMixin

from gevir.models import GeneScore, GeneIdentifier
from gevir.models import CodingRegion, VariantIntolerantRegion
from gevir.forms import Search, VariantSearch
from gevir.tables import GeneScoreTable, VirTable, VariantVir
from gevir.filters import GeneScoreFilter
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


# Create your views here.
def index(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = Search(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required and redirect to a new URL:
			request.session['input_data'] = form.cleaned_data['gene_identifiers'] 
			return HttpResponseRedirect(reverse('results'))
	# if a GET (or any other method) we'll create a blank form
	else:
		form = Search()

	return render(request, 'gevir/index.html', {'form': form})

	#context_dict = {'boldmessage': "Scores, scores, RANKS!"}
	#return render(request, 'gevir/index.html', context=context_dict)


def results(request):
	if 'input_data' in request.session:
		input_data = request.session['input_data']
		input_gene_identifiers = []
		for line in input_data.split('\n'):
			input_gene_identifiers.append(line.strip(' \t\n\r').upper())

		#found_transcript_ids = ['ENST00000252034', 'ENST00000379887', 'ENST00000265689']
		'''
		found_transcript_ids = GeneIdentifier.objects.filter(gene_identifier_upper__in=input_gene_identifiers).values_list('canonical_transcript', flat=True)
		found_gene_identifiers = GeneIdentifier.objects.filter(gene_identifier_upper__in=input_gene_identifiers).values_list('gene_identifier_upper', flat=True)
		not_found_gene_identifiers = set(input_gene_identifiers) - set(found_gene_identifiers)
		not_found_gene_identifiers_string = ', '.join(not_found_gene_identifiers)
		'''
		
		main_found_transcript_ids = GeneIdentifier.objects.filter(gene_identifier_upper__in=input_gene_identifiers, main=True).values_list('canonical_transcript', flat=True)
		main_found_gene_identifiers = GeneIdentifier.objects.filter(gene_identifier_upper__in=input_gene_identifiers, main=True).values_list('gene_identifier_upper', flat=True)
		main_not_found_gene_identifiers = set(input_gene_identifiers) - set(main_found_gene_identifiers)

		alternative_found_transcript_ids = GeneIdentifier.objects.filter(gene_identifier_upper__in=main_not_found_gene_identifiers, main=False).values_list('canonical_transcript', flat=True)
		alternative_found_gene_identifiers = GeneIdentifier.objects.filter(gene_identifier_upper__in=main_not_found_gene_identifiers, main=True).values_list('gene_identifier_upper', flat=True)
		alternative_not_found_gene_identifiers = main_not_found_gene_identifiers - set(alternative_found_gene_identifiers)

		not_found_gene_identifiers_string = ', '.join(alternative_not_found_gene_identifiers)

		found_transcript_ids = list(main_found_transcript_ids) + list(alternative_found_transcript_ids)

		gene_scores = GeneScore.objects.order_by('gevir_percentile').filter(canonical_transcript__in=found_transcript_ids)
	else:
		gene_scores = GeneScore.objects.order_by('gevir_percentile')
		not_found_gene_identifiers_string = ''

	#table = GeneScoreTable(gene_scores)
	f = GeneScoreFilter(request.GET, queryset=gene_scores)
	#table = GeneScoreTable(f.queryset)

	if request.method == "GET":
		list1=list()
		#print len(f.qs)
		for obj in f.qs:
			#print obj
			list1.append(obj)

		#print 'AAAA', obj
		table=GeneScoreTable(list1)


	RequestConfig(request).configure(table)

	export_format = request.GET.get('_export', None)
	if TableExport.is_valid_format(export_format):
		exporter = TableExport(export_format, table)
		return exporter.response('table.{}'.format(export_format))

	return render(request, 'gevir/results.html', {'table': table, 'not_found_gene_identifiers': not_found_gene_identifiers_string, 'filter': f})


def clear_gene_search(request):
	request.session.pop('input_data', None)
	return HttpResponseRedirect(reverse('results'))	


def variant_search(request):
	# if this is a POST request we need to process the form data
	if request.method == 'POST':
		# create a form instance and populate it with data from the request:
		form = VariantSearch(request.POST)
		# check whether it's valid:
		if form.is_valid():
			# process the data in form.cleaned_data as required and redirect to a new URL:
			request.session['input_variants'] = form.cleaned_data['variants'] 
			return HttpResponseRedirect(reverse('variant_regions'))
	# if a GET (or any other method) we'll create a blank form
	else:
		form = VariantSearch()

	return render(request, 'gevir/variant_search.html', {'form': form})

# Borrowed from gnomAD Browser
CHROMOSOMES = [str(x) for x in range(1, 23)]
CHROMOSOMES.extend(['X', 'Y', 'M'])
CHROMOSOME_TO_CODE = { item: i+1 for i, item in enumerate(CHROMOSOMES) }

# Borrowed from gnomAD Browser
def get_xpos(chrom, pos):
	return CHROMOSOME_TO_CODE[chrom] * int(1e9) + int(pos)

'''
# Borrowed from gnomAD Browser
def get_xpos(chrom, pos):
    if not chrom.startswith('chr'):
        chrom = 'chr{}'.format(chrom)
    return get_single_location(chrom, int(pos))
'''

def string_is_int(s):
	try: 
		int(s)
		return True
	except ValueError:
		return False

def get_variant_xpos(variant):
	xpos = 0
	is_variant_valid = True
	variant_parts = variant.split('-')
	if len(variant_parts) < 2:
		is_variant_valid = False
	elif variant_parts[0] not in CHROMOSOMES:
		is_variant_valid = False
	elif not string_is_int(variant_parts[1]):
		is_variant_valid = False
	else:
		xpos = get_xpos(variant_parts[0], variant_parts[1])
	return xpos, is_variant_valid



def variant_regions(request):
	if 'input_variants' in request.session and not ('processed_variants' in request.session and request.session['processed_variants'] == request.session['input_variants']):
	# CodingRegion VariantIntolerantRegion
	#if 'input_variants' in request.session:
		input_variants = request.session['input_variants']
		input_variants = input_variants.split('\n')
		input_variants = input_variants[:50]
		
		variant_xposes = OrderedDict()
		not_valid_variants = []
		for variant in input_variants:
			variant = variant.strip(' \t\n\r')
			xpos, is_variant_valid = get_variant_xpos(variant)

			if is_variant_valid:
				variant_xposes[variant] = xpos
			else:
				not_valid_variants.append(variant)

		request.session['processed_variants'] = request.session['input_variants']
		request.session['not_valid_variants'] = ', '.join(not_valid_variants)

		non_found_variants = []
		variant_flags = OrderedDict()
		variant_regions = OrderedDict()
		variant_region_data = []

		variant_virs = []
		for variant_id, xpos in variant_xposes.iteritems():
			is_in_region = False
			#coding_regions = CodingRegion.objects.filter(xstart__lte=xpos, xstop__gte=xpos)
			coding_regions = 'ok'
			if coding_regions:
				print variant_id
				virs = VariantIntolerantRegion.objects.filter(xstart__lte=xpos, xstop__gte=xpos)
				if virs:
					is_in_region = True
					for vir in virs:
						variant_vir = VariantVir()
						flag = 'BORDER CODON'

						if xpos > vir.codon_xstart and xpos < vir.codon_xstop:
							flag = 'INSIDE CODON'

						variant_vir.variant_id = variant_id
						variant_vir.flag = flag
						'''
						variant_vir.chrom = vir.chrom
						variant_vir.strand = vir.strand
						variant_vir.start = vir.start
						variant_vir.stop = vir.stop
						'''
						variant_vir.region = "{}:{}-{} ({})".format(vir.chrom, vir.start, vir.stop, vir.strand)
						variant_vir.canonical_transcript = vir.canonical_transcript
						variant_vir.exome_coverage = vir.exome_coverage
						variant_vir.region_filter = vir.region_filter
						variant_vir.length = vir.length
						variant_vir.gerp_mean = vir.gerp_mean
						variant_vir.percentile = vir.percentile

						variant_virs.append(variant_vir.get_dictionary())

			if not is_in_region:
				print 'aaaaaaaaaaaaaaaaaa!!!!!!!!!!!!!!'

				variant_vir = VariantVir()
				variant_vir.variant_id = variant_id
				variant_vir.flag = 'NOT FOUND'
				variant_virs.append(variant_vir.get_dictionary())

		request.session['variant_virs'] = variant_virs

	table = VirTable(request.session['variant_virs'])
	#f = GeneScoreFilter(request.GET, queryset=gene_scores)
	RequestConfig(request).configure(table)

	export_format = request.GET.get('_export', None)
	if TableExport.is_valid_format(export_format):
		exporter = TableExport(export_format, table)
		return exporter.response('table.{}'.format(export_format))

	return render(request, 'gevir/variant_regions.html', {'table': table})

	#return render(request, 'gevir/variant_regions.html')


def faq(request):
	return render(request, 'gevir/faq.html')

def download(request):
	return render(request, 'gevir/download.html')

def cite(request):
	return render(request, 'gevir/cite.html')

def terms(request):
	return render(request, 'gevir/terms.html')

'''
1-55505545-C-T
1-55505549-C-T

'''