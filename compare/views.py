from django.shortcuts import render
from typing import List, Any

from .models import CMP_Stop
from osmapp.models import Tag, KeyValueString, Node, Way, OSM_Relation
from multigtfs.models import Stop


def get_stops(request):
    # filter stops from Node table
    # highway
    # public_transport = stop_position
    stop_key = KeyValueString.objects.get(value="public_transport")
    stop_value = KeyValueString.objects.get(value="stop_position")
    stop_tag = Tag.objects.get(key=stop_key, value=stop_value)
    stop_nodes = stop_tag.node_set.all()

    '''
    While filtering with public_transport=stop_position there are 3 cases
    1. nodes may have tag with both bus=yes/tram=yes
       and highway=bus_stop/railway=tram_stop
    2. nodes may have tag only with bus=yes/tram=yes
    3. nodes may have tag only with highway=bus_stop/railway=tram_stop
    '''
    bus_nodes = []
    tram_nodes = []

    for stop_node in stop_nodes:
        tags = stop_node.tags.all()
        bus_stop_key_text = ['highway', 'bus']
        bus_stop_value_text = ['bus_stop', 'yes']
        is_bus_stop = 0

        for (sbus_stop_key_text, sbus_stop_value_text) in zip(bus_stop_key_text, bus_stop_value_text):
            bus_stop_key = KeyValueString.objects.filter(value=sbus_stop_key_text)
            bus_stop_value = KeyValueString.objects.filter(value=sbus_stop_value_text)
            if bus_stop_key.count() > 0 and bus_stop_value.count() > 0:
                is_bus_stop = tags.filter(key=bus_stop_key[0], value=bus_stop_value[0]).count()

        if is_bus_stop > 0:
            bus_nodes.append(stop_node)

        tram_stop_key_text = ['railway', 'tram']
        tram_stop_value_text = ['tram_stop', 'yes']
        is_tram_stop = 0

        for (stram_stop_key_text, stram_stop_value_text) in zip(tram_stop_key_text, tram_stop_value_text):
            tram_stop_key = KeyValueString.objects.filter(value=stram_stop_key_text)
            tram_stop_value = KeyValueString.objects.filter(value=stram_stop_value_text)
            if tram_stop_key.count() > 0 and tram_stop_value.count() > 0:
                is_tram_stop = tags.filter(key=tram_stop_key[0], value=tram_stop_value[0]).count()

        if is_tram_stop > 0:
            tram_nodes.append(stop_node)

    print(OrderedSet(bus_nodes))
    print(OrderedSet(tram_nodes))

    return render(request, 'gs/load.html')


def get_gtfs_stops(request):
    gtfs_stops = Stop.objects.all()

    for gtfs_stop in gtfs_stops:
        cmp_stop = CMP_Stop(stop=gtfs_stop)
        gtfs_stop_lat = gtfs_stop.lat
        gtfs_stop_lon = gtfs_stop.lon
        print('{} {}'.format(gtfs_stop_lon, gtfs_stop_lat))
        cmp_stop.gtfs_save_geom(gtfs_stop_lon, gtfs_stop_lat)
        # cmp_stop.save()

    return render(request, 'gs/load.html')
