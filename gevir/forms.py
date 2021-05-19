from django import forms

class Search(forms.Form):
	gene_identifiers = forms.CharField(label='', widget=forms.Textarea)

class VariantSearch(forms.Form):
	variants = forms.CharField(label='', widget=forms.Textarea)