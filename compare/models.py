from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager
from django.contrib.gis.geos import Point, LineString


class CMP_Stop(models.Model):
    stop = models.ForeignKey('multigtfs.Stop',
                             on_delete=models.CASCADE,
                             null=True)
    node = models.ForeignKey('osmapp.Node',
                             on_delete=models.CASCADE,
                             null=True)
    geom = models.PointField(geography=True,
                             spatial_index=True,
                             null=True)
    node_geom = models.PointField(geography=True,
                                  spatial_index=True,
                                  null=True)
    type = models.CharField(max_length=10, null=True)
    objects = GeoManager()

    def gtfs_save_geom(self, stop_lat, stop_lon):
        self.geom = Point(stop_lat, stop_lon)
        self.save()

    class Meta:
        db_table = 'cmp_stop'
        app_label = 'compare'

class CMP_Line(models.Model):
    pass


class itineraries(models.Model):
    pass
