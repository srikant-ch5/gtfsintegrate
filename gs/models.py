from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.db.models import PointField,LineStringField
from django.contrib.gis.geos import Point,LineString
from django.db.models import Manager as GeoManager
from django.utils import timezone

class GTFSForm(models.Model):
  url = models.URLField()
  name = models.CharField(max_length=50, blank=True )
  osm_tag   = models.CharField(max_length=20, blank=True)
  gtfs_tag  = models.CharField(max_length=20, blank=True)
  frequency = models.IntegerField(blank=True, default=3)
  timestamp = models.DateTimeField(null=True)

  def __str__(self):
    return self.name
