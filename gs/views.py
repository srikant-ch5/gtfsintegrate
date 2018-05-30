from __future__ import unicode_literals
import logging

from django.shortcuts import render
from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand
from django.views.generic import ListView
from django.core.files.storage import FileSystemStorage
from django.contrib.gis.geos import Point

from multigtfs.models import Agency, Feed, Service
from multigtfs.management.commands.importgtfs import Command

from .models import Tag, KeyValueString, Node, Way, GTFSForm
from lxml import etree
from decimal import Decimal

from .forms import GTFSInfoForm
from django.utils import timezone
import requests

from .tasks import test2, download_feed_task, reset_feed, check_feeds_task

def feed_form(request):
	if request.method == 'POST':
		form = GTFSInfoForm(request.POST)
		#check if the url is already since the timestamp changes for every entry django creates a gtfs form
		is_feed_present = GTFSForm.objects.filter(url=request.POST['url'], osm_tag=request.POST['osm_tag'],
												  gtfs_tag=request.POST['gtfs_tag'])
		
		context = 'Error'
		if is_feed_present.count() > 0:
			print('Feed already exists with name trying to renew the feed in DB')

			formId = is_feed_present[0].id
			context = reset_feed(formId)

			#call celery task which checks the timestamp of the 
		else:
			context = "Creating new feed"
			print(context)

			if form.is_valid():
				gtfs_feed_info = form.save(commit=False)
				gtfs_feed_info.save()

				download_feed_task(gtfs_feed_info.id)

		return render(request, 'gs/form.html',{'form':form,'context':context})
	else:
		form = GTFSInfoForm()
		return render(request,'gs/form.html',{'form':form})


def home(request):
	check_feeds_task()
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

def celery_task(request):
	printnumbers()	

	return render(request, 'gs/task_template.html')