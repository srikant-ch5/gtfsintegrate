
from django.conf.urls import url,include
from django.contrib import admin
from django.views.generic import DetailView, ListView
from . import views
from multigtfs.models import Feed
from .views import FeedListView
import osmapp.views as osmview
from djgeojson.views import GeoJSONLayerView
from multigtfs.models import Stop
from geodjango.views import FormView

urlpatterns = [
    url(r'^$',views.home,name="home"),
    url(r'^osm/',osmview.load ,name="osm"),
    url(r'^nodedata/', GeoJSONLayerView.as_view(model=Stop, properties=('id')), name="nodedata"),
    #url(r'^waydata/', GeoJSONLayerView.as_view(model=Way, properties=('id','version','visible','incomplete')), name="waydata"),
    url(r'^stops/',osmview.get_stops, name="stops"),
    url(r'^route_masters', osmview.get_route_master_relations, name="route_master"),
    url(r'^map/', views.map,name="map"),
    url(r'^feed/', FeedListView.as_view(model=Feed), name='feed_list'),
    url(r'^feed_form/', views.feed_form , name='feed_form'),
    url(r'^celery_task/', views.celery_task, name="celery_task"),
    url(r'^formdata/(?P<pk>\d+)/$',FormView.as_view(),name="formdata")
]
