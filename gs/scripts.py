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
          snode_id   = int(primitive.get("id"))
          stimestamp = primitive.get("timestamp")
          suid       = int(primitive.get("uid"))
          suser      = primitive.get("user")
          sversion   = int(primitive.get("version"))
          schangeset = int(primitive.get("changeset"))
          slat       = Decimal(primitive.get("lat"))
          slon       = Decimal(primitive.get("lon"))

          #print(" Node %d %s %d %s %d %d %f %f" % (snode_id,stimestamp,suid,suser,sversion,schangeset,slat,slon))
          
          node = Node(node_id=snode_id, timestamp=stimestamp,uid=suid,user=suser,version=sversion,changeset=schangeset,lat=slat,lon=slon)
          node.save()

          for xmlTag in primitive.getchildren():
            #Step 1 get key and value text from the xml tag element
            get_key_text_from_xml = xmlTag.get("k")
            get_value_text_from_xml = xmlTag.get("v")

            #step 2 is to check if the tag with same key and value exists
            t = Tag.objects.all()
            flag= 0
            key_to_search = get_key_text_from_xml
            value_to_search = get_value_text_from_xml
            tag_to_use = Tag()
            tag_index = 0

            for onetag in t:
              if onetag.key_ref.all()[0].key_text == key_to_search and onetag.value_ref.all()[0].value_text == value_to_search:
                flag = 1
                tag_index = onetag.tag_id
                break

            if flag == 1:
                tag_to_use = Tag.objects.get(tag_id=tag_index)
                node.tag_ref.add(tag_to_use)
                node.save()

            else:
                #create a key value with text and id counter and also create a Tag using them
                print("creating new tag")
                key_count = Key.objects.filter(key_text=key_to_search).count()

                if key_count == 0:
                  key = Key(key_id=key_counter,key_text=key_to_search)
                  key.save()
                  key_counter += 1
                elif key_count >1:
                  countDec = key_count
                  while countDec > 1:
                    Key.objects.filter(key_text=key_to_search)[0].delete()
                    print("Deleted one similar key")
                    countDec -= 1

                value_count = Value.objects.filter(value_text=value_to_search).count()

                if value_count == 0:
                  value = Value(value_id=value_counter, value_text=value_to_search)
                  value.save()
                  value_counter += 1
                elif value_count > 1:
                  countVDec = value_count
                  while countVDec > 1:
                    Value.objects.filter(value_text=value_to_search)[0].delete()
                    countVDec -= 1

                unique_key = Key.objects.get(key_text=key_to_search)
                unique_value =Value.objects.get(value_text=value_to_search)

                tag_to_create = Tag(tag_id = 78934556)
                tag_to_create.save()
                tag_to_create.key_ref.add(unique_key)
                tag_to_create.value_ref.add(unique_value)
                tag_to_create.save()
                tag_to_use = Tag.objects.filter(tag_id=78934556)
                print(tag_to_use)
                tag_counter += 1
                
                node = Node.objects.get(node_id=snode_id)
                node.tag_ref.add(tag_to_use)
                node.save()

      elif primitive.tag == 'way':

        wway_id    = int(primitive.get("id"))
        wtimestamp = primitive.get("timestamp")
        wuid       = int(primitive.get("uid"))
        wuser      = primitive.get("user")
        wversion   = int(primitive.get("version"))
        wchangeset = int(primitive.get("changeset"))

        way = Way(way_id=wway_id,timestamp=wtimestamp,uid=wuid,user=wuser,version=wversion,changeset=wchangeset)
        way.save()

        for xmlTag in primitive.getchildren():

          if xmlTag.tag == 'nd':
            node_reference = int(xmlTag.get("ref"))
            node_to_add = Node.objects.get(node_id=node_reference)
            way.node_ref.add(node_to_add)
            way.save()

          elif xmlTag.tag == 'tag':

            get_key_text_from_xml = xmlTag.get("k")
            get_value_text_from_xml = xmlTag.get("v")

            #step 2 is to check if the tag with same key and value exists
            t = Tag.objects.all()
            flag= 0
            key_to_search = get_key_text_from_xml
            value_to_search = get_value_text_from_xml
            tag_to_use = Tag()
            tag_index = 0

            for onetag in t:
              if onetag.key_ref.all()[0].key_text == key_to_search and onetag.value_ref.all()[0].value_text == value_to_search:
                flag = 1
                tag_index = onetag.tag_id
                break

            if flag == 1:
                tag_to_use = Tag.objects.get(tag_id=tag_index)
                way.tag_ref.add(tag_to_use)
                way.save()

            else:
                #create a key value with text and id counter and also create a Tag using them
                print("creating new tag")
                key_count = Key.objects.filter(key_text=key_to_search).count()

                if key_count == 0:
                  key = Key(key_id=key_counter,key_text=key_to_search)
                  key.save()
                  key_counter += 1
                elif key_count >1:
                  countDec = key_count
                  while countDec > 1:
                    Key.objects.filter(key_text=key_to_search)[0].delete()
                    print("Deleted one similar key")
                    countDec -= 1

                value_count = Value.objects.filter(value_text=value_to_search).count()

                if value_count == 0:
                  value = Value(value_id=value_counter, value_text=value_to_search)
                  value.save()
                  value_counter += 1
                elif value_count > 1:
                  countVDec = value_count
                  while countVDec > 1:
                    Value.objects.filter(value_text=value_to_search)[0].delete()
                    countVDec -= 1

                unique_key = Key.objects.get(key_text=key_to_search)
                unique_value =Value.objects.get(value_text=value_to_search)

                tag_to_create = Tag(tag_id = tag_counter)
                tag_to_create.save()
                tag_to_create.key_ref.add(unique_key)
                tag_to_create.value_ref.add(unique_value)
                tag_to_create.save()
                tag_to_use = Tag.objects.get(tag_id=tag_counter)
                print(tag_to_use)
                tag_counter += 1
                
                way = Way.objects.get(way_id=wway_id)
                way.tag_ref.add(tag_to_use)
                way.save()

      elif primitive.tag == "relation":

        rrelation_id  = int(primitive.get("id"))
        rtimestamp    = primitive.get("timestamp")
        ruid          = int(primitive.get("uid"))
        ruser         = primitive.get("user")
        rversion      = int(primitive.get("version"))
        rchangeset    = int(primitive.get("changeset"))

        relation = Relation(rel_id=rrelation_id,timestamp=rtimestamp,uid=ruid,user=ruser,version=rversion,changeset=rchangeset)
        relation.save()

        for xmlTag in primitive.getchildren():


          if xmlTag.tag == "member":

            try:
              mem_type = xmlTag.get("type")
              mem_role = xmlTag.get("role")

              if xmlTag.get("type") == 'node':
                node_id_to_ref = xmlTag.get("ref")
                node_obj       = Node.objects.get(node_id=node_id_to_ref)
                member_node = Member(member_type=mem_type,member_role=mem_role,node_ref=node_obj)
                member_node.save()

              elif xmlTag.get("type") == 'way':
                way_id_to_ref  = xmlTag.get("ref")
                way_obj        = Way.objects.get(way_id=way_id_to_ref)
                member_way = Member(member_type=mem_type,member_role=mem_role,way_ref=way_obj)
                member_way.save()

            except Exception as e:
              print("The member already exists in some other relation")

          elif xmlTag.tag == "tag":

            get_key_text_from_xml = xmlTag.get("k")
            get_value_text_from_xml = xmlTag.get("v")

            #step 2 is to check if the tag with same key and value exists
            t = Tag.objects.all()
            flag= 0
            key_to_search = get_key_text_from_xml
            value_to_search = get_value_text_from_xml
            tag_to_use = Tag()
            tag_index = 0

            for onetag in t:
              if onetag.key_ref.all()[0].key_text == key_to_search and onetag.value_ref.all()[0].value_text == value_to_search:
                flag = 1
                tag_index = onetag.tag_id
                break

            if flag == 1:
                tag_to_use = Tag.objects.get(tag_id=tag_index)
                relation.tag_ref.add(tag_to_use)
                relation.save()

            else:
                #create a key value with text and id counter and also create a Tag using them
                print("creating new tag")
                key_count = Key.objects.filter(key_text=key_to_search).count()

                if key_count == 0:
                  key = Key(key_id=key_counter,key_text=key_to_search)
                  key.save()
                  key_counter += 1
                elif key_count >1:
                  countDec = key_count
                  while countDec > 1:
                    Key.objects.filter(key_text=key_to_search)[0].delete()
                    print("Deleted one similar key")
                    countDec -= 1

                value_count = Value.objects.filter(value_text=value_to_search).count()

                if value_count == 0:
                  value = Value(value_id=value_counter, value_text=value_to_search)
                  value.save()
                  value_counter += 1
                elif value_count > 1:
                  countVDec = value_count
                  while countVDec > 1:
                    Value.objects.filter(value_text=value_to_search)[0].delete()
                    countVDec -= 1

                unique_key = Key.objects.get(key_text=key_to_search)
                unique_value =Value.objects.get(value_text=value_to_search)

                tag_to_create = Tag(tag_id = tag_counter)
                tag_to_create.save()
                tag_to_create.key_ref.add(unique_key)
                tag_to_create.value_ref.add(unique_value)
                tag_to_create.save()
                tag_to_use = Tag.objects.get(tag_id=tag_counter)
                print(tag_to_use)
                tag_counter += 1
                
                relation_n = Relation.objects.get(rel_id=rrelation_id)
                relation_n.tag_ref.add(tag_to_use)
                relation_n.save()


  return render(request,'osm/confirm.html')
