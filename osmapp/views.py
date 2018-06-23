import os
import overpy
import xml.etree.cElementTree as cetree
import pdb
from requests import post

from django.contrib.gis.geos import Point, LineString
from django.contrib.gis.geos import LineString
from django.shortcuts import render
from ordered_set import OrderedSet
from typing import List, Any
from django.db import connection

from multigtfs.models import Feed, Stop
from .models import Tag, KeyValueString, Node, Way, OSM_Relation, FeedBounds
from gs.tasks import dividemap, getmidpoint
import json


def get_bounds(request):
    if request.method == 'POST':
        context = {
            'feed_id': -1
        }
        feed_id = request.POST.get('feed_id')
        feed_name = Feed.objects.get(id=feed_id).name

        query = 'SELECT gtfs_stop.geom FROM gtfs_stop where gtfs_stop.feed_id=8'
        query2 = 'SELECT ST_AsGeoJson(ST_Envelope(ST_Union(ST_Envelope(geom)))) AS table_extent FROM gtfs_stop where gtfs_stop.feed_id=8'
        cursor = connection.cursor()
        cursor.execute(query2)
        result = cursor.fetchall()
        bounds_json = json.loads(result[0][0])
        southwest = bounds_json['coordinates'][0][0]
        northwest = bounds_json['coordinates'][0][1]
        northeast = bounds_json['coordinates'][0][2]
        southeast = bounds_json['coordinates'][0][3]

        west = [0.0, 0.0]
        west[0], west[1] = getmidpoint(northwest[1], northwest[0], southwest[1], southwest[0])
        east = [0.0, 0.0]
        east[0], east[1] = getmidpoint(northeast[1], northeast[0], southeast[1], southeast[0])
        north = [0.0, 0.0]
        north[0], north[1] = getmidpoint(northeast[1], northeast[0], northwest[1], northwest[0])
        south = [0.0, 0.0]
        south[0], south[1] = getmidpoint(southwest[1], southwest[0], southeast[1], southeast[0])

        center = [0.0, 0.0]
        center[0], center[1] = getmidpoint(north[0], north[1], south[0], south[1])

        top_left = getmidpoint(northwest[1], northwest[0], center[0], center[1])
        top_right = getmidpoint(northeast[1], northeast[0], center[0], center[1])
        bottom_left = getmidpoint(southwest[1], southwest[0], center[0], center[1])
        bottom_right = getmidpoint(southeast[1], southeast[0], center[0], center[1])

        top_left = Point(top_left[0],top_left[1])
        top_right = Point(top_right[0],top_right[1])
        bottom_left = Point(bottom_right[0],bottom_right[1])
        bottom_left = Point(bottom_left[0],bottom_left[1])


        outerbound = [southwest, northwest, northeast, southeast]
        outerbound = LineString(outerbound)

        innerbound = [bottom_left, top_left, top_right, bottom_right]
        feedbound = FeedBounds(operator_name=feed_name, outer_bound=outerbound, inner_bound=innerbound)
        feedbound.save()

        print('saved inner bound {} {} {} {} with operator {}'.format(top_left, top_right, bottom_left, bottom_right,
                                                                      feed_name))
        pdb.set_trace()

    return render(request, 'gs/load.html', {'context': context})


def set_bounds(request):
    context = {
        'loaded': ''
    }

    if request.method == 'POST':
        east = request.POST.get('east')
        west = request.POST.get('west')
        north = request.POST.get('north')
        south = request.POST.get('south')
        northeast_lat = request.POST.get('northeast_lat')
        northeast_lon = request.POST.get('northeast_lon')
        northwest_lon = request.POST.get('northwest_lon')
        northwest_lat = request.POST.get('northwest_lat')
        southeast_lon = request.POST.get('southeast_lon')
        southeast_lat = request.POST.get('southeast_lat')
        southwest_lat = request.POST.get('southwest_lat')
        southwest_lon = request.POST.get('southwest_lon')
        coordinates_arr = request.POST.get('stopscoordinates_array')

        data = json.loads(coordinates_arr)

        print('{} {} {} {} {} {} {} {} {} {} {} {}'.format(south, west, north, east, northeast_lat, northeast_lon,
                                                           northwest_lat, northwest_lon, southeast_lat, southeast_lon,
                                                           southwest_lat, southwest_lon
                                                           ))

        bbox = south + "," + west + "," + north + "," + east

        get_stops_query = '''
        [out:xml];
            (
            node(''' + bbox + ''')[highway=bus_stop];
            node(''' + bbox + ''')[bus=yes];
            node(''' + bbox + ''')[public_transport=stop_position];
            node(''' + bbox + ''')[public_transport=platform];
        );
        out meta;
        '''
        print(get_stops_query)
        try:
            result = post("http://overpass-api.de/api/interpreter", get_stops_query)
        except ConnectionError as ce:
            context['connection_error'] = "There is a connection error while downloading the OSM data"

        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
        xmlfiledir = xmlfiledir = os.path.join(os.path.dirname(PROJECT_ROOT), 'osmapp', 'static')
        xmlfile = xmlfiledir + '/node.osm'
        with open(xmlfile, 'wb') as fh:
            fh.write(result.content)

        print("Content has been copied")
        dividemap(east, west, north, south, northeast_lat, northeast_lon, northwest_lat, northwest_lon, southeast_lat,
                  southeast_lon, southwest_lat, southwest_lon, data)
        # load(xmlfile)

    return render(request, 'gs/load.html', {'context': context})


def get_osm_data(request):
    context = {
        'loaded': 'Data has been loaded'
    }

    api = overpy.Overpass()

    result = api.query("node(50.745,7.17,50.75,7.18);out;")

    return render(request, 'gs/load.html', {'context': context})


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
    1. nodes may have tag with both bus=yes/tram=yes and highway=bus_stop/railway=tram_stop
    2. nodes may have tag only with bus=yes/tram=yes
    3. nodes may have tag only waith highway=bus_stop/railway=tram_stop
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

    OrderedSet(bus_nodes)
    print(OrderedSet(tram_nodes))

    return render(request, 'gs/load.html')


def get_route_master_relations(request):
    route_master_key = KeyValueString.objects.get(value='type')
    route_master_value = KeyValueString.objects.get(value='route_master')
    route_master_tag = Tag.objects.get(key=route_master_key, value=route_master_value)
    route_master_relations = route_master_tag.osm_relation_set.all()

    bus_route_master = []
    rail_route_master = []

    for route_master_relation in route_master_relations:
        type_key = KeyValueString.objects.get(value='route_master')
        tags = route_master_relation.tags.get(key=type_key)

        if tags.value.value == 'bus':
            print(tags.value)
            bus_route_master.append(route_master_relation)
        elif tags.value.value == 'light_rail':
            rail_route_master.append(route_master_relation)

    print(OrderedSet(bus_route_master))
    print(OrderedSet(rail_route_master))

    return render(request, 'gs/load.html')


def get_route_relations(request):
    route_key = KeyValueString.objects.get(value='type')
    route_value = KeyValueString.objects.get(value='route')
    route_tag = Tag.objects.get(key=route_key, value=route_value)
    route_relations = route_tag.osm_relation_set.all()

    bus_route = []
    rail_route = []

    for route_relation in route_relations:
        type_key = KeyValueString.objects.get(value='route')
        tags = route_relation.tags.get(key=type_key)

        if tags.value.value == 'bus':
            print(tags.value)
            bus_route.append(route_relation)
        elif tags.value.value == 'light_rail':
            rail_route.append(route_relation)

    print(OrderedSet(bus_route))
    print(OrderedSet(rail_route))

    return render(request, 'gs/load.html')


def load(xmlfile):
    Node.objects.all().delete()
    Way.objects.all().delete()
    print("Downloading the nodes")
    data = open(xmlfile)

    tree = cetree.parse(data)
    root = tree.getroot()

    for primitive in root:
        if primitive.tag == 'node':
            try:
                snode_id = int(primitive.attrib.get("id"))
                stimestamp = primitive.attrib.get("timestamp")
                suid = int(primitive.attrib.get("uid"))
                suser = primitive.attrib.get("user")
                sversion = int(primitive.attrib.get("version"))
                schangeset = int(primitive.attrib.get("changeset"))
                slat = float(primitive.attrib.get("lat"))
                slon = float(primitive.attrib.get("lon"))

                node = Node(id=snode_id, timestamp=stimestamp, uid=suid, user=suser, version=sversion, visible=True,
                            changeset=schangeset, incomplete=False)
                node.set_cordinates(slon, slat)
                node.save()
            except Exception as e:
                print(e)

            for xmlTag in primitive:
                getkey_fromxml = xmlTag.get("k")
                getvalue_fromxml = xmlTag.get("v")

                tag = Tag()
                tag = tag.add_tag(getkey_fromxml, getvalue_fromxml)
                node.save()
                node.tags.add(tag)

        elif primitive.tag == 'way':
            try:
                wway_id = int(primitive.attrib.get("id"))
                wtimestamp = primitive.attrib.get("timestamp")
                wuid = int(primitive.attrib.get("uid"))
                wuser = primitive.attrib.get("user")
                wversion = int(primitive.attrib.get("version"))
                wchangeset = int(primitive.attrib.get("changeset"))

                way = Way(id=wway_id, timestamp=wtimestamp, visible=True, incomplete=False, uid=wuid, user=wuser,
                          version=wversion, changeset=wchangeset)
                way.save()
                way.wn_set.all().delete()

            except Exception as e:
                print(e)

            for xmlTag in primitive:
                if xmlTag.tag == "nd":
                    node_reference = int(xmlTag.get('ref'))
                    try:
                        node = Node.objects.get(id=node_reference)
                        way.add_node(node)
                    except Exception as e:
                        print("Node does not exist creating dummy node")
                        dummy_node = Node.objects.create(id=node_reference, visible=False, incomplete=True)
                        dummy_node.set_cordinates(0, 0)
                        dummy_node.save()
                        way.incomplete = 'True'
                        way.save()
                        way.add_node(node)

                elif xmlTag.tag == "tag":
                    getkey_fromxml = xmlTag.get("k")
                    getvalue_fromxml = xmlTag.get("v")

                    tag = Tag()
                    tag = tag.add_tag(getkey_fromxml, getvalue_fromxml)
                    way.tags.add(tag)

            way_nodes = way.nodes.all()
            nodes = []  # type: List[List[Any]]

            for way_node in way_nodes:
                single_node_geom = list(way_node.geom)
                nodes.append(single_node_geom)

            print(nodes)
            way.geom = LineString(nodes)
            way.save()

        elif primitive.tag == "relation":
            rid = int(primitive.get("id"))
            rtimestamp = primitive.get("timestamp")
            ruid = int(primitive.get("uid"))
            ruser = primitive.get("user")
            rversion = int(primitive.get("version"))
            rchangeset = int(primitive.get("changeset"))

            relation = OSM_Relation(id=rid, timestamp=rtimestamp, uid=ruid, user=ruser, version=rversion,
                                    changeset=rchangeset, visible=True, incomplete=False)
            relation.save()
            relation.memberrelation_set.all().delete()

            for xmlTag in primitive:

                if xmlTag.tag == 'tag':
                    getkey_fromxml = xmlTag.get("k")
                    getvalue_fromxml = xmlTag.get("v")

                    tag = Tag()
                    tag = tag.add_tag(getkey_fromxml, getvalue_fromxml)
                    relation.tags.add(tag)

                elif xmlTag.tag == 'member':
                    type = xmlTag.get("type")
                    ref = xmlTag.get("ref")
                    role = xmlTag.get("role")

                    try:
                        if type == 'node':
                            rel_node = Node.objects.get(id=ref)
                            rm = relation.add_member(rel_node, type, role)
                        elif type == 'way':
                            rel_way = Way.objects.get(id=ref)
                            rm = relation.add_member(rel_way, type, role)
                        elif type == 'relation':
                            rel_child_relation = OSM_Relation.objects.get(id=ref)
                            rm = relation.add_member(rel_child_relation, type, role)

                    except Exception as e:
                        if type == 'node':
                            dummy_rel_node = Node.objects.create(id=ref, visible=False, incomplete=True)
                            dummy_rel_node.set_cordinates(0, 0)
                            dummy_rel_node.save()

                            rm = relation.add_member(dummy_rel_node, type, role)

                        elif type == 'way':
                            dummy_rel_way = Way.objects.create(id=ref, visible=False, incomplete=True)
                            dummy_rel_way.save()

                            rm = relation.add_member(dummy_rel_way, type, role)

                        elif type == 'relation':
                            dummy_rel_relation = OSM_Relation.objects.create(id=ref, visible=False, incomplete=True)
                            dummy_rel_relation.save()

                            rm = relation.add_member(dummy_rel_relation, type, role)

    print("The data has been downloaded")
