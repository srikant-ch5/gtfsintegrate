from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import Tag, Node, KeyValueString, Way, OSM_Relation, Bounds


class FeedBoundsAdmin(admin.ModelAdmin):
    display = 'operator_name'


class TagAdmin(admin.ModelAdmin):
    display = 'tag.id'


class KeyValueStringAdmin(admin.ModelAdmin):
    display = 'value'


class RelationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


admin.site.register(Bounds, FeedBoundsAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Node, LeafletGeoAdmin)
admin.site.register(Way, LeafletGeoAdmin)
admin.site.register(KeyValueString, KeyValueStringAdmin)
admin.site.register(OSM_Relation, RelationAdmin)
