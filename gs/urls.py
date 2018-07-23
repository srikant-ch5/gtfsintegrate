from django.conf.urls import url
from djgeojson.views import GeoJSONLayerView

import compare.views as compview
import conversionapp.views as conv_view
import osmapp.views as osmview
from multigtfs.models import Feed
from multigtfs.models import Stop
from osmapp.models import Node
from . import views
from .views import FeedListView

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url('^map/mapview/(?P<pk>\d+)/$', views.showmap, name="showmap"),
    url('^map/compmapview/(?P<pk>\d+)/$', compview.showmap_with_comp, name="showcompmap"),
    url(r'^osmnodedata/', GeoJSONLayerView.as_view(model=Node, properties=('id', 'version', 'feed', 'tags')),
        name="osmnodedata"),
    url(r'^stopdata/',
        GeoJSONLayerView.as_view(model=Stop, properties=(
            'stop_id', 'feed', 'name', 'normalized_name', 'zone', 'description', 'code')),
        name="stopdata"),
    # url(r'^waydata/', GeoJSONLayerView.as_view(model=Way,
    # properties=('id','version','visible','incomplete')), name="waydata"),
    url(r'^route_masters', osmview.get_route_master_relations, name="route_master"),
    url(r'^feed/', FeedListView.as_view(model=Feed), name='feed_list'),
    url(r'^feed_form/', views.feed_form, name='feed_form'),
    url(r'^bounds/', osmview.load_osm_data_view, name="load_osm_data"),
    url(r'^correspondence', views.correspondence_view, name="correspondence"),
    url(r'^conversionview', conv_view.conversionview, name="conversionview"),
    url(r'^conversion/$', conv_view.make_conversion, name="make-conversion"),
    url(r'^save-correspondence', conv_view.save_correspondence, name="save_correspondence"),
    url(r'^match_stop/$', compview.match_stop, name="match_stop"),
    url(r'^match_stops/$', compview.match_stops, name="match_stops"),
    url(r'^define_relation/(?P<pk>\d+)/$', compview.define_relation, name="define_relation"),
    url(r'^save_route_corr/$', compview.save_route_corr, name="save_route_corr"),
    url(r'^save_ag_corr/$', compview.save_ag_corr, name="save_ag_corr"),
    url(r'^saveextra/$', compview.saveextra, name="saveextra"),
]
