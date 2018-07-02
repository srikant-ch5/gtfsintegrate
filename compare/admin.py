from django.contrib import admin
from .models import CMP_Stop

class CMPStopAdmin(admin.ModelAdmin):
    display = ('id')

admin.site.register(CMP_Stop, CMPStopAdmin)
