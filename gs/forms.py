from django import forms
from .models import GTFSForm
from django.http import JsonResponse
from django.views.generic.edit import CreateView
from leaflet.forms.widgets import LeafletWidget
from multigtfs.models import Stop



class GTFSInfoForm(forms.ModelForm):
    class Meta:
        model = GTFSForm
        fields = ('url', 'name', 'osm_tag', 'gtfs_tag', 'frequency')

    def __init__(self, *args, **kwargs):
        super(GTFSInfoForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {
            'id': 'formname',
            'name': 'feedname',
            'label': 'formname'
        }
        self.fields['url'].widget.attrs = {
            'id': 'formurl',
            'name': 'feedurl'
        }
        self.fields['gtfs_tag'].widget.attrs = {
            'id': 'formgtfstag',
            'name': 'feedgtfstag'
        }
        self.fields['osm_tag'].widget.attrs = {
            'id': 'formosmtag',
            'name': 'feedosmtag'
        }
        self.fields['frequency'].widget.attrs = {
            'id': 'formfrequency',
            'name': 'feedfrequency'
        }
