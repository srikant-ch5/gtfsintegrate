from django.contrib import admin

from .models import Correspondence, Conversion


class CorrespondenceAdmin(admin.ModelAdmin):
    display = 'id'


class ConversionAdmin(admin.ModelAdmin):
    display = 'id'


admin.site.register(Correspondence, CorrespondenceAdmin)
admin.site.register(Conversion, ConversionAdmin)
