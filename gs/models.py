from __future__ import unicode_literals

from django.db import models
from django.contrib.gis.db import models

# Create your models here.

class Member(models.Model):
	member_type = models.CharField(max_length=20)
	member_ref  = models.IntegerField()
	member_role = models.CharField(max_length=20)
	relation    = models.ForeignKey(Relation, blank=True, null=True)

class Relation(models.Model):
	rel_id    = models.IntegerField()
	timestamp = models.CharField(max_length=20)
	uid       = models.IntegerField()
	user      = models.CharField(max_length=20)
	version   = models.IntegerField()
	changeset = models.IntegerField()

	def __str__(self):
		return self.rel_id

class Way(models.Model):
	way_id    = models.IntegerField(primary_key=True)
	timestamp = models.CharField(max_length=20)
	uid       = models.IntegerField()
	user      = models.CharField(max_length=20)
	version   = models.CharField(max_length=20)
	changeset = models.IntegerField()
	node_ref  = models.IntegerField(blank=True, null=True)

	def __str__(self):
		return self.way_id

class Node(models.Model):
	node_id   = models.IntegerField(primary_key=True)
	timestamp = models.CharField(max_length=20)
	uid       = models.IntegerField()
	user      = models.CharField(max_length=20)
	version   = models.IntegerField()
	changeset = models.IntegerField()
	lat       = models.DecimalField(max_digits=10, decimal_places=2)
	lon       = models.DecimalField(max_digits=10, decimal_places=2)
	#objects = models.GeoManager()

	def __str__(self):
		return self.node_id

class Tag(models.Model):
	tag_id 	 = models.IntegerField()
	key_id   = models.IntegerField()
	value_id = models.IntegerField()
	node_tag = models.ForeignKey(Node, blank=True, null=True)
	way_tag  = models.ForeignKey(Way, blank=True, null=True)
	relation_tag = models.ForeignKey(Relation, blank=True, null=True)
	def __str__(self):
		return self.tag_id