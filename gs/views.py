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

from .models import Tag, KeyValueString, Node, Way, GTFSForm
from lxml import etree
from decimal import Decimal
from django.contrib.gis.geos import Point

from .forms import GTFSInfoForm
from django.utils import timezone

import requests

def download_feed_in_db(file, file_name):
	feeds = Feed.objects.create(name=file_name)
	feeds.import_gtfs(file)
	print("Creating new gtfs file")

def feed_form(request):
	if request.method == 'POST':

		form = GTFSInfoForm(request.POST)
		#check if the url is already since the timestamp changes for every entry django creates a gtfs form
		is_feed_present = GTFSForm.objects.filter(url=request.POST['url'], osm_tag=request.POST['osm_tag'],
												  gtfs_tag=request.POST['gtfs_tag'],
												  frequency=request.POST['frequency'])
		
		feed_name = ((lambda: request.POST['name'], lambda: request.POST['osm_tag'])[request.POST['name']=='']())
		print(feed_name)
		if is_feed_present.count() > 0:
			print('Feed already exists with name %s ' %(feed_name))
			context = 'Feed already exists'
		else:
			context = "Creating new feed"
			print(context)

			#download the zip file 
			url = request.POST['url']
			r = requests.get(url, allow_redirects=True)
			feed_file = 'gs/gtfsfeeds/'+feed_name+'.zip'
			open(feed_file,'wb').write(r.content)

			download_feed_in_db(feed_file,feed_name)

			if form.is_valid():
				print("Going through this")
				gtfs_feed_info = form.save(commit=False)
				gtfs_feed_info.timestamp = timezone.now()
				gtfs_feed_info.save()

		return render(request, 'gs/form.html',{'form':form,'context':context})
	else:
		form = GTFSInfoForm()
		return render(request,'gs/form.html',{'form':form})

def home(request):
	return render(request,'gs/home.html')

def map(request):
	return render(request,'gs/map.html')

def download(request):

	if request.method == 'POST' and request.FILES['gtfsfile']:


		if(Feed.objects.filter(name=name).exists()):
			context = 'File is already present in the Database'
			print(context)
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
