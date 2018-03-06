
from django.conf.urls import url,include
from django.contrib import admin
from django.views.generic import DetailView, ListView
from . import views
from multigtfs.models import Feed
from .views import FeedListView

urlpatterns = [
    url(r'^$',views.map,name="map"),
    url(r'feed/$', FeedListView.as_view(model=Feed), name='feed_list'),
    url(r'/downloading_page/',views.download,name="download")
]
