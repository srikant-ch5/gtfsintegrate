from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager
from django.contrib.gis.geos import Point, LineString


class CMP_Stop(models.Model):
    gtfs_stop = models.ForeignKey('multigtfs.Stop', on_delete=models.CASCADE, null=True)
    fixed_match = models.OneToOneField('osmapp.Node', related_name='by_user', on_delete=models.CASCADE, blank=True,
                                       null=True)

    def to_xml(self, is_present, version_inc, **tags):
        outputparams = {
            'newline': '\n',
            'indent': ' ',
            'upload': '',
        }
        xml = ''
        xml += self.fixed_match.to_xml(version_inc, outputparams=outputparams)

        return xml

    def __str__(self):
        return '{}'.format(self.gtfs_stop)


class CMP_Line(models.Model):
    pass


class itineraries(models.Model):
    pass


class Line_Stop(models.Model):
    feed_id = models.IntegerField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    stop_id = models.CharField(max_length=500,blank=True, null=True)
    stop_code = models.CharField(max_length=500, blank=True, null=True)
    stop_name = models.CharField(max_length=100, blank=True, null=True)
    stop_time_stop_seq = models.IntegerField(blank=True, null=True)
    trip_extra_data = models.CharField(max_length=500, blank=True, null=True)
    route_id_db = models.IntegerField(blank=True, null=True)
    route_id = models.CharField(max_length=500, blank=True, null=True)
    route_short_name = models.CharField(max_length=500, blank=True, null=True)
    route_long_name = models.CharField(max_length=500, blank=True, null=True)
    route_desc = models.CharField(max_length=500, blank=True, null=True)
    route_color = models.CharField(max_length=500, blank=True, null=True)
    route_text_color = models.CharField(max_length=500, blank=True, null=True)
