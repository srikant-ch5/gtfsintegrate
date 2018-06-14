from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from .views import FormView
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Gtfsintegrate API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', RedirectView.as_view(url="/gtfs/")),
    url(r'^gtfs/', include('gs.urls')),
    url(r'^api/', schema_view)
]
