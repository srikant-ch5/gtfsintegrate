from django.shortcuts import render
from typing import List, Any

from .models import CMP_Stop
from osmapp.models import Tag, KeyValueString, Node, Way, OSM_Relation
from multigtfs.models import Stop


