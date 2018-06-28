from django import forms
from .models import GTFSForm
from django.http import JsonResponse
from django.views.generic.edit import CreateView
from leaflet.forms.widgets import LeafletWidget
from multigtfs.models import Stop
from conversionapp.models import Correspondence


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


class CorrespondenceForm(forms.ModelForm):
    class Meta:
        model = Correspondence
        fields = ('feed_id','stop_id', 'stop_code', 'stop_name', 'stop_desc', 'stop_zone', 'stop_url', \
                  'stop_location_type', 'stop_parent_station', 'stop_timezone', \
                  'agency_name', 'agency_id', 'agency_url', 'agency_timezone', \
                  'agency_lang', 'agency_phone', 'agency_fare_url')

    def __init__(self, *args, **kwargs):
        super(CorrespondenceForm, self).__init__(*args, **kwargs)
        self.fields['feed_id'].widget.attrs = {
            'id': 'feed_id',
            'name': 'Feed ID(GTFS)',
        }
        self.fields['stop_id'].widget.attrs = {
            'id': 'stop_id',
            'name': 'Stop ID(GTFS)',
        }
        self.fields['stop_code'].widget.attrs = {
            'id': 'stop_code',
            'name': 'Stop Code'
        }
        self.fields['stop_name'].widget.attrs = {
            'id': 'stop_name',
            'name': 'Stop name'
        }
        self.fields['stop_desc'].widget.attrs = {
            'id': 'stop_desc',
            'name': 'Stop desc'
        }
        self.fields['stop_zone'].widget.attrs = {
            'id': 'stop_zone_key',
            'name': 'Stop zone'
        }
        self.fields['stop_url'].widget.attrs = {
            'id': 'stop_url',
            'name': 'Stop url'
        }
        self.fields['stop_location_type'].widget.attrs = {
            'id': 'stop_location_type',
            'name': 'Stop location type'
        }
        self.fields['stop_parent_station'].widget.attrs = {
            'id': 'stop_parent_station',
            'name': 'Stop parent station'
        }
        self.fields['stop_timezone'].widget.attrs = {
            'id': 'stop_timezone',
            'name': 'Stop timezone'
        }
        self.fields['agency_name'].widget.attrs = {
            'id': 'agency_name',
            'name': 'Agency name'
        }
        self.fields['agency_id'].widget.attrs = {
            'id': 'agency_id',
            'name': 'Agency id'
        }
        self.fields['agency_url'].widget.attrs = {
            'id': 'agency_url',
            'name': 'Agency url'
        }
        self.fields['agency_timezone'].widget.attrs = {
            'id': 'agency_timezone',
            'name': 'Agency timezone'
        }
        self.fields['agency_lang'].widget.attrs = {
            'id': 'agency_lang',
            'name': 'Agency lang'
        }
        self.fields['agency_phone'].widget.attrs = {
            'id': 'agency_phone',
            'name': 'Agency phone'
        }
        self.fields['agency_fare_url'].widget.attrs = {
            'id': 'agency_fare_url',
            'name': 'Agency fare url'
        }
