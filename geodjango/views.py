from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework import generics
from gs.models import GTFSForm
from multigtfs.models import Stop, Feed, Agency, Route
from osmapp.models import Node, Way, KeyValueString, OSM_Relation, Tag
from .serializers import FormSerializer, StopSerializer, NodeSerializer, WaySerializer, \
    TagSerializer, KeyValueStringSerializer, RelationSerializer, FeedSerializer, AgencySerializer, \
    RouteSerializer

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


def main(request):
    return render(request, 'gtfstoosmtool/base.html')


'''Gs app models'''


class FormView(APIView):
    def get(self, request):
        forms = GTFSForm.objects.all()
        serializer = FormSerializer(forms, many=True)
        return Response(serializer.data)


'''OSM app models'''


class NodeView(APIView):
    def get(self, request):
        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)


class WayView(APIView):
    def get(self, request):
        ways = Way.objects.all()
        serializer = WaySerializer(ways, many=True)
        return Response(serializer.data)


class RelationView(APIView):
    def get(self, request):
        relations = OSM_Relation.objects.all()
        serializer = RelationSerializer(relations, many=True)
        return Response(serializer.data)


class TagView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class KeyValueStringView(APIView):
    def get(self, request):
        kvs = KeyValueString.objects.all()
        serializer = KeyValueStringSerializer(kvs, many=True)
        return Response(serializer.data)


'''GTFS Models'''


class StopView(APIView):
    def get(self, request):
        stops = Stop.objects.all()
        serializer = StopSerializer(stops, many=True)
        return Response(serializer.data)


class FeedView(APIView):
    def get(self, request):
        feeds = Feed.objects.all()
        serializer = FeedSerializer(feeds, many=True)
        return Response(serializer.data)


class AgencyView(APIView):
    def get(self, request):
        agencies = Agency.objects.all()
        serializer = AgencySerializer(agencies, many=True)
        return Response(serializer.data)


class RouteView(APIView):
    def get(self, request):
        route = Route.objects.all()
        serializer = RouteSerializer(route, many=True)
        return Response(serializer.data)
