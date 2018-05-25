import string
from django.contrib.auth.models import User
from celery import shared_task,Celery
from celery.schedules import crontab
from geodjango.celery import app

@shared_task
def printnumbers():
	print(" 1 2 3 4 5 ")

@app.task
def test():
	print("I am not gonna say hello I will say it works instead")

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
	#calls test every 10 seconds
	print("10")
	sender.add_periodic_task(1.0,test('hello'), name="add every 10 seconds")
