import django_filters
from gevir.models import GeneScore

# pip install django-filter~=1.1
class GeneScoreFilter(django_filters.FilterSet):
	class Meta:
		model = GeneScore
		fields = {'gene_name': ['contains']}