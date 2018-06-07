from django.contrib.gis.db import models
from multigtfs.models import Feed

class GTFSForm(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=50, blank=True)
    osm_tag = models.CharField(max_length=20, blank=True)
    gtfs_tag = models.CharField(max_length=20, blank=True)
    frequency = models.IntegerField(blank=True, default=3)
    timestamp = models.DateTimeField(null=True)

    feed = models.OneToOneField('multigtfs.Feed', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
