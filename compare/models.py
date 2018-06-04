from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager


class CMP_Stop(models.Model):
    stop = models.ForeignKey('multigtfs.Stop', on_delete=models.CASCADE)
    node = models.ForeignKey('osmapp.Node', on_delete=models.CASCADE)
    stop_geom = models.PointField(geography=True, spatial_index=True)
    node_geom = models.PointField(geography=True, spatial_index=True)
    obejcts = GeoManager()

    class Meta:
        db_table = 'cmp_stop'
        app_label = 'compare'

#class CMP_Line(models.Model):

# class iteneraries(models.Model):
