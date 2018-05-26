import string
import os
import requests
import datetime

from django.contrib.auth.models import User
from celery import shared_task,Celery, task
from celery.schedules import crontab
from geodjango.celery import app
from .models import GTFSForm

from multigtfs.models import Agency, Feed, Service
from multigtfs.management.commands.importgtfs import Command

#should be included here app will refer to gs https://groups.google.com/forum/#!topic/celery-users/XiSDiNjBR6k
app = Celery()

@shared_task
def test():
	print("I am not gonna say hello I will say it works instead")

@app.task
def test2():
    print("HI")

@app.task
def rename_feed(name):
	present_name = name
	feed = Feed.objects.get(name=name)
	agencies = feed.agency_set.all()
	update_name = ''

	for agency in agencies:
		agname = agency.name.replace(" ","")
		update_name += agname
		#remove space
	feed.name = update_name
	feed.save()
	to_change = '/home/srikant/workspace/allprojects/gtfs/env/gtfsapp/gtfsintegrate/gs/gtfsfeeds/'+name+'.zip'
	update_name = '/home/srikant/workspace/allprojects/gtfs/env/gtfsapp/gtfsintegrate/gs/gtfsfeeds/'+update_name+'.zip'
	os.rename(to_change,update_name)



@app.task
def download_feed_in_db(file, file_name):
	feeds = Feed.objects.create(name=file_name)
	feeds.import_gtfs(file)
	print("Creating new gtfs file")
	print(feeds.id)
	rename_feed(file_name)

@app.task
def download_feed_task(formId):
	#get url osm_tag gtfs_tag of the user entered form
	user_form 		= GTFSForm.objects.get(id=formId)
	entered_url	    = user_form.url
	entered_osm_tag = user_form.osm_tag
	entered_gtfs_tag= user_form.gtfs_tag
	entered_name  	= user_form.name
	user_form.timestamp = datetime.datetime.now().isoformat()
	user_form.save()

	r = requests.get(entered_url, allow_redirects=True)

	#temporary name for file
	feed_name = ((lambda: entered_name, lambda: entered_osm_tag)[entered_name=='']())
	feed_file = 'gs/gtfsfeeds/'+feed_name+'.zip'
	open(feed_file,'wb').write(r.content)

	download_feed_in_db(feed_file,feed_name)

