from django.contrib import admin
from .models import Tag,Node,KeyValueString,Way, GTFSForm

class FormAdmin(admin.ModelAdmin):
	list_display = ('id','name','url')

class TagAdmin(admin.ModelAdmin):
	display = ('tag.id')
class NodeAdmin(admin.ModelAdmin):
	list_display =('id','user')
class KeyValueStringAdmin(admin.ModelAdmin):
	display =('value')
class WayAdmin(admin.ModelAdmin):
	list_display =('id','user')
admin.site.register(Tag,TagAdmin)
admin.site.register(Node,NodeAdmin)
admin.site.register(KeyValueString,KeyValueStringAdmin)
admin.site.register(Way,WayAdmin)
admin.site.register(GTFSForm,FormAdmin)