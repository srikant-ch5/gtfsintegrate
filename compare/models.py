from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager
from django.contrib.gis.geos import Point, LineString


class CMP_Stop(models.Model):
    gtfs_stop = models.ForeignKey('multigtfs.Stop', on_delete=models.CASCADE, null=True)
    fixed_match = models.OneToOneField('osmapp.Node', related_name='by_user', on_delete=models.CASCADE, blank=True,
                                       null=True)

    def to_xml(self, is_present, generator='Python Script', **tags):
        outputparams = {
            'newline': '\n',
            'indent': ' ',
            'upload': '',
            'generator': " generator='{}'".format(generator)
        }

        xml = '''<?xml version='1.0' encoding='UTF-8' ?>{newline}<osm version='0.6'{upload}{generator}>{newline}'''.format(
            **outputparams)

        xml += self.fixed_match.to_xml(outputparams=outputparams)

        xml += '''{newline}</osm>'''.format(**outputparams)

        return xml

    def __str__(self):
        return '{}'.format(self.gtfs_stop)


class CMP_Line(models.Model):
    pass


class itineraries(models.Model):
    pass
