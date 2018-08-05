from typing import Tuple

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, LineString
from django.contrib.postgres.fields import ArrayField
from django.db.models import Manager as GeoManager

# for string matcing
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


# model for storing bounds specific to the operator

def xmlsafe(name):
    return str(name).replace('&', '&amp;').replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;").replace('"',
                                                                                                                    "&quot;")


def urlsafe(name):
    return xmlsafe(name).replace(' ', '%20')


class Bounds(models.Model):
    feed_id = models.IntegerField(blank=True)
    operator_name = models.CharField(max_length=200)
    outer_bound = ArrayField(ArrayField(models.FloatField()), blank=True)
    inner_bound = models.CharField(max_length=10000000, blank=True)

    def __str__(self):  # __unicode__ on Python 2
        return self.operator_name


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
        unique_together = ("key", "value")  # type: Tuple[str, str]

    def to_xml(self, outputparams=None):
        if outputparams is None:
            _outputparams = {'newline': '\n', 'indent': ' '}
        else:
            _outputparams = outputparams

        key = self.key.value
        value = self.value.value.replace('&', '&amp;').replace("'", "&apos;").replace("<", "&lt;").replace(">",
                                                                                                           "&gt;").replace(
            '"', "&quot;")

        self.xml = ''

        self.xml += "{newline}  <tag k='{key}' v='{value}' />".format(key=key, value=value, **_outputparams)

        return self.xml

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
    id = models.BigIntegerField(primary_key=True)
    timestamp = models.DateTimeField(null=True)
    uid = models.IntegerField(null=True)
    user = models.TextField(null=True)  # textfield for large ammount of text to store
    visible = models.BooleanField()
    version = models.IntegerField(null=True)
    changeset = models.IntegerField(null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    incomplete = models.BooleanField(default=False)
    feed = models.ForeignKey('multigtfs.Feed', on_delete=models.CASCADE, blank=True, null=True)
    purpose = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        abstract = True

    def add_tag(self, key, value):
        self.tags = Tag.add_tag(key=key, value=value)
        self.save()
        return self

    def add_tags(self, tagsdict):
        for key, value in tagsdict:
            self.add_tag(key=key, value=value)

    def base_to_xml(self, primitive, outputparams=None, body='', attributes=[], modify=False):
        if outputparams is None:
            _outputparams = {'newline': '\n', 'indent': '  '}
        else:
            _outputparams = outputparams
        _outputparams['primitive'] = primitive

        if modify:
            self.xml = "{newline}<{primitive} action='modify' ".format(**_outputparams)
        else:
            self.xml = '{newline}<{primitive} '.format(**_outputparams)

        tags = self.tags.all()

        for attr, value in self.__dict__.items():
            if attr in attributes:
                if attr == 'timestamp':
                    ts_main = str(value).split('+')
                    ts_value = ts_main[0].replace(' ', 'T') + 'Z'
                    self.xml += "{}='{}' ".format(attr, ts_value, **_outputparams)
                elif attr == 'user':
                    self.xml += "{}='{}' ".format(attr, ts_value, **_outputparams)
                elif attr == 'geom':
                    lon = str(value[0])
                    self.xml += "{}='{}' ".format('lon', lon)
                    lat = str(value[1])
                    self.xml += "{}='{}' ".format('lat', lat)
                else:
                    self.xml += "{}='{}' ".format(attr, str(value), **_outputparams)

        if tags.count() == 0:
            self.xml += '/>'
        else:
            self.xml += '>'

        if body:
            self.xml += body

        for tag in tags:
            self.xml += tag.to_xml(_outputparams)

        if tags.count() > 0:
            self.xml += '{newline}</{primitive}>'.format(**_outputparams)

        return self.xml


class Node(OSM_Primitive):
    geom = models.PointField(geography=True, spatial_index=True, null=True)  # geography will force srid to be 4326
    objects = GeoManager()

    def set_cordinates(self, lat, lon):
        self.geom = Point(lat, lon)
        self.save()

    def to_xml(self, outputparams=None):
        attributes = ['id', 'geom', 'action', 'timestamp', 'uid', 'user', 'visible', 'version', 'changeset']

        return super().base_to_xml(primitive='node', attributes=attributes)


class Way(OSM_Primitive):
    nodes = models.ManyToManyField('Node', through='WN', related_name="nodes_in_way")
    geom = models.LineStringField(blank=True, null=True)

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

            max_sequence_num = max(sequence_list) + 1

            wn = WN.objects.create(node=node, way=self, sequence=max_sequence_num)
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

    def to_xml(self, outputparams=None, body=''):
        if outputparams is None:
            _outputparams = {'newline': '\n', 'indent': '  '}
        else:
            _outputparams = outputparams

        attributes = ['id', 'action', 'timestamp', 'uid', 'user', 'visible', 'version', 'changeset']
        for node in self.nodes.all():
            body += "{newline}{indent}<nd ref='{node_id}' />".format(node_id=node.id, **_outputparams)
        return super().base_to_xml(body=body, attributes=attributes, primitive='way')


class WN(models.Model):
    node = models.ForeignKey('Node', on_delete=models.CASCADE)
    way = models.ForeignKey('Way', on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField()

    class Meta:
        unique_together = ("node", "way", "sequence")

    def to_xml(self, outputparams):
        return "{newline}{indent}<member type='{primtype}' ref='{ref}' />".format(
            primtype='node', ref=self.node.id, **outputparams)


class MemberRelation(models.Model):
    parent = models.ForeignKey('OSM_Relation', on_delete=models.CASCADE)
    member_node = models.ForeignKey('Node', on_delete=models.CASCADE, blank=True, null=True)
    member_way = models.ForeignKey('Way', on_delete=models.CASCADE, blank=True, null=True)
    member_relation = models.ForeignKey('OSM_Relation', on_delete=models.CASCADE, blank=True,
                                        related_name="%(class)s_member_relations_rel", null=True)

    NODE = 'n'
    WAY = 'w'
    RELATION = 'r'
    TYPES = (
        (NODE, 'node'),
        (WAY, 'way'),
        (RELATION, 'relation')
    )

    type = models.CharField(max_length=1, choices=TYPES, blank=True)
    role = models.TextField(blank=True)
    sequence = models.PositiveIntegerField(blank=True)


class OSM_Relation(OSM_Primitive):
    member_nodes_rel = models.ManyToManyField('Node', through='MemberRelation',
                                              through_fields=('parent', 'member_node'))
    member_ways_rel = models.ManyToManyField('Way', through='MemberRelation', through_fields=('parent', 'member_way'))
    member_relations_rel = models.ManyToManyField('OSM_Relation', through='MemberRelation',
                                                  through_fields=('parent', 'member_relation'))

    def add_member(self, member, memtype, role):
        count = self.memberrelation_set.count()
        rm = None

        if count == 0:
            if memtype == 'node':
                rm = MemberRelation(parent=self, member_node=member, type='n', role=role, sequence=1)
            elif memtype == 'way':
                rm = MemberRelation(parent=self, member_way=member, type='w', role=role, sequence=1)
            elif memtype == 'relation':
                rm = MemberRelation(parent=self, member_relation=member, type='r', role=role, sequence=1)

        elif count > 0:
            mem_sequences = self.memberrelation_set.all()
            sequence_list = []
            sequence = 0

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

    def to_xml(self, outputparams=None, stops=[], body='', counter_arr=[]):

        if outputparams is None:
            _outputparams = {'newline': '\n'}
        else:
            _outputparams = outputparams
        attributes = ['id', 'action', 'timestamp', 'uid', 'user', 'visible', 'version', 'changeset']
        modify = False
        new_nodes = []

        if len(stops) > 0:
            modify = True
            stops_in_osm = []
            for member in self.memberrelation_set.filter(type='n'):
                node = Node.objects.get(id=member.member_node.id)
                node_tags = node.tags
                mem_role = member.role

                for tag in node_tags.all():
                    if tag.key.value == 'name':
                        data = {'node_id': node.id, 'node_name': xmlsafe(tag.value.value), 'mem_role': mem_role}
                    else:
                        data = {'node_id': node.id, 'mem_role': mem_role}

                stops_in_osm.append(data)

            for i in range(0, len(stops)):
                if i < len(stops_in_osm):
                    for key, value in stops_in_osm[i].items():
                        if key == 'node_name':
                            if fuzz.ratio(stops[i][0], xmlsafe(stops_in_osm[i]['node_name'])) >= 50:
                                role = stops_in_osm[i]['mem_role']
                                node_id = stops_in_osm[i]['node_id']
                                body += "{newline}{indent}<member type='{primtype}' ref='{ref}' role='{role}' />".format(
                                    primtype='node', ref=node_id, role=role, **outputparams)
                            else:
                                print('Fuzz of {} {} {}'.format(stops[i][0],stops_in_osm[i]['node_name'], fuzz.ratio(stops[i][0], xmlsafe(stops_in_osm[i]['node_name']))))

                                neg_number = counter_arr[len(counter_arr) - 1] - 1
                                counter_arr.append(neg_number)
                                node_id = str(neg_number)

                                new_ar = [stops[i][0], stops[i][1], stops[i][2], node_id]
                                new_nodes.append(new_ar)

                                stops_in_osm.insert(i, {'node_id': str(neg_number), 'mem_role': 'paltform',
                                                        'node_name': stops[i][0]})

                                role = 'platform'
                                body += "{newline}{indent}<member type='{primtype}' ref='{ref}' role='{role}' />".format(
                                    primtype='node', ref=node_id, role=role, **outputparams)
                else:

                    neg_number = counter_arr[len(counter_arr) - 1] - 1
                    counter_arr.append(neg_number)

                    stops_in_osm.insert(i, {'node_id': '-1', 'mem_role': ''})
                    node_id = str(neg_number)
                    new_ar = [stops[i][0], stops[i][1], stops[i][2], node_id]
                    new_nodes.append(new_ar)
                    role = 'platform'
                    body += "{newline}{indent}<member type='{primtype}' ref='{ref}' role='{role}' />".format(
                        primtype='node', ref=node_id, role=role, **outputparams)

        elif len(stops) == 0:
            for member_node in self.memberrelation_set.filter(type='n'):
                mem_role = member_node.role
                mem_type = 'node'
                mem_id = member_node.member_node.id
                body += "{newline}{indent}<member type='{primtype}' ref='{ref}' role='{role}' />".format(
                    primtype=mem_type, ref=mem_id, role=mem_role, **outputparams)

        for member_way in self.memberrelation_set.filter(type='w'):
            mem_role = member_way.role
            mem_type = 'way'
            mem_id = member_way.member_way.id
            body += "{newline}{indent}<member type='{primtype}' ref='{ref}' role='{role}' />".format(
                primtype=mem_type, ref=mem_id, role=mem_role, **outputparams)

        for member_relation in self.memberrelation_set.filter(type='r'):
            mem_role = member_relation.role
            mem_type = 'relation'
            mem_id = member_relation.member_relation.id
            body += "{newline}{indent}<member type='{primtype}' ref='{ref}' role='{role}' />".format(
                primtype=mem_type, ref=mem_id, role=mem_role, **outputparams)

        xml = super().base_to_xml(outputparams=_outputparams, attributes=attributes, body=body, primitive='relation',
                                  modify=modify)

        node_xml = ''
        if len(new_nodes) > 0:
            for new_node in new_nodes:
                new_node_name = new_node[0]
                new_node_lon = str(new_node[1])
                new_node_lat = str(new_node[2])
                new_node_id = str(new_node[3])
                node_xml += "{newline}<node id='{nodeid}' action='modify' lat='{nodelat}' lon='{nodelon}' version='1' >{newline}{indent}<tag k='bus' v='yes'/>{newline}{indent}<tag k='name' v='{nodename}' />{newline}{indent}<tag k='highway' v='bus_stop' />{newline}</node>".format(
                    newline=_outputparams['newline'], indent=_outputparams['indent'], nodelat=new_node_lat,
                    nodelon=new_node_lon, nodename=new_node_name, nodeid=new_node_id)

        xml += node_xml

        return xml, counter_arr
