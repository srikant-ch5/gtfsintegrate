import string
import os
import requests
from django.utils import timezone

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
	print("shared_task")

@app.task
def test2():
	print("HI")

@app.task
def rename_feed(name, formId):
	present_name = name
	feed = Feed.objects.get(name=name)
	agencies = feed.agency_set.all()
	update_name = ''

	for agency in agencies:
		agname = agency.name.replace(" ","")
		update_name += agname
		#remove space
	user_form 		= GTFSForm.objects.get(id=formId)
	user_form.name  = update_name
	user_form.save()
	feed.name = update_name
	feed.save()
	to_change = os.path.join(os.path.dirname(os.path.abspath(__file__)),"gtfsfeeds/") +name+'.zip'
	update_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),"gtfsfeeds/")+update_name+'.zip'
	os.rename(to_change,update_name)

@app.task
def download_feed_in_db(file, file_name, code, formId):
	feeds = Feed.objects.create(name=file_name)
	feeds.import_gtfs(file)
	print("Creating new gtfs file")
	print(feeds.id)

	if code == 'not_present':
		rename_feed(file_name, formId)
	
@app.task
def download_feed_with_url(download_url, save_feed_name, code, formId):
	r = requests.get(download_url, allow_redirects=True)

	feed_file = 'gs/gtfsfeeds/'+save_feed_name+'.zip'
	#temporary name for file
	if code == 'present':
		os.remove(feed_file)
	
	open(feed_file,'wb').write(r.content)

	download_feed_in_db(feed_file,save_feed_name, code, formId)

@app.task
def download_feed_task(formId):
	#get url osm_tag gtfs_tag of the user entered form
	user_form 		= GTFSForm.objects.get(id=formId)
	entered_url	    = user_form.url
	entered_osm_tag = user_form.osm_tag
	entered_gtfs_tag= user_form.gtfs_tag
	entered_name  	= user_form.name
	user_form.timestamp = timezone.now()	
	user_form.save()

	feed_name = ((lambda: entered_name, lambda: entered_osm_tag)[entered_name=='']())

	code = 'not_present'
	download_feed_with_url(entered_url, feed_name, code, formId)

@app.task
def check_feeds_task():
	#keep on checking the feeds for every five days all the feeds are downloaded again into the database
	#1. get all the feeds
	all_feeds = Feed.objects.all()

	for feed in all_feeds:
		#get the name of the feed
		feed_name = feed.name
		print(feed_name)
		feed_form = GTFSForm.objects.get(name=feed_name)
		feed_url  = feed_form.url
		feed_timestamp = feed_form.timestamp
		current_timestamp= timezone.now()
		print("{}  {}".format(feed_timestamp,current_timestamp))

		ts_diff = str(current_timestamp - feed_timestamp)[0]

		if int(ts_diff) > 2:
			download_feed_with_url(feed_url, feed_name, code)	

		code = 'present'
		print("renewing the feed")
		download_feed_with_url(feed_url, feed_name, code, feed_form.id)
		print("Feed renewed")
		feed.delete()

@app.task
def reset_feed(formId):
	form = GTFSForm.objects.get(id=formId)
	form_timestamp = form.timestamp
	current_timestamp = timezone.now()
	form_name = form.name

	ts_diff = str(current_timestamp - form_timestamp)[0]
	status = 'The Feed is up to date'

	code = 'present'
	if int(ts_diff) > 2:
		status = 'Reseting feed with latest data'
		form.timestamp = timezone.now()
		form.save()
		Feed.objects.filter(name=form_name).all().delete()
		download_feed_with_url(form.url, form.name, code, formId)

	return status



