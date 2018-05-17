from django.shortcuts import render
from lxml import etree
from .models import Node, Tag, Way, Relation, Value, Key, Member

def storeIntoDb(request):
    osmFile = 'osm/PTsamples.xml'
    with open(osmFile) as fileobj:
        xmlfile = fileobj.read()
    xmlfile = xmlfile.encode('utf-8')
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

    root = etree.fromstring(xmlfile, parser=parser)

    for primitive in root.getchildren():
        if primitive.tag == "node":
            node = Node(id=primitive.get("id"),
                        timestamp=primitive.get("timestamp"),
                        uid=primitive.get("uid"),
                        user=primitive.get("user"),
                        version=primitive.get("version"),
                        visible=True,
                        changeset=int(primitive.get("changeset")),
                        incomplete=False)
            node.set_coordinates(primitive.get("lon"),
                                 primitive.get("lat"))
            node.save()

            for xmlTag in primitive.getchildren():
                tag = Tag()
                tag = tag.add_tag(xmlTag.get("k"),
                                  xmlTag.get("v"))
                node.tags.add(tag)

        elif primitive.tag == "way":
            way = Way(id=primitive.get("id"),
                      timestamp=primitive.get("timestamp"),
                      uid=primitive.get("uid"),
                      user=primitive.get("user"),
                      version=primitive.get("version"),
                      visible=True,
                      changeset=int(primitive.get("changeset")),
                      incomplete=False)

            way.save()
            way.wn_set.all().delete()

            for xmlTag in primitive.getchildren():
                if xmlTag.tag == "nd":
                    node_reference = int(xmlTag.get('ref'))
                    try:
                        node = Node.objects.get(id=node_reference)
                        way.add_node(node)
                        print(node)
                    except Exception as e:
                        print("Node does not exist creating dummy node")
                        dummy_node = Node.objects.create(id=node_reference, visible=False, incomplete=True)
                        dummy_node.set_coordinates(0, 0)
                        dummy_node.save()
                        way.incomplete = 'True'
                        way.save()
                        way.add_node(node)

                elif xmlTag.tag == "tag":
                    tag = Tag()
                    tag = tag.add_tag(xmlTag.get("k"),
                                      xmlTag.get("v"))
                    way.tags.add(tag)

        elif primitive.tag == "relation":
            relation = OSM_Relation(id=primitive.get("id"),
                                    timestamp=primitive.get("timestamp"),
                                    uid=primitive.get("uid"),
                                    user=primitive.get("user"),
                                    version=primitive.get("version"),
                                    visible=True,
                                    changeset=int(primitive.get("changeset")),
                                    incomplete=False)
            relation.save()
            relation.memberrelation_set.all().delete()

            for xmlTag in primitive.getchildren():

                if xmlTag.tag == 'tag':
                    tag = Tag()
                    tag = tag.add_tag(xmlTag.get("k"),
                                      xmlTag.get("v"))
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
                            rel_child_relation = OSM_Relation.get(id=ref)
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

    return render(request, 'osm/load.html')
