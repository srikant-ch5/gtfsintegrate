import re
from urllib.parse import urlencode
from osmapp.models import Node, Way, OSM_Relation, Tag, KeyValueString


def xmlsafe(name):
    return str(name).replace('&', '&amp;').replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;").replace('"',
                                                                                                                    "&quot;")


def urlsafe(name):
    return xmlsafe(name).replace(' ', '%20')


class MapLayer():
    def __init__(self):
        self.nodes = []
        self.ways = []
        self.relations = {}

    def to_xml(self, output='doc', upload=False, generator='Python script'):
        """
            :type output: string doc for formatted file output, url for concise output
            :type generator: string documentation to be added to OSM xml file for tool that generated the XML data
        """
        outputparams = {}
        if output == 'url':
            outputparams['newline'] = ''
            outputparams['indent'] = ''
        else:
            outputparams['newline'] = '\n'
            outputparams['ident'] = '  '

        if upload is False:
            outputparams["upload"] = " upload='false'"
        else:
            output['upload'] = ""

        if generator:
            outputparams["generator"] = " generator='{}'".format(generator)
        else:
            outputparams["generator"] = ""

        xml = '''<?xml version='1.0' encoding='UTF-8'?>{newline}<osm version='0.6'{upload}{generator}>{newline}'''.format(
            **outputparams)

        for n in self.nodes:
            node = Node.objects.get(id=n)
            xml += node.to_xml(outputparams=outputparams)
        for w in self.ways:
            way = Way.objects.get(id=w)
            xml += way.to_xml(outputparams=outputparams)
        for rel_id,stop_names in self.relations.items():
            relation = OSM_Relation.objects.get(id=rel_id)
            xml += relation.to_xml(outputparams=outputparams, stops=stop_names)

        xml += '''{newline}</osm>'''.format(**outputparams)
        return xml

    def to_url(self, upload=False, generator='Python script', new_layer=True, layer_name=''):
        """
            :type output: string doc for formatted file output, url for concise output
            :type generator: string documentation to be added to OSM xml file for tool that generated the XML data
            :type new_layer: bool set to False to add data to currently open layer in JOSM
            :type layer_name: string name for the layer to be created if new_layer=True
        """

        values = {'data': self.to_xml(output='url', upload=upload, generator=generator)}

        if new_layer is False:
            values['new_layer'] = 'false'
        else:
            values['new_layer'] = 'true'

        if layer_name:
            values['layer_name'] = layer_name

        return "http://localhost:8111/load_data?" + urlencode(values)

    def to_link(self, upload=False, generator='Python script', new_layer=True, layer_name='', linktext=''):
        """
        :type output: string doc for formatted file output, url for concise output
        :type generator: string documentation to be added to OSM xml file for tool that generated the XML data
        :type new_layer: bool set to False to add data to currently open layer in JOSM
        :type layer_name: string name for the layer to be created if new_layer=True
        :type linktext: string text to show on the link
        """
        params = {'linktext': linktext,
                  'url': self.to_url(upload=upload,
                                     generator=generator,
                                     new_layer=new_layer,
                                     layer_name=layer_name)
                  }
        print(params)

        return '<a href="{url}">{linktext}</a>'.format(**params)
