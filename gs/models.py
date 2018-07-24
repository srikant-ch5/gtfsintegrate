from django.contrib.gis.db import models

from multigtfs.models import Feed


class GTFSForm(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=500, blank=True)
    frequency = models.IntegerField(blank=True, default=3)
    timestamp = models.DateTimeField(null=True)
    feed_id = models.IntegerField(blank=True, default=-1)

    def __str__(self):
        return self.name
