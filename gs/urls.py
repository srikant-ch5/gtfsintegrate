from django.conf.urls import url, include

from multigtfs.models import Feed
from osmapp.models import Node
from multigtfs.models import Stop
from compare.models import CMP_Stop

from . import views
from .views import FeedListView
from djgeojson.views import GeoJSONLayerView

from geodjango.views import FormView
import osmapp.views as osmview
import compare.views as compview

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^osm/', osmview.load, name="osm"),
    url(r'^nodedata/', GeoJSONLayerView.as_view(model=Node, properties=('id')), name="nodedata"),
    url(r'^stopdata/', GeoJSONLayerView.as_view(model=Stop, properties=('id','feed')), name="stopdata"),
    url(r'^gtfsstopdata',GeoJSONLayerView.as_view(model=CMP_Stop), name="gtfsstopdata"),
    # url(r'^waydata/', GeoJSONLayerView.as_view(model=Way, properties=('id','version','visible','incomplete')), name="waydata"),
    url(r'^stops/', compview.get_gtfs_stops, name="stops"),
    url(r'^route_masters', osmview.get_route_master_relations, name="route_master"),
    url(r'^map/', views.map, name="map"),
    url(r'^feed/', FeedListView.as_view(model=Feed), name='feed_list'),
    url(r'^feed_form/', views.feed_form, name='feed_form'),
    url(r'^formdata/(?P<pk>\d+)/$', FormView.as_view(), name="formdata"),
]
