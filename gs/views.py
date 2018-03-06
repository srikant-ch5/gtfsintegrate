from __future__ import unicode_literals
from django.shortcuts import render
from datetime import datetime
import logging

from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand
from django.views.generic import ListView

from multigtfs.models import Agency, Feed, Service

from multigtfs.management.commands.importgtfs import Command
def map(request):
	return render(request,'gs/map.html')

def download(request):

	if request.method == 'POST':
		gtfs_feed = "gtfs.zip"
		unset_name = 'Imported at %s' % datetime.now()
		name = "BelgiumGTFS(South)"
		feeds = Feed.objects.create(name=name)
		feeds.import_gtfs(gtfs_feed)

		context = {'Downloaded'}
		
	return render(request,'gs/download.html',{'context':context})

class FeedListView(ListView):
	model = Feed
	template_name = 'gs/feeds.html'

	def get_queryset(self):
		return Feed.objects.all().order_by('id').reverse()