from lxml import etree
from models import Node,Tag,Way,Relation,Value,Key
from decimal import Decimal

def parseXML(osmFile):

    with open(osmFile) as fileobj:
        xml = fileobj.read()

    root = etree.fromstring(xml)

    tag_counter = 10000
    keyid_counter = 5000
    valueid_counter = 5000

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

            print(" Node %d %s %d %s %d %d %f %f" % (snode_id,stimestamp,suid,suser,sversion,schangeset,slat,slon))
            node = Node(node_id=snode_id, timestamp=stimestamp,uid=suid,user=suser,version=sversion,changeset=schangeset,lat=slat,lon=slon)
            node.save()
            for xmlTag in primitive.getchildren():
                stag_id = tag_counter
                skey = xmlTag.get("k")
                svalue = xmlTag.get("v")

                print("Key %d %s" %(keyid_counter,skey))
                print("Value %d %s " %(valueid_counter,svalue))
                
                
                key = Key(key_id=keyid_counter,key_text=skey)
                key.save()
                value = Value(value_id=valueid_counter,value_text=svalue)
                value.save()
                

                tag_counter += 1
                keyid_counter += 1
                valueid_counter += 1

                print("Tag %d (%d %s)(%d %s)" %(tag_counter,keyid_counter,skey,valueid_counter,svalue))
                tag = Tag(tag_id=stag_id,key_ref=key,value_ref=value,node_tag=node)
                tag.save()
                node.tag_set.add(tag)
                node.save()
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
                    #reference for node
                    nodeReference = int(xmlTag.get("ref"))
                    node_in_way  = Node.objects.filter(node_id=nodeReference)
                    way.node_set.add(node_in_way)
                    way.save()

                elif xmlTag.tag == "tag":
                    wtag_id = tag_counter
                    wkey    = xmlTag.get("k")
                    wvalue  = xmlTag.get("v")

                    key = Key(key_id=keyid_counter,key_text=wkey)
                    key.save()
                    value = Value(value_id = valueid_counter,value_text=wvalue)
                    value.save()

                    tag_counter += tag_counter
                    keyid_counter += keyid_counter
                    valueid_counter += valueid_counter

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
            
            relation = Relation(relation_id=rrelation_id,timestamp=rtimestamp,uid=ruid,user=ruser,version=rversion,changeset=rchangeset)
            relation.save()

            if primitive.tag == 'member':

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

                        tag_counter += tag_counter
                        keyid_counter += keyid_counter
                        valueid_counter += valueid_counter

                        tag = Tag(tag_id=stag_id,key_ref=key,value_ref=value,node_tag=node)
                        tag.save()
                        relation.tag_set.add(tag)
                        relation.save()

if __name__ == "__main__":
    parseXML("PTsamples.xml")
