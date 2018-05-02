from lxml import etree
'''import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osm.settings")
from models import Node,Tag,Way
'''
def parseXML(osmFile):

    with open(osmFile) as fileobj:
        xml = fileobj.read()

    root = etree.fromstring(xml)

    tag_counter = 10000

    for primitive in root.getchildren():
        if primitive.tag == "node":
            snode_id   = primitive.get("id")
            stimestamp = primitive.get("timestamp")
            suid       = primitive.get("uid")
            suser      = primitive.get("user")
            sversion   = primitive.get("version")
            schangeset = primitive.get("changeset")
            slat       = primitive.get("lat")
            slon       = primitive.get("lon")

            node = Node(node_id=snode_id, timestamp=stimestamp,uid=suid,user=suser,version=sversion,changeset=schangeset,lat=slat,lon=slon)
            node.save()
            
            for tag in primitive.getchildren():
                stag_id = tag_counter
                skey = tag.get("key")
                svalue = tag.get("value")
                tag_counter += tag_counter

                tag = Tag(tag_id=stag_id,key=skey,value=svalue,node_tag=node)
                tag.save()
        else:
            break

if __name__ == "__main__":
    parseXML("PTsamples.xml")
