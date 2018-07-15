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


def define_relation(request, pk=None):
    if request.method == "POST":
        route_form = Correspondence_Route_Form(request.POST)

        if route_form.is_valid():
            entered_route_corr_form = route_form.save(commit=False)
            entered_route_corr_form_feed_id = entered_route_corr_form.feed_id

            if Correspondence_Route.objects.filter(feed_id=entered_route_corr_form_feed_id).exists():
                print("Saving Route form")
            else:
                entered_route_corr_form.save()
    else:
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
        return render(request, 'gs/define-relation.html',
                      {'context': context, 'route_form': route_form})


def save_route_corr(request):
    if request.method == "POST":
        route_form = Correspondence_Route_Form(request.POST)
        entered_route_corr_form_feed_id = -1
        if route_form.is_valid():
            entered_route_corr_form = route_form.save(commit=False)
            entered_route_corr_form_feed_id = entered_route_corr_form.feed_id
            context = {
                'feed_id': entered_route_corr_form_feed_id
            }
            if Correspondence_Route.objects.filter(feed_id=entered_route_corr_form_feed_id).exists():
                route_corr_obj = Correspondence_Route.objects.get(feed_id=entered_route_corr_form_feed_id)
                route_corr_obj.route_id = entered_route_corr_form.route_id
                route_corr_obj.agency = entered_route_corr_form.agency
                route_corr_obj.short_name = entered_route_corr_form.short_name
                route_corr_obj.long_name = entered_route_corr_form.long_name
                route_corr_obj.desc = entered_route_corr_form.desc
                route_corr_obj.rtype = entered_route_corr_form.rtype
                route_corr_obj.url = entered_route_corr_form.url
                route_corr_obj.color = entered_route_corr_form.color
                route_corr_obj.text_color = entered_route_corr_form.text_color

                route_corr_obj.save()
            else:
                entered_route_corr_form.save()

        else:
            print("Route form not valid {}".format(route_form))

        agency_form = Correspondence_Agency_Form()
        return render(request, 'gs/define-relation.html', {'context': context, 'agency_form': agency_form})


def save_ag_corr(request):
    if request.method == "POST":
        agency_form = Correspondence_Agency_Form(request.POST)

        if agency_form.is_valid():
            entered_agency_corr_form = agency_form.save(commit=False)
            entered_agency_corr_form_feed_id = entered_agency_corr_form.feed_id

            if Correspondence_Agency.objects.filter(feed_id=entered_agency_corr_form_feed_id).exists():
                ag_corr_obj = Correspondence_Agency.objects.get(feed_id=entered_agency_corr_form_feed_id)
                ag_corr_obj.feed_id = entered_agency_corr_form_feed_id
                ag_corr_obj.agency_name = entered_agency_corr_form.agency_name
                ag_corr_obj.agency_id = entered_agency_corr_form.agency_id
                ag_corr_obj.agency_url = entered_agency_corr_form.agency_url
                ag_corr_obj.agency_timezone = entered_agency_corr_form.agency_timezone
                ag_corr_obj.agency_lang = entered_agency_corr_form.agency_lang
                ag_corr_obj.agency_phone = entered_agency_corr_form.agency_phone
                ag_corr_obj.agency_fare_url = entered_agency_corr_form.agency_fare_url

                ag_corr_obj.save()
            else:
                entered_agency_corr_form.save()

            '''Creating XML File'''
            # get the routes form with that feed
            routes_list = Route.objects.filter(feed=entered_agency_corr_form_feed_id)
            routes_form = Correspondence_Route.objects.get(feed_id=entered_agency_corr_form_feed_id)

            valid_routes_attr_list = {}

            for key, value in routes_form.__dict__.items():
                if key == '_state':
                    continue
                elif key == 'feed_id':
                    continue
                elif key == 'id':
                    continue
                else:
                    if value != '':
                        pair = {key: value}
                        valid_routes_attr_list.update(pair)

            print(valid_routes_attr_list)
            xml = ''
            for route in routes_list:
                xml += "\n<tag k='type' v='route_master'>\n"
                for r_key, r_value in route.__dict__.items():
                    if r_key in valid_routes_attr_list:
                        tag_key = valid_routes_attr_list[r_key]
                        tag_val = r_value

                        if tag_val != '':
                            xml += "<tag k='"+str(tag_key)+"' v='"+str(tag_val)+"' />\n"

            print(xml)

        return render(request, 'gs/saved_relation.html', {'agency_form': agency_form})
