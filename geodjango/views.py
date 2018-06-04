from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework import generics
from gs.models import GTFSForm
from .serializers import FormSerializer


def main(request):
    return render(request, 'gtfstoosmtool/base.html')


class FormView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = FormSerializer

    def get_queryset(self):
        return GTFSForm.objects.all()
