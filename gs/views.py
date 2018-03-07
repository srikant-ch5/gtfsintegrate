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
		name = "Test3"
		feeds = Feed.objects.create(name=name)
		feeds.import_gtfs(gtfs_feed)

	return render(request,'gs/download.html',{'uploaded_file_url':uploaded_file_url})

class FeedListView(ListView):
	model = Feed
	template_name = 'gs/feeds.html'

	def get_queryset(self):
		return Feed.objects.all().order_by('id').reverse()