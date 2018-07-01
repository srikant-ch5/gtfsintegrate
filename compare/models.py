from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager
from django.contrib.gis.geos import Point, LineString

class CMP_Stop(models.Model):
    conversion_method = (
        ('NAME', 'name'),
        ('LOCATION', 'location')
    )

    feed = models.ForeignKey('multigtfs.feed', on_delete=models.CASCADE, blank=True)
    gtfs_stop = models.ForeignKey('multigtfs.Stop', on_delete=models.CASCADE, null=True)
    matching_type = models.CharField(max_length=10, choices=conversion_method, blank=True)
    probable_matched_stops = models.ManyToManyField('osmapp.Node', related_name='by_app', blank=True)
    fixed_match = models.OneToOneField('multigtfs.stop', related_name='by_user', on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return '{}'.format(self.feed_id)

class CMP_Line(models.Model):
    pass


class itineraries(models.Model):
    pass

