from __future__ import unicode_literals
from django.db import models
from django.contrib.gis.db import models


class Incidences(models.Model):
	name = models.CharField(max_length=20)
	location = models.PointField(srid=4200)
	objects = models.GeoManager()

	def __unicode__(self):
		return self.name

	class Meta:
		verbose_name_plural = " Incidences"