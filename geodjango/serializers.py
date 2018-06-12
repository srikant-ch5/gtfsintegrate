from rest_framework import serializers
from gs.models import GTFSForm
from multigtfs.models import Stop


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = GTFSForm
        fields = [
            'url',
            'name',
            'osm_tag',
            'gtfs_tag',
            'timestamp',
            'frequency',
            'feed'
        ]


class GTFS_Stop_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = [
            'feed',
            'stop_id',
            'name',
            'lat',
            'lon',
            'location_type',
        ]
