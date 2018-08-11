from django.contrib import admin

from conversionapp.models import Correspondence_Route, Correspondence_Agency
from .models import Relation_data

class CorrespondenceRouteAdmin(admin.ModelAdmin):
    display = 'id'


class CorrespondenceAgencyAdmin(admin.ModelAdmin):
    display = 'id'

class RelationdataAdmin(admin.ModelAdmin):
    display = 'id'


admin.site.register(Correspondence_Route, CorrespondenceRouteAdmin)
admin.site.register(Correspondence_Agency, CorrespondenceAgencyAdmin)
admin.site.register(Relation_data, RelationdataAdmin)
