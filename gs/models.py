from __future__ import unicode_literals
from django.db import models

class Member(models.Model):
  member_type = models.CharField(max_length=20)
  member_role = models.CharField(max_length=20)
  node_ref    = models.OneToOneField('Node',blank=True,null=True, on_delete=models.CASCADE)
  way_ref     = models.OneToOneField('Way', blank=True, null=True, on_delete=models.CASCADE)

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
  tag_id   = models.IntegerField(primary_key=True)
  key_ref  = models.ManyToManyField('Key', blank=True)
  value_ref= models.ManyToManyField('Value', blank=True)

  def __str__(self):
    return "%s" % self.tag_id

class Node(models.Model):
  node_id   = models.IntegerField(primary_key=True)
  timestamp = models.DateTimeField()
  uid       = models.IntegerField()
  user      = models.CharField(max_length=20)
  version   = models.IntegerField()
  changeset = models.IntegerField()
  lat       = models.DecimalField(max_digits=10, decimal_places=2)
  lon       = models.DecimalField(max_digits=10, decimal_places=2)
  tag_ref   = models.ManyToManyField('Tag', blank=True)
  #objects = models.GeoManager()

  def __str__(self):
    return "%s " % self.node_id

class Way(models.Model):
  way_id    = models.IntegerField(primary_key=True)
  timestamp = models.DateTimeField()
  uid       = models.IntegerField()
  user      = models.CharField(max_length=20)
  version   = models.IntegerField()
  changeset = models.IntegerField()
  node_ref  = models.ManyToManyField('Node', blank=True)
  tag_ref   = models.ManyToManyField('Tag', blank=True)

  def __str__(self):
    return "%s" % self.way_id

class Relation(models.Model):
  rel_id    = models.IntegerField(primary_key=True)
  timestamp = models.DateTimeField()
  uid       = models.IntegerField()
  user      = models.CharField(max_length=20)
  version   = models.IntegerField()
  changeset = models.IntegerField()
  mem_ref   = models.ForeignKey('Member', blank=True, null=True, on_delete=models.CASCADE)
  tag_ref   = models.ManyToManyField('Tag', blank=True)

  def __str__(self):
    return " %s " %self.rel_id


  def __str__(self):
    return " %s " %self.rel_id
