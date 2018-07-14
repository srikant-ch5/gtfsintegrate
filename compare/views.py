from django.shortcuts import render

from multigtfs.models import Stop, Feed, Route, Agency
from django.db import connection
from .models import CMP_Stop
import json
from gs.tasks import save_comp, connect_to_JOSM
from conversionapp.models import Correspondence, ExtraField, Correspondence_Route, Correspondence_Agency
from gs.forms import Correspondence_Route_Form, Correspondence_Agency_Form


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

    # Initially comparison should be done by the user
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

    return render(request, 'gs/comparison.html', {'context': context})


def match_stop(request):
    if request.method == 'POST':
        context = {
            'match_success': 0,
            'error': ''
        }

        data_to_match_json = request.POST.get('data_to_match')
        data_to_match = json.loads(data_to_match_json)

        print(data_to_match)

        feed_id = data_to_match[0]['feed_id']
        gtfs_stop_data = data_to_match[0]['gtfs']
        osm_stop_data = data_to_match[0]['osm']

        generator = 'Python Script'
        outputparams = {
            'newline': '\n',
            'indent': ' ',
            'upload': '',
            'generator': " generator='{}'".format(generator)
        }

        xml = '''<?xml version='1.0' encoding='UTF-8' ?>{newline}<osm version='0.6'{upload}{generator}>{newline}'''.format(
            **outputparams)
        xml += save_comp(gtfs_stop_data, osm_stop_data, feed_id, stops_layer=False)
        xml += '''{newline}</osm>'''.format(**outputparams)
        connect_to_JOSM(xml)

        print(xml)

    return render(request, 'gs/comparison.html')


def match_stops(request):
    if request.method == 'POST':
        context = {
            'match_success': 0,
            'error': ''
        }
        data_to_match_json = request.POST.get('data_to_match')
        data_to_match = json.loads(data_to_match_json)

        print(data_to_match)

        generator = 'Python Script'
        outputparams = {
            'newline': '\n',
            'indent': ' ',
            'upload': '',
            'generator': " generator='{}'".format(generator)
        }
        xml = '''<?xml version='1.0' encoding='UTF-8' ?>{newline}<osm version='0.6'{upload}{generator}>{newline}'''.format(
            **outputparams)
        for i in range(0, len(data_to_match)):
            feed_id = data_to_match[i]['feed_id']
            gtfs_stop_data = data_to_match[i]['gtfs']
            osm_stop_data = data_to_match[i]['osm']
            xml += save_comp(gtfs_stop_data, osm_stop_data, feed_id, stops_layer=True)

        xml += '''{newline}</osm>'''.format(**outputparams)
        print(xml)
        connect_to_JOSM(xml)

        '''
        stops_layer = True
        data_in_string = request.POST.get('match_data')
        data_in_json = json.loads(data_in_string)
        tags_json = request.POST.get('tags')
        tags_data = json.loads(tags_json)
        print(tags_data)

        generator = 'Python Script'
        outputparams = {
            'newline': '\n',
            'indent': ' ',
            'upload': '',
            'generator': " generator='{}'".format(generator)
        }
        '''
        # xml = '''<?xml version='1.0' encoding='UTF-8' ?>{newline}<osm version='0.6'{upload}{generator}>{newline}'''.format(
        #    **outputparams)

        '''
        for i in range(0, len(data_in_json)):
            str = data_in_json[i]['gtfs_stop'].split('-')
            gtfs_feed_id = str[0]
            gtfs_stop_id = str[1]
            osm_stop_id = data_in_json[i]['osm_stop']

            xml += save_comp(gtfs_feed_id, gtfs_stop_id, osm_stop_id, tags_data[i], stops_layer)
        '''
        # xml += '''{newline}</osm>'''.format(**outputparams)
        # connect_to_JOSM(xml)

    return render(request, 'gs/comparison.html', {'context': context})


def define_relation(request, pk):
    corr_form = Correspondence.objects.get(feed_id=pk)
    print(corr_form)

    context = {
        'feed_id': pk,
        'extra_data': '',
        'extra_data_ex': ''
    }

    extra_field_keys = []
    extra_data_ex = {}
    feed_routes = Route.objects.filter(feed=pk)
    print(feed_routes.all()[0].extra_data)
    for i in range(0, len(feed_routes)):
        extra_data = feed_routes[i].extra_data
        for key, value in extra_data.items():
            if key not in extra_field_keys:
                extra_field_keys.append(key)
                if ExtraField.objects.filter(feed_id=pk, field_name=key, value=None).exists():
                    ef = ExtraField.objects.filter(feed_id=pk, field_name=key, value=None)[0]
                else:
                    ef = ExtraField(feed_id=pk, field_name=key)
                    ef.save()
    context['extra_field_ex'] = extra_data_ex
    context['extra_field_keys'] = extra_field_keys
    route_form = Correspondence_Route_Form()
    agency_form = Correspondence_Agency_Form()
    return render(request, 'gs/define-relation.html',
                  {'context': context, 'route_form': route_form, 'agency_form': agency_form})
