from django.shortcuts import render
from typing import List, Any

from osmapp.models import Tag, KeyValueString, Node, Way, OSM_Relation
from multigtfs.models import Stop
from django.db import connection


def showmap_with_comp(request, pk):
    context = {
        'type': 'conversion_view',
        'feed_id': pk,
        'error': 'No errors'
    }

    # 1. Load all stops first
    try:
        stops = Stop.objects.filter(feed=pk)
    except Exception as e:
        context['error'] = 'No stops present'

    # 2. for all the stops get osm stops that lies in 100m
    try:
        for stop in stops:
            query = query = "SELECT * FROM osmapp_node WHERE ST_DWithin(geom, 'Point({0} {1})', 100)".format(
                str(stop.lon), str(stop.lat))  # lon, lat
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            print('{0} {1}'.format(stop.stop_id, result))
    except Exception as e:
        print(e)

    # 2. Match using names

    return render(request, 'gs/load.html', {'context': context})
