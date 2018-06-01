from django import forms 
from .models import GTFSForm
from django.http import JsonResponse
from django.views.generic.edit import CreateView


class AjaxableResponseMixin:
	def form_invalid(self,form):
		response = super().form_invalid(form)
		if self.request.is_ajax():
			return JsonResponse(form.errors, status=400)
		else:
			return response

	def form_valid(self, form):
		response = super().form_valid(form)
		if self.request.is_ajax():
			data = {
				'pk':self.object.pk,
			}
			return JsonResponse(data)
		else:
			return response

class GTFSInfoForm(AjaxableResponseMixin, forms.ModelForm):

    class Meta:
        model = GTFSForm
        fields = ('url','name','osm_tag','gtfs_tag','frequency')

    def __init__(self, *args, **kwargs):
    	super(GTFSInfoForm, self).__init__(*args, **kwargs)
    	self.fields['name'].widget.attrs={
    		'id'   : 'formname',
    		'name' : 'feedname',
			'label': 'formname'
    		}
    	self.fields['url'].widget.attrs={
    		'id'   : 'formurl',
    		'name' : 'feedurl'
    	}
    	self.fields['gtfs_tag'].widget.attrs={
    		'id'	:	'formgtfstag',
    		'name'	:	'feedgtfstag'
    	}
    	self.fields['osm_tag'].widget.attrs={
    		'id'	:	'formosmtag',
    		'name'	:	'feedosmtag'
    	}
    	self.fields['frequency'].widget.attrs={
    		'id'	:	'formfrequency',
    		'name'	:	'feedfrequency'
    	}