from django.contrib import admin
from .models import GTFSForm

class FormAdmin(admin.ModelAdmin):
	list_display = ('id','name','url')

admin.site.register(GTFSForm,FormAdmin)