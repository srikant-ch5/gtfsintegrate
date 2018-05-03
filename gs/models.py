from __future__ import unicode_literals

from django.db import models
from django.contrib.gis.db import models

# Create your models here.

class Relation(models.Model):
	rel_id    = models.IntegerField()
	timestamp = models.CharField(max_length=20)
	uid       = models.IntegerField()
	user      = models.CharField(max_length=20)
	version   = models.IntegerField()
	changeset = models.IntegerField()

	def __str__(self):
		return " %s " %self.rel_id

class Member(models.Model):
	member_type = models.CharField(max_length=20)
	member_ref  = models.IntegerField()
	member_role = models.CharField(max_length=20)
	relation    = models.ForeignKey(Relation, blank=True, null=True)

class Node(models.Model):
	node_id   = models.IntegerField(primary_key=True)
	timestamp = models.CharField(max_length=20)
	uid       = models.IntegerField()
	user      = models.CharField(max_length=20)
	version   = models.IntegerField()
	changeset = models.IntegerField()
	lat       = models.DecimalField(max_digits=10, decimal_places=2)
	lon       = models.DecimalField(max_digits=10, decimal_places=2)
	way_ref   = models.ForeignKey(Way, blank=True,null=True)
	rel_ref   = models.ForeignKey(Relation, blank=True,null=True)

	#objects = models.GeoManager()

	def __str__(self):
		return " %s " % self.node_id

class Way(models.Model):
	way_id    = models.IntegerField(primary_key=True)
	timestamp = models.CharField(max_length=20)
	uid       = models.IntegerField()
	user      = models.CharField(max_length=20)
	version   = models.IntegerField(max_length=20)
	changeset = models.IntegerField()
	rel_ref  = models.ForeignKey(Relation, blank=True, null=True)

	def __str__(self):
		return " %s " % self.way_id

class Key(models.Model):
	key_id = models.IntegerField()
	key_text = models.CharField(max_length=50)

	def __str__(self):
		return " %s " % self.key_id

class Value(models.Model):
	value_id = models.IntegerField()
	value_text = models.CharField(max_length=50)

	def __str__(self):
		return " %s " % self.value_id

class Tag(models.Model):
	tag_id 	 = models.IntegerField(primary_key=True)
	key_ref  = models.OneToOneField(Key, blank=True, null=True)
	value_ref= models.OneToOneField(Value, blank=True, null=True)
	node_tag = models.ForeignKey(Node, blank=True, null=True)
	way_tag  = models.ForeignKey(Way, blank=True, null=True)
	relation_tag = models.ForeignKey(Relation, blank=True, null=True)

	def __str__(self):
		return " %s " % self.tag_id