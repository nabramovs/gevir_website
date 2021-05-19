# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from gevir.models import GeneScore, GeneIdentifier
from gevir.models import VariantIntolerantRegion, CodingRegion

# Register your models here.

admin.site.register(GeneScore)
admin.site.register(GeneIdentifier)
admin.site.register(VariantIntolerantRegion)
admin.site.register(CodingRegion)