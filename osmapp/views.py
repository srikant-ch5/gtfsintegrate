from django.shortcuts import render
from .models import Tag, KeyValueString, Node, Way,OSM_Relation, MemberRelation
from lxml import etree
from decimal import Decimal
from django.contrib.gis.geos import Point
from ordered_set import OrderedSet
from django.contrib.gis.geos import Point,LineString

def home(request):

    #whenever load map the ways should have the nodes 
    ways = Way.objects.all()

    for way in ways:
        way_nodes = way.nodes.all()
        nodes = []
        for way_node in way_nodes:
            single_node_geom = list(way_node.geom)
            nodes.append(single_node_geom)
        
        print(nodes)
        way.geom = LineString(nodes)
        way.save()

    return render(request, 'gs/load.html')

def get_stops(request):
    #filter stops from Node table
    #highway 
    #public_transport = stop_position
    stop_key  = KeyValueString.objects.get(value="public_transport")
    stop_value = KeyValueString.objects.get(value="stop_position")
    stop_tag   = Tag.objects.get(key=stop_key, value=stop_value)
    stop_nodes = stop_tag.node_set.all()

    ''' 
    While filtering with public_transport=stop_position there are 3 cases
    1. nodes may have tag with both bus=yes/tram=yes and highway=bus_stop/railway=tram_stop
    2. nodes may have tag only with bus=yes/tram=yes
    3. nodes may have tag only waith highway=bus_stop/railway=tram_stop
    '''
    bus_nodes  = []
    tram_nodes = []

    for stop_node in stop_nodes:
        tags = stop_node.tags.all()
        bus_stop_key_text = ['highway','bus']
        bus_stop_value_text = ['bus_stop','yes']
        is_bus_stop = 0

        for (sbus_stop_key_text, sbus_stop_value_text) in zip(bus_stop_key_text, bus_stop_value_text):
            bus_stop_key   = KeyValueString.objects.filter(value=sbus_stop_key_text)
            bus_stop_value = KeyValueString.objects.filter(value=sbus_stop_value_text)
            if bus_stop_key.count() > 0 and bus_stop_value.count() > 0:
                is_bus_stop = tags.filter(key=bus_stop_key[0], value=bus_stop_value[0]).count()

        if is_bus_stop > 0:
            bus_nodes.append(stop_node)
        
        tram_stop_key_text   = ['railway','tram']
        tram_stop_value_text = ['tram_stop', 'yes']
        is_tram_stop         = 0

        for(stram_stop_key_text, stram_stop_value_text) in zip(tram_stop_key_text,tram_stop_value_text):
            tram_stop_key   = KeyValueString.objects.filter(value=stram_stop_key_text)
            tram_stop_value = KeyValueString.objects.filter(value=stram_stop_value_text)
            if tram_stop_key.count() > 0 and tram_stop_value.count() > 0:
                is_tram_stop = tags.filter(key=tram_stop_key[0], value=tram_stop_value[0]).count()

        if is_tram_stop > 0:
            tram_nodes.append(stop_node)

    print(OrderedSet(bus_nodes))
    print(OrderedSet(tram_nodes))

    return render(request,'gs/load.html')

def get_route_master_relations(request):

    route_master_key   = KeyValueString.objects.get(value='type')
    route_master_value = KeyValueString.objects.get(value='route_master')
    route_master_tag    = Tag.objects.get(key=route_master_key, value=route_master_value)
    route_master_relations = route_master_tag.osm_relation_set.all()

    bus_route_master  = []
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

    route_key   = KeyValueString.objects.get(value='type')
    route_value = KeyValueString.objects.get(value='route')
    route_tag    = Tag.objects.get(key=route_key, value=route_value)
    route_relations = route_tag.osm_relation_set.all()

    bus_route  = []
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

def load(request):

    osmFile = '''
    <osm version='0.6' generator='JOSM'>
      <node id='313586' timestamp='2018-01-15T17:26:05Z' uid='72151' user='GeorgFausB' version='13' changeset='55469382' lat='50.9558026' lon='6.9691347'>
        <tag k='TMC:cid_58:tabcd_1:Class' v='Point' />
        <tag k='TMC:cid_58:tabcd_1:Direction' v='positive' />
        <tag k='TMC:cid_58:tabcd_1:LCLversion' v='9.00' />
        <tag k='TMC:cid_58:tabcd_1:LocationCode' v='39623' />
        <tag k='TMC:cid_58:tabcd_1:NextLocationCode' v='39624' />
        <tag k='TMC:cid_58:tabcd_1:PrevLocationCode' v='39622' />
        <tag k='test-tag' v='testvalue' />
      </node>
      <node id='23423432' timestamp='2017-01-15T17:26:05Z' uid='51' user='FausB' version='1' changeset='469382' lat='50.9558026' lon='6.9691347'>
      <tag k='test-tag' v='testvalue' />
      </node>
      <way id='25250108' timestamp='2016-03-28T13:24:52Z' uid='109062' user='Jojo4u' version='28' changeset='38120453'>
        <nd ref='313586' />
        <nd ref='23423432' />
        <tag k='electrified' v='contact_line' />
        <tag k='frequency' v='0' />
        <tag k='gauge' v='1000;1435' />
        <tag k='maxspeed' v='30' />
        <tag k='network' v='VVS' />
        <tag k='operator' v='Stuttgarter Straßenbahnen AG' />
        <tag k='railway' v='light_rail' />
        <tag k='railway:pzb' v='no' />
        <tag k='voltage' v='750' />
        <tag k='workrules' v='DE:BOStrab' />
      </way>

     </osm>
    '''
    root = etree.fromstring(osmFile)

    for primitive in root.getchildren():
        if primitive.tag == "node":
            #create tag
            snode_id   = int(primitive.get("id"))
            stimestamp = primitive.get("timestamp")
            suid       = int(primitive.get("uid"))
            suser      = primitive.get("user")
            sversion   = int(primitive.get("version"))
            schangeset = int(primitive.get("changeset"))
            slat       = float(primitive.get("lat"))
            slon       = float(primitive.get("lon"))

            node = Node(id=snode_id, timestamp=stimestamp,uid=suid,user=suser,version=sversion,visible=True,changeset=schangeset,incomplete=False)
            node.set_cordinates(slat,slon)
            node.save()

            for xmlTag in primitive.getchildren():
                getkey_fromxml = xmlTag.get("k")
                getvalue_fromxml = xmlTag.get("v")

                tag = Tag()
                tag = tag.add_tag(getkey_fromxml,getvalue_fromxml)
                node.tags.add(tag)

        elif primitive.tag == "way":
            wway_id    = int(primitive.get("id"))
            wtimestamp = primitive.get("timestamp")
            wuid       = int(primitive.get("uid"))
            wuser      = primitive.get("user")
            wversion   = int(primitive.get("version"))
            wchangeset = int(primitive.get("changeset"))

            way = Way(id=wway_id,timestamp=wtimestamp,visible=True,incomplete=False,uid=wuid,user=wuser,version=wversion,changeset=wchangeset)
            way.save()
            way.wn_set.all().delete()

            for xmlTag in primitive.getchildren():
                if xmlTag.tag == "nd":
                    node_reference = int(xmlTag.get('ref'))
                    try:
                        node = Node.objects.get(id=node_reference)
                        way.add_node(node)
                    except Exception as e:
                        print("Node does not exist creating dummy node")
                        dummy_node = Node.objects.create(id=node_reference, visible=False, incomplete=True)
                        dummy_node.set_cordinates(0,0)
                        dummy_node.save()
                        way.incomplete = 'True'
                        way.save()
                        way.add_node(node)

                elif xmlTag.tag == "tag":
                    getkey_fromxml= xmlTag.get("k")
                    getvalue_fromxml =xmlTag.get("v")

                    tag = Tag()
                    tag = tag.add_tag(getkey_fromxml,getvalue_fromxml)
                    way.tags.add(tag)
        elif primitive.tag == "relation":
            rid        = int(primitive.get("id"))
            rtimestamp = primitive.get("timestamp")
            ruid       = int(primitive.get("uid"))
            ruser      = primitive.get("user")
            rversion   = int(primitive.get("version"))
            rchangeset = int(primitive.get("changeset"))

            relation = OSM_Relation(id=rid, timestamp=rtimestamp, uid=ruid, user=ruser, version=rversion, changeset=rchangeset,visible=True,incomplete=False)
            relation.save()
            relation.memberrelation_set.all().delete()

            for xmlTag in primitive.getchildren():

                if xmlTag.tag == 'tag':
                    getkey_fromxml= xmlTag.get("k")
                    getvalue_fromxml =xmlTag.get("v")

                    tag = Tag()
                    tag = tag.add_tag(getkey_fromxml, getvalue_fromxml)
                    relation.tags.add(tag)

                elif xmlTag.tag == 'member':
                    type = xmlTag.get("type")
                    ref  = xmlTag.get("ref")
                    role = xmlTag.get("role")

                    try:
                        if type == 'node':
                            rel_node = Node.objects.get(id=ref)
                            rm = relation.add_member(rel_node,type ,role)
                        elif type == 'way':
                            rel_way = Way.objects.get(id=ref)
                            rm = relation.add_member(rel_way,type, role)
                        elif type == 'relation':
                            rel_child_relation = OSM_Relation.objects.get(id=ref)
                            rm = relation.add_member(rel_child_relation,type, role)

                    except Exception as e:
                        if type == 'node':
                            dummy_rel_node = Node.objects.create(id=ref, visible=False, incomplete=True)
                            dummy_rel_node.set_cordinates(0,0)
                            dummy_rel_node.save()

                            rm = relation.add_member(dummy_rel_node, type, role)
                        
                        elif type == 'way':
                            dummy_rel_way = Way.objects.create(id=ref, visible=False, incomplete=True)
                            dummy_rel_way.save()

                            rm = relation.add_member(dummy_rel_way, type ,role)

                        elif type == 'relation':
                            dummy_rel_relation = OSM_Relation.objects.create(id= ref, visible=False, incomplete=True)
                            dummy_rel_relation.save()

                            rm = relation.add_member(dummy_rel_relation, type, role)


    return render(request,'gs/load.html')
