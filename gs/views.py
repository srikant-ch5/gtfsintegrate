from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime
import logging

from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand
from django.views.generic import ListView
from django.core.files.storage import FileSystemStorage

from multigtfs.models import Agency, Feed, Service

from multigtfs.management.commands.importgtfs import Command
from .models import Tag, KeyValueString, Node, Way
from lxml import etree
from decimal import Decimal
from django.contrib.gis.geos import Point

def home(request):
	return render(request,'gs/home.html')

def map(request):
	return render(request,'gs/map.html')

def download(request):

	if request.method == 'POST' and request.FILES['gtfsfile']:

		'''schedule = transitfeed.Schedule()
		schedule.AddAgency("File Agency","http://iflyagency.com",
                   "America/Los_Angeles")
		service_period = schedule.GetDefaultServicePeriod()
		service_period.SetStartDate("20160101")
		service_period.SetEndDate("20170101")
		service_period.SetWeekdayService(True)
		service_period.SetDateHasService('20070704', False)

		schedule.Validate()
		schedule.WriteGoogleTransitFeed('google_transit.zip')'''

		gtfs_feed = request.FILES['gtfsfile']
		name = gtfs_feed.name[:-4]

		if(Feed.objects.filter(name=name).exists()):
			context = 'File is already present in the Database'
		else:
			feeds = Feed.objects.create(name=name)
			feeds.import_gtfs(gtfs_feed)
			context = name + "GTFS file is uploaded to Database"

	return render(request,'gs/map.html',{'context':context})

class FeedListView(ListView):
	model = Feed
	template_name = 'gs/feeds.html'

	def get_queryset(self):
		return Feed.objects.all().order_by('id').reverse()
from django.shortcuts import render
from .models import Tag, KeyValueString, Node, Way,OSM_Relation, MemberRelation
from lxml import etree
from decimal import Decimal
from django.contrib.gis.geos import Point

def home(request):
	return render(request, 'osm/home.html')

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
	print(Node.objects.get(id=313586).tags.all())
	for stop_node in stop_nodes:
		tags = stop_node.tags.all()
		bus_stop_key_text = ['highway','bus']
		bus_stop_value_text = ['bus_stop','yes']
		is_bus_stop = 0

		for (sbus_stop_key_text, sbus_stop_value_text) in zip(bus_stop_key_text, bus_stop_value_text):
			bus_stop_key   = KeyValueString.objects.get(value=sbus_stop_key_text)
			bus_stop_value = KeyValueString.objects.get(value=sbus_stop_value_text)
			
			is_bus_stop = tags.filter(key=bus_stop_key, value=bus_stop_value).count()

		print(is_bus_stop)

	return render(request,'osm/stops.html')

def get_route_master_relations(request):
	return render(request, 'osm/route_master.html')

def get_route_relations(request):
	return render(request, 'osm/route.html')

def load(request):
	osmFile = 'osm/PTsamples.xml'
    with open(osmFile) as fileobj:
        xmlfile = fileobj.read()
    xmlfile = xmlfile.encode('utf-8')
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')

    root = etree.fromstring(xmlfile, parser=parser)

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

	return render(request,'osm/load.html')
