from django.conf.urls import url,include
from django.contrib import admin
from django.views.generic import RedirectView
from djgeojson.views import GeoJSONLayerView
from multigtfs.models import Stop
from osmapp.models import Node
from gs.models import GTFSForm
from django.views.generic import TemplateView
from .views import FormView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',RedirectView.as_view(url="/gtfs/")),
    url(r'^gtfs/',include('gs.urls')),
    url(r'^nodedata/', GeoJSONLayerView.as_view(model=Node, properties=('id')), name="nodedata"),
]
