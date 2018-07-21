from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework import generics
from gs.models import GTFSForm
from multigtfs.models import Stop, Feed, Agency, Route
from osmapp.models import Node, Way, KeyValueString, OSM_Relation, Tag, Bounds
from .serializers import FormSerializer, StopSerializer, NodeSerializer, WaySerializer, \
    TagSerializer, KeyValueStringSerializer, RelationSerializer, FeedSerializer, AgencySerializer, \
    RouteSerializer, FeedBoundsSerializer, CorrespondenceSerializer, ConversionSerializer, ExtraFieldSerializer, LineStopSerializer
from conversionapp.models import Correspondence, Conversion, ExtraField, Correspondence_Route
from compare.models import Line_Stop
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

    def post(self, request):
        serializer = FormSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''OSM app models'''


class NodeView(APIView):
    def get(self, request):
        nodes = Node.objects.all()
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NodeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WayView(APIView):
    def get(self, request):
        ways = Way.objects.all()
        serializer = WaySerializer(ways, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WaySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RelationView(APIView):
    def get(self, request):
        relations = OSM_Relation.objects.all()
        serializer = RelationSerializer(relations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RelationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TagSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KeyValueStringView(APIView):
    def get(self, request):
        kvs = KeyValueString.objects.all()
        serializer = KeyValueStringSerializer(kvs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = KeyValueStringSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''GTFS Models'''


class StopView(APIView):
    def get(self, request):
        stops = Stop.objects.all()
        serializer = StopSerializer(stops, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StopSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedView(APIView):
    def get(self, request):
        feeds = Feed.objects.all()
        serializer = FeedSerializer(feeds, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FeedSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgencyView(APIView):
    def get(self, request):
        agencies = Agency.objects.all()
        serializer = AgencySerializer(agencies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AgencySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteView(APIView):
    def get(self, request):
        route = Route.objects.all()
        serializer = RouteSerializer(route, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RouteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedBoundsView(APIView):
    def get(self, request):
        feedbound = Bounds.objects.all()
        serializer = FeedBoundsSerializer(feedbound, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FeedBoundsSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CorrespondenceView(APIView):
    def get(self, request):
        feedbound = Correspondence.objects.all()
        serializer = CorrespondenceSerializer(feedbound, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CorrespondenceSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversionView(APIView):
    def get(self, request):
        feedbound = Conversion.objects.all()
        serializer = ConversionSerializer(feedbound, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConversionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LineStopView(APIView):
    def get(self, request):
        linestop = Line_Stop.objects.all()
        serializer = LineStopSerializer(linestop, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LineStopSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExtraFieldView(APIView):
    def get(self, request):
        extrafield = ExtraField.objects.all()
        serializer = ExtraFieldSerializer(extrafield, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExtraFieldSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LineStopView(APIView):
    def get(self, request):
        linestop = Line_Stop.objects.all()
        serializer = LineStopSerializer(linestop, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LineStopSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)