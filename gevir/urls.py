from django.conf.urls import url
from gevir import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^results/$', views.results, name='results'), #ResultsView.as_view() # views.results
	url(r'^variant_search/$', views.variant_search, name='variant_search'),
	url(r'^variant_regions/$', views.variant_regions, name='variant_regions'),
	url(r'^faq/$', views.faq, name='faq'),
	url(r'^download/$', views.download, name='download'),
	url(r'^cite/$', views.cite, name='cite'),
	url(r'^terms/$', views.terms, name='terms'),
	url(r'^clear_gene_search/$', views.clear_gene_search, name='clear_gene_search'),
]
