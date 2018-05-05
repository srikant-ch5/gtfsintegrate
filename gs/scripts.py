from django.shortcuts import render
from lxml import etree
from .models import Node,Tag,Way,Relation,Value,Key
from decimal import Decimal

def storetoDb(request):

  #node = Node(node_id=45455454513586, timestamp='2018-01-15T17:26:05Z',uid=72151,user='GeorgFausB',version=13,changeset=55469382,lat=50.9558026,lon=6.9691347)
  #node.save()
  '''
  test_key = Key(key_id=995123,key_text="test_key")
  test_value =Value(value_id=239122,value_text="test_value")
  test_key.save()
  test_value.save()
  test_tag = Tag(tag_id=9848422595)
  test_tag.save()
  test_tag.key_ref.add(test_key)
  test_tag.value_ref.add(test_value)
  
  t = Tag.objects.get(tag_id=9848422595)
  t.key_ref.all().values_list('key_text',flat=True)
  '''
  #node2 = Node(node_id=234235424544545,timestamp='234tz',uid=234234,user='Srikant',version=1,changeset=23,lat=56.67,lon=6.889,tag_ref=tag1)
  #node2.save()

  t = Tag.objects.all()
  flag= 0
  key_to_search = 'test_key'
  value_to_search = 'test_value'

  for onetag in t:
    for i in range(0,onetag.key_ref.count()):
      print ("%s   %s" %(onetag.key_ref.all()[i].key_text,onetag.value_ref.all()[i]))
      if onetag.key_ref.all()[i].key_text == key_to_search and onetag.value_ref.all()[i].value_text == value_to_search:
        flag = 1
        break

  if flag == 1:
      print("Found")
  else:
      print("Not found")
  return render(request,'osm/confirm.html')

def storeIntoDb(request):

  osmFile = 'osm/PTsamples.xml'
  with open(osmFile) as fileobj:
    xmlfile = fileobj.read()
  xmlfile = xmlfile.encode('utf-8')
  parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

  root = etree.fromstring(xmlfile,parser=parser)

  tag_counter = 10000
  key_counter = 5000
  value_counter = 5000

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

            for onetag in t:
              for i in range(0,onetag.key_ref.count()):
                #print ("%s   %s" %(onetag.key_ref.all()[i].key_text,onetag.value_ref.all()[i]))
                if onetag.key_ref.all()[i].key_text == key_to_search and onetag.value_ref.all()[i].value_text == value_to_search:
                  flag = 1
                  break

            if flag == 1:
                print("Found")
                tag_to_use = Tag.objects.filter(tag_id=onetag.tag_id)[0]
                #return the tag as it is already in the DB

            else:
                #create a key value with text and id counter and also create a Tag using them
                key_count = Key.objects.filter(key_text=key_to_search).count()

                if key_count == 0:
                  key = Key(key_id=key_counter,key_text=key_to_search)
                  key.save()
                  key_counter += 1
                elif key_count >1:
                  countDec = key_count
                  while countDec > 1:
                    Key.objects.filter(key_text=key_to_search)[0].delete()
                    countDec -= 1
                unique_key = Key.objects.get(key_text=key_to_search)
                unique_key.save()
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

                unique_value =Value.objects.filter(value_text=value_to_search)
                unique_value.save()

                tag = Tag(tag_id=tag_counter,key_ref=unique_key,value_ref=unique_value)
                tag.save()
                tag_to_use = Tag.objects.filter(tag_id=tag_counter)
                tag_counter += 1

            #print("Tag %d (%d %s)(%d %s)" %(tag_counter,keyid_counter,skey,valueid_counter,svalue))
          node_to_add_tag = Node.objects.get(node_id=snode_id)
          node_to_add_tag.tag_ref.add(tag_to_use)
          node_to_add_tag.save()
      '''
      elif primitive.tag == "way":
          #w prefix refers single way
          wway_id    = int(primitive.get("id"))
          wtimestamp = primitive.get("timestamp")
          wuid       = int(primitive.get("uid"))
          wuser      = primitive.get("user")
          wversion   = int(primitive.get("version"))
          wchangeset = int(primitive.get("changeset"))
          
          way = Way(way_id=wway_id,timestamp=wtimestamp,uid=wuid,user=wuser,version=wversion,changeset=wchangeset)
          way.save()

          for xmlTag in primitive.getchildren():
              if xmlTag.tag == "nd":

                  nodeReference = int(xmlTag.get("ref"))
                  node_in_way  = Node.objects.filter(node_id=nodeReference)[0]
                  way.node_set.add(node_in_way)
                  way.save()

              elif xmlTag.tag == "tag":
                  wtag_id = tag_counter
                  wkey    = xmlTag.get("k")
                  wvalue  = xmlTag.get("v")

                  #print("Key %d %s" %(keyid_counter,skey))
                  #print("Value %d %s " %(valueid_counter,svalue))
                  key = Key(key_id=keyid_counter,key_text=wkey)
                  key.save()
                  value = Value(value_id = valueid_counter,value_text=wvalue)
                  value.save()
                
                  tag_counter += 1
                  keyid_counter += 1
                  valueid_counter += 1

                  print("Tag %d (%d %s)(%d %s)" %(tag_counter,keyid_counter,wkey,valueid_counter,wvalue))
                  tag = Tag(tag_id=stag_id,key_ref=key,value_ref=value,node_tag=node)
                  tag.save()
                  way.tag_set.add(tag)
                  way.save()

      elif primitive.tag == "relation":
          rrelation_id    = int(primitive.get("id"))
          rtimestamp = primitive.get("timestamp")
          ruid       = int(primitive.get("uid"))
          ruser      = primitive.get("user")
          rversion   = int(primitive.get("version"))
          rchangeset = int(primitive.get("changeset"))
          
          #print("         Relation   %d %s %d %s %d %d" %(rrelation_id,rtimestamp,ruid,ruser,rversion,rchangeset))
          relation = Relation(relation_id=rrelation_id,timestamp=rtimestamp,uid=ruid,user=ruser,version=rversion,changeset=rchangeset)
          relation.save()

          for xmlTag in primitive.getchildren():

              if xmlTag.tag == "member":
                  mem_type = xmlTag.get("type")
                  mem_ref = int(xmlTag.get("ref"))

                  if mem_type == "node":
                      node = Node.objects.filter(node_id=mem_ref)
                      relation.node_set.add(node)
                  elif mem_type == "way":
                      way = Way.objects.filter(way_id=mem_ref)
                      relation.way_set.add(way)
  
                  relation.save()
              elif xmlTag.tag == "tag":
                  rtag_id = tag_counter
                  rkey    = xmlTag.get("k")
                  rvalue  = xmlTag.get("v")

                  key = Key(key_id=keyid_counter,key_text=rkey)
                  key.save()
                  value = Value(value_id = valueid_counter,value_text=rvalue)
                  value.save()

                  tag_counter += 1
                  keyid_counter += 1
                  valueid_counter += 1
                  #print("Tag %d (%d %s)(%d %s)" %(tag_counter,keyid_counter,rkey,valueid_counter,rvalue))
                  
                  tag = Tag(tag_id=stag_id,key_ref=key,value_ref=value,node_tag=node)
                  tag.save()
                  relation.tag_set.add(tag)
                  relation.save()'''

  return render(request,'osm/confirm.html')
