from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from .views import FormView
from rest_framework_swagger.views import get_swagger_view
from geodjango.views import FormView, StopView, FeedView, AgencyView, RouteView, \
    NodeView, WayView, RelationView, TagView, KeyValueStringView, FeedBoundsView, \
    CorrespondenceView, ConversionView
schema_view = get_swagger_view(title='Gtfsintegrate API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', RedirectView.as_view(url="/gtfs/")),
    url(r'^gtfs/', include('gs.urls')),
    url(r'^swagger/', schema_view),

    url(r'^api/gtfsstopdata/$', StopView.as_view(), name="gtfsstopdata"),
    url(r'^api/formdata/$', FormView.as_view(), name="formdata"),
    url(r'^api/nodedata/$', NodeView.as_view(), name="nodedata"),
    url(r'^api/waydata/$', WayView.as_view(), name="waydata"),
    url(r'^api/relationdata/$', RelationView.as_view(), name="relationdata"),
    url(r'^api/tagdata/$', TagView.as_view(), name="tagdata"),
    url(r'^api/keyvaluestringdata/$', KeyValueStringView.as_view(), name="keyvaluestringdata"),
    url(r'^api/feedbounds/$', FeedBoundsView.as_view(), name="feedbounds"),

    url(r'^api/feeddata/$', FeedView.as_view(), name="feeddata"),
    url(r'^api/agencydata/$', AgencyView.as_view(), name="agencydata"),
    url(r'^api/routedata/$', RouteView.as_view(), name="routedata"),

    url(r'^api/correspondencedata/$', CorrespondenceView.as_view(), name="correspondencedata"),
    url(r'^api/conversiondata/$', ConversionView.as_view(), name="conversiondata"),
]
