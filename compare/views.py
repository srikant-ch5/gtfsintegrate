from django.shortcuts import render
from typing import List, Any

from osmapp.models import Tag, KeyValueString, Node, Way, OSM_Relation
from multigtfs.models import Stop
from django.db import connection

def showmap_with_comp(request, pk):
    context = {
        'type': 'conversion_view',
        'feed_id':pk,
        'error':'No errors'
    }

    #1. Load all stops first
    try:
        stops = Stop.objects.filter(feed=pk)
    except Exception as e:
        context['error'] = 'No stops present'

    #2. for all the stops get osm stops that lies in 400m
    query = "SELECT * FROM osmapp_node WHERE ST_DWithin(geom, 'POINT(23.9492771 54.1362744)', 100)"#lon, lat
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    print(result)

    #2. Match using names



    return render(request, 'gs/load.html', {'context': context})
