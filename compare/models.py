from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager
from django.contrib.gis.geos import Point, LineString

class CMP_Stop(models.Model):

    gtfs_stop = models.ForeignKey('multigtfs.Stop', on_delete=models.CASCADE, null=True)
    fixed_match = models.OneToOneField('osmapp.Node', related_name='by_user', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.gtfs_stop)

class CMP_Line(models.Model):
    pass


class itineraries(models.Model):
    pass

