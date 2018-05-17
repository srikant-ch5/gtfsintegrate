from django.contrib.gis.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db.models import Manager as GeoManager


class KeyValueString(models.Model):
    value = models.TextField(unique=True)

    def __str__(self):
        return self.value


class Tag(models.Model):
    key = models.ForeignKey('KeyValueString', related_name='keys', on_delete=models.CASCADE, blank=True)
    value = models.ForeignKey('KeyValueString', related_name='values', on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return " {} = {}".format(self.key, self.value)

    class Meta:
        unique_together = ("key", "value")

    def add_tag(self, key, value):

        # check if the tag with same key
        try:
            found_key = KeyValueString.objects.filter(value=key)
            count = found_key.count()
            if count > 0:

                self.key = found_key[0]
            elif count == 0:
                newkey = KeyValueString(value=key)
                newkey.save()
                self.key = newkey

            found_value = KeyValueString.objects.filter(value=value)
            value_count = found_value.count()
            if value_count > 0:
                self.value = found_value[0]
            elif value_count == 0:
                newvalue = KeyValueString(value=value)
                newvalue.save()
                self.value = newvalue

            self.save()

            return self
        except Exception as e:
            avail_key = KeyValueString.objects.get(value=key)
            avail_key_id = avail_key.id
            avail_value = KeyValueString.objects.get(value=value)
            avail_value_id = avail_value.id

            tag = Tag.objects.get(key=avail_key_id, value=avail_value_id)
            return tag


class OSM_Primitive(models.Model):
    _id = models.BigIntegerField(primary_key=True, db_column="id")
    timestamp = models.DateTimeField(null=True)
    _uid = models.IntegerField(null=True, db_column="uid")
    user = models.TextField(null=True)  # textfield for large amount of text to store
    visible = models.BooleanField()
    _version = models.IntegerField(null=True, db_column="version")
    _changeset = models.IntegerField(null=True, db_column="changeset")
    tags = models.ManyToManyField('Tag', blank=True)
    incomplete = models.BooleanField(default=False)

    class Meta:
        abstract = True

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = int(value)

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = int(value)

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = int(value)

    @property
    def changeset(self):
        return self._changeset

    @changeset.setter
    def changeset(self, value):
        self._changeset = int(value)

    def add_tag(self, key, value):
        self.tags = Tag.add_tag(key=key, value=value)
        self.save()
        return self

    def add_tags(self, tagsdict):
        for key, value in tagsdict:
            self.add_tag(key=key, value=value)


class Node(OSM_Primitive):
    geom = models.PointField(geography=True, spatial_index=True, null=True)  # geography will force srid to be 4326
    objects = GeoManager()

    def set_coordinates(self, lon, lat):
        self.geom = Point(float(lon), float(lat))
        self.save()


class Way(OSM_Primitive):
    nodes = models.ManyToManyField('Node', through='WN', related_name="nodes_in_way")

    def add_node(self, node):
        count = self.wn_set.count()
        if count == 0:
            wn = WN.objects.create(node=node, way=self, sequence=1)
            wn.save()

        else:
            node_sequences = self.wn_set.all()
            sequence_list = []
            sequence = 0

            for seq in node_sequences:
                sequence_list.append(seq.sequence)

            max_sequence_num = max(sequence_list) + 1

            wn = WN.objects.create(node=node, way=self, sequence=max_sequence_num)
            wn.save()
        return wn


class WN(models.Model):
    node = models.ForeignKey('Node', on_delete=models.CASCADE)
    way = models.ForeignKey('Way', on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()

    class Meta:
        unique_together = ("node", "way", "sequence")


class MemberRelation(models.Model):
    parent = models.ForeignKey('OSM_Relation', on_delete=models.CASCADE)
    member_node = models.ForeignKey('Node', on_delete=models.CASCADE, blank=True)
    member_way = models.ForeignKey('Way', on_delete=models.CASCADE, blank=True)
    member_relation = models.ForeignKey('OSM_Relation', on_delete=models.CASCADE, blank=True,
                                        related_name="%(class)s_member_relations_rel")

    NODE = 'n'
    WAY = 'w'
    RELATION = 'r'
    TYPES = (
        (NODE, 'node'),
        (WAY, 'way'),
        (RELATION, 'relation')
    )

    type = models.CharField(max_length=1, choices=TYPES)
    role = models.TextField()
    sequence = models.PositiveIntegerField()


class OSM_Relation(models.Model):
    member_nodes_rel = models.ManyToManyField('Node', through='MemberRelation',
                                              through_fields=('parent', 'member_node'))
    member_ways_rel = models.ManyToManyField('Way', through='MemberRelation', through_fields=('parent', 'member_way'))
    member_relations_rel = models.ManyToManyField('OSM_Relation', through='MemberRelation',
                                                  through_fields=('parent', 'member_relation'))
