from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.db.models import PointField,LineStringField
from django.contrib.gis.geos import Point,LineString
from django.db.models import Manager as GeoManager

class KeyValueString(models.Model):
    value = models.TextField(unique=True)

    def __str__(self):
        return self.value

class Tag(models.Model):
    key   = models.ForeignKey('KeyValueString', related_name='keys', on_delete=models.CASCADE, blank=True)
    value = models.ForeignKey('KeyValueString', related_name='values', on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return " {} = {}".format(self.key,self.value)


    class Meta:
        unique_together = ("key","value")

    def add_tag(self, key, value):

        #check if the tag with same key
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
            elif value_count == 0 :
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

            tag = Tag.objects.get(key=avail_key_id,value=avail_value_id)
            return tag

class OSM_Primitive(models.Model):
    id        = models.BigIntegerField(primary_key=True)
    timestamp = models.DateTimeField(null=True)
    uid       = models.IntegerField(null=True)
    user      = models.TextField(null=True)#textfield for large ammount of text to store
    visible   = models.BooleanField()
    version   = models.IntegerField(null=True)
    changeset = models.IntegerField(null=True)
    tags      = models.ManyToManyField('Tag', blank=True)
    incomplete= models.BooleanField(default=False)

    class Meta:
        abstract = True

    def add_tag(self, key,value):
        self.tags = Tag.add_tag(key=key, value=value)
        self.save()
        return self

    def add_tags(self, tagsdict):
        for key, value in tagsdict:
            self.add_tag(key=key,value=value)

class Node(OSM_Primitive):
    geom = models.PointField(geography=True, spatial_index=True,null=True)#geography will force srid to be 4326
    objects = GeoManager()

    def set_cordinates(self, lat, lon):
        self.geom = Point(lon, lat)
        self.save()

class Way(OSM_Primitive):

    nodes = models.ManyToManyField('Node', through='WN',  related_name="nodes_in_way")
    geom  = models.LineStringField(blank=True, null=True)

    objects = GeoManager()

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

            max_sequence_num = max(sequence_list)+1

            wn = WN.objects.create(node= node, way=self, sequence=max_sequence_num)
            wn.save()
        return wn

    def add_nodes_geom(self):
        way_nodes = self.nodes.all()

        nodes = []

        for way_node in way_nodes:
            single_node_geom = list(way_node.geom)
            nodes.append(single_node_geom)

        self.geom = LineString(nodes)
        self.save()

class WN(models.Model):
    node     =  models.ForeignKey('Node',on_delete=models.CASCADE)
    way      =  models.ForeignKey('Way',on_delete=models.CASCADE)
    sequence =  models.PositiveIntegerField()

    class Meta:
        unique_together = ("node","way","sequence")

class MemberRelation(models.Model):
    parent      = models.ForeignKey('OSM_Relation', on_delete=models.CASCADE)
    member_node = models.ForeignKey('Node', on_delete=models.CASCADE, blank=True,null=True)
    member_way  = models.ForeignKey('Way', on_delete= models.CASCADE, blank=True,null=True)
    member_relation = models.ForeignKey('OSM_Relation', on_delete=models.CASCADE, blank=True, related_name="%(class)s_member_relations_rel",null=True)

    NODE = 'n'
    WAY = 'w'
    RELATION = 'r'
    TYPES = (
        (NODE, 'node'),
        (WAY, 'way'),
        (RELATION, 'relation')
    )

    type = models.CharField(max_length=1, choices=TYPES, blank=True)
    role = models.TextField( blank=True)
    sequence    = models.PositiveIntegerField(blank=True)

class OSM_Relation(OSM_Primitive):
    member_nodes_rel = models.ManyToManyField('Node', through='MemberRelation', through_fields=('parent','member_node'))
    member_ways_rel  = models.ManyToManyField('Way', through='MemberRelation', through_fields=('parent','member_way'))
    member_relations_rel = models.ManyToManyField('OSM_Relation', through='MemberRelation', through_fields=('parent','member_relation'))

    def add_member(self, member, memtype, role):
        count = self.memberrelation_set.count()
        rm = None

        if count==0:
            if memtype == 'node':
                rm = MemberRelation(parent=self, member_node=member, type='n', role=role, sequence=1)
            elif memtype == 'way':
                rm - MemberRelation(parent=self, member_way=member, type='w', role=role, sequence=1)
            elif memtype == 'relation':
                rm = MemberRelation(parent=self, member_relation=member, type='r', role=role, sequence=1)

        elif count > 0:
            mem_sequences = self.memberrelation_set.all() 
            sequence_list = []
            sequence      = 0

            for seq in mem_sequences:
                sequence_list.append(seq.sequence)

            max_sequence_num = max(sequence_list) + 1
            if memtype == 'node':
                rm = MemberRelation(parent=self, member_node=member, type='n', role=role, sequence=max_sequence_num)
            elif memtype == 'way':
                rm = MemberRelation(parent=self, member_way=member, type='w', role=role, sequence=max_sequence_num)
            elif memtype == 'relation':
                rm = MemberRelation(parent=self, member_relation=member, type='r', role=role, sequence=max_sequence_num)


        rm.save()

        return rm
