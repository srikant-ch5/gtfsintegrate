from django.shortcuts import render

from multigtfs.models import Stop, Feed
from django.db import connection
from .models import CMP_Stop
import json
from gs.tasks import save_comp


def get_nodes_within100m(lon, loat):
    query = "SELECT * FROM osmapp_node WHERE ST_DWithin(geom, 'Point({0} {1})', 100)".format(lon, lat)  # lon, lat
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    return result


def showmap_with_comp(request, pk):
    context = {
        'type': 'conversion_view',
        'feed_id': pk,
        'feed_name': Feed.objects.get(id=pk).name,
        'error': 'No errors'
    }

    # 1. Load all stops first
    try:
        stops = Stop.objects.filter(feed=pk)
    except Exception as e:
        context['error'] = 'No stops present'

    # Initially comparision should be done by the user
    try:
        for stop in stops:
            # osm_nodes_in_bound = get_nodes_within100m(str(stop.lon),str(stop.lat))
            if not CMP_Stop.objects.filter(gtfs_stop=stop).exists():
                comp_stop = CMP_Stop.objects.create(gtfs_stop=stop)
                comp_stop.save()
    except Exception as e:
        context['error'] = e

    '''                
    #to be executed if the matching needs to be done by the app
    for stop in stops:
        nodes = get_nodes_within100m(str(stop.lon),str(stop.lat))

        # create a cmp_stop data
        if CMP_Stop.objects.filter(gtfs_stop=stop).exists():
            comp_stop = CMP_Stop.objects.get(gtfs_stop=stop)
            if len(result) > 0:
                for osm_node_info in result:
                    osm_node = Node.objects.get(id=osm_node_info[0])
                    comp_stop.probable_matched_stops.add(osm_node)
                    comp_stop.save()
        else:
            comp_stop = CMP_Stop.objects.create(gtfs_stop=stop, matching_type='LOCATION')
            comp_stop.save()'''

    return render(request, 'gs/comparision.html', {'context': context})


def match_stop(request):
    if request.method == 'POST':
        context = {
            'match_success': 0,
            'error': ''
        }

        gtfs_stop_data = request.POST.get('gtfs_stop')
        osm_stop_id = request.POST.get('osm_stop')
        tags_json  = request.POST.get('tags')
        tags_data = json.loads(tags_json)

        str = gtfs_stop_data.split('-')
        gtfs_feed_id = str[0]
        gtfs_stop_id = str[1]
        save_comp(gtfs_feed_id, gtfs_stop_id, osm_stop_id, tags_data)

    return render(request, 'gs/comparision.html')


def match_stops(request):
    if request.method == 'POST':

        context = {
            'match_success': 0,
            'error': ''
        }

        data_in_string = request.POST.get('match_data')
        tags_json = request.POST.get('tags')
        tags_data = json.loads(tags_json)
        print(tags_data)
        json_data = json.loads(data_in_string)
        for i in range(0, len(json_data)):
            str = json_data[i]['gtfs_stop'].split('-')
            gtfs_feed_id = str[0]
            gtfs_stop_id = str[1]
            osm_stop_id = json_data[i]['osm_stop']

            context['match_success'], context['error'] = save_comp(gtfs_feed_id, gtfs_stop_id, osm_stop_id)

    return render(request, 'gs/comparision.html', {'context': context})
