from rest_framework import serializers
from gs.models import GTFSForm


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
