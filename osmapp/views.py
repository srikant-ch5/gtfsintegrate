import json
import os
import xml.etree.cElementTree as cetree
from typing import List, Any

from django.contrib.gis.geos import LineString
from django.db import connection
from django.shortcuts import render
from ordered_set import OrderedSet
from requests import post

from gs.tasks import getmidpoint, reduce_bounds
from multigtfs.models import Feed
from .models import Tag, KeyValueString, Node, Way, OSM_Relation

def xmlsafe(name):
    return str(name).replace('&', '&amp;').replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;").replace('"',
                                                                                                                    "&quot;")

def get_osm_data(feed_id):
    print("Osm data in view")
    feed_name = Feed.objects.get(id=feed_id).name

    get_bound_query = 'SELECT ST_AsGeoJson(ST_Envelope(ST_Union(ST_Envelope(geom)))) AS table_extent FROM gtfs_stop where gtfs_stop.feed_id=' + str(
        feed_id)
    cursor = connection.cursor()
    cursor.execute(get_bound_query)
    result = cursor.fetchall()
    bounds_json = json.loads(result[0][0])

    # bounds required by overpass query is two points left min and right max
    southwest = bounds_json['coordinates'][0][0]
    northwest = bounds_json['coordinates'][0][1]
    northeast = bounds_json['coordinates'][0][2]
    southeast = bounds_json['coordinates'][0][3]

    # reduce_bounds(southeast,southwest,northeast,northwest)

    bbox = str(southwest[1]) + "," + str(southwest[0]) + "," + str(northeast[1]) + "," + str(northeast[0])

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

    if not Node.objects.filter(feed=feed_id).exists():
        print("Downloading osm data from overpass to Db")
        load(xmlfile, feed_id, 'cmp_nodes')
    else:
        print("Nodes are already downloaded")


def load_osm_data_view(request):
    if request.method == 'POST':
        context = {
            'feed_id': -1
        }
        feed_id = request.POST.get('feed_id')

        get_osm_data(feed_id)

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


def load(xmlfile, feed_id, purpose):
    relation_ids = []
    relations_info = []
    all_nodes_info = []
    all_nodes_ids = []
    way_ids = []

    print("Downloading the nodes")
    data = open(xmlfile)

    tree = cetree.parse(data)
    root = tree.getroot()
    print(feed_id)
    feed = Feed.objects.get(id=feed_id)

    for primitive in root:
        if primitive.tag == 'node':
            try:
                single_node = []
                snode_id = int(primitive.attrib.get("id"))
                stimestamp = primitive.attrib.get("timestamp")
                suid = int(primitive.attrib.get("uid"))
                suser = primitive.attrib.get("user")
                sversion = int(primitive.attrib.get("version"))
                schangeset = int(primitive.attrib.get("changeset"))
                slat = float(primitive.attrib.get("lat"))
                slon = float(primitive.attrib.get("lon"))

                node = Node(feed=feed, id=snode_id, timestamp=stimestamp, uid=suid, user=suser, version=sversion,visible=True,changeset=schangeset, incomplete=False, purpose=purpose)
                node.set_cordinates(slon, slat)
                node.save()
                all_nodes_ids.append(snode_id)
                single_node.append(str(snode_id))
            except Exception as e:
                print(e)

            for xmlTag in primitive:
                getkey_fromxml = xmlTag.get("k")
                getvalue_fromxml = xmlTag.get("v")

                if getkey_fromxml == 'name':
                    single_node.append(getkey_fromxml)
                    single_node.append(getvalue_fromxml)
                    getvalue_fromxml = xmlsafe(getvalue_fromxml)
                elif getkey_fromxml == 'ref':
                    single_node.append(getkey_fromxml)
                    single_node.append(getvalue_fromxml)
                if len(single_node) > 1:
                    all_nodes_info.append(single_node)

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

                way = Way(feed=feed, id=wway_id, timestamp=wtimestamp, visible=True, incomplete=False, uid=wuid,
                          user=wuser,
                          version=wversion, changeset=wchangeset, purpose=purpose)
                way.save()
                way.wn_set.all().delete()
                way_ids.append(wway_id)

            except Exception as e:
                print(e)

            for xmlTag in primitive:
                if xmlTag.tag == "nd":
                    node_reference = int(xmlTag.get('ref'))
                    if Node.objects.filter(id=node_reference).exists():
                        node = Node.objects.get(id=node_reference)
                        way.add_node(node)
                    else:
                        print("Node does not exist creating dummy node")
                        dummy_node = Node.objects.create(feed=feed, id=node_reference, visible=False, incomplete=True,
                                                         purpose=purpose)
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
            relation_ar = []
            rid = int(primitive.get("id"))
            rtimestamp = primitive.get("timestamp")
            ruid = int(primitive.get("uid"))
            ruser = primitive.get("user")
            rversion = int(primitive.get("version"))
            rchangeset = int(primitive.get("changeset"))

            relation = OSM_Relation(feed=feed, id=rid, timestamp=rtimestamp, uid=ruid, user=ruser, version=rversion,
                                    changeset=rchangeset, visible=True, incomplete=False, purpose=purpose)

            relation.save()
            relation.memberrelation_set.all().delete()
            relation_ids.append(rid)
            relation_ar.append(str(rid))

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

                            node_tags = rel_node.tags.all()
                            ar = []
                            print("{} node tags counts is {}".format(rel_node.id,node_tags.count()))
                            for it in range(0, node_tags.count()):
                                if node_tags[it].key.value == 'name' or node_tags[it].key.value == 'ref':
                                    ar.append(str(rid))
                                    ar.append(node_tags[it].key.value)
                                    ar.append(node_tags[it].value.value)
                            if len(ar) > 1:
                                relations_info.append(ar)
                        elif type == 'way':
                            rel_way = Way.objects.get(id=ref)
                            rm = relation.add_member(rel_way, type, role)
                        elif type == 'relation':
                            rel_child_relation = OSM_Relation.objects.get(id=ref)
                            rm = relation.add_member(rel_child_relation, type, role)

                    except Exception as e:
                        print("************** {} *****************".format(e))
                        if type == 'node':
                            dummy_rel_node = Node.objects.create(id=ref, visible=False, incomplete=True,
                                                                 purpose=purpose)
                            dummy_rel_node.set_cordinates(0, 0)
                            dummy_rel_node.save()

                            rm = relation.add_member(dummy_rel_node, type, role)

                        elif type == 'way':
                            dummy_rel_way = Way.objects.create(id=ref, visible=False, incomplete=True, purpose=purpose)
                            dummy_rel_way.save()

                            rm = relation.add_member(dummy_rel_way, type, role)

                        elif type == 'relation':
                            dummy_rel_relation = OSM_Relation.objects.create(id=ref, visible=False, incomplete=True,
                                                                             purpose=purpose)
                            dummy_rel_relation.save()

                            rm = relation.add_member(dummy_rel_relation, type, role)

    print("The data has been downloaded")

    return all_nodes_ids, relation_ids, relations_info, way_ids
