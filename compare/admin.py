from django.contrib import admin
from .models import CMP_Stop
from leaflet.admin import LeafletGeoAdmin


class CMP_StopAdmin(admin.ModelAdmin):
    list_display = ('id', 'stop', 'node')


admin.site.register(CMP_Stop, LeafletGeoAdmin)
