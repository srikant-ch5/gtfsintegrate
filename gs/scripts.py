from django.shortcuts import render
from lxml import etree
from .models import Node,Tag,Way,Relation,Value,Key,Member
from decimal import Decimal

def storeIntoDb(request):

  osmFile = 'osm/PTsamples.xml'
  with open(osmFile) as fileobj:
    xmlfile = fileobj.read()
  xmlfile = xmlfile.encode('utf-8')
  parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

  root = etree.fromstring(xmlfile,parser=parser)
  tag_counter = 678555
  key_counter = 4569875
  value_counter =856474

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

t      for xmlTag in primitive.getchildren():
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
            print(node)
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
              rel_child_relation = OSM_Relation.get(id=ref)
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

  return render(request,'osm/load.html')
