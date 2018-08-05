from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField


class CMP_Stop(models.Model):
    gtfs_stop = models.ForeignKey('multigtfs.Stop', on_delete=models.CASCADE, null=True)
    fixed_match = models.OneToOneField('osmapp.Node', related_name='by_user', on_delete=models.CASCADE, blank=True,
                                       null=True)

    def cmp_single_node_to_xml(self, is_present, version_inc, **tags):
        outputparams = {
            'newline': '',
            'indent': '',
            'upload': 'True',
        }
        xml = ''
        xml += self.fixed_match.single_node_to_xml(version_inc, outputparams=outputparams)

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
    stop_id = models.CharField(max_length=500, blank=True, null=True)
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


class Relation_data(models.Model):
    token = models.CharField(max_length=200, blank=True, null=True)
    nodes_ids = ArrayField(models.BigIntegerField(), blank=True, null=True)
    relations_info = ArrayField(ArrayField(models.CharField(max_length=250, blank=True, null=True)), blank=True,
                               null=True)
    rels_ids = ArrayField(models.BigIntegerField(), blank=True, null=True)
    ways_ids = ArrayField(models.BigIntegerField(), blank=True, null=True)

    def __str__(self):
        return '{} '.format(self.token)
