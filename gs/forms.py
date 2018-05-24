from django import forms 
from .models import GTFSForm

class GTFSInfoForm(forms.ModelForm):

	class Meta:
		model = GTFSForm
		fields = ('name','url','osm_tag','gtfs_tag','frequency')