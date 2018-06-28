from django.shortcuts import render
from gs.forms import CorrespondenceForm
from .models import Conversion
from multigtfs.models import Stop
import re


def save_correspondence(request):
    if request.method == 'POST':

        form = CorrespondenceForm(request.POST)
        feed_id = -1
        if form.is_valid():
            corr_form = form.save(commit=False)
            feed_id = corr_form.feed_id

        context = {
            'feed_id': feed_id
        }

        return render(request, 'gs/correspondence.html', {'context': context})


def conversionview(request):
    if request.method == 'POST':
        present = request.POST.getlist('present_str[]')
        replace = request.POST.getlist('replace_str[]')
        context = {
            'saved_status': 'Conversions are saved1'
        }
        present_strings = list(filter(None, present))
        replace_strings = list(filter(None, replace))
        print(present_strings)
        print(replace_strings)
        from_string = ['St.', 'Rd.', 'St', 'Rd']
        to_string = ['Street', 'Road', 'Street', 'Road']

        corr_form_id = request.POST.get('corr_form_id')
        feed_id = int(request.POST.get('feed_id'))
        stops = Stop.objects.filter(feed=feed_id)
        print("converting stop names")

        for i in range(0, len(stops)):
            stop_name = stops[i].name

            for j in range(0, len(from_string)):
                if re.search(from_string[j], stop_name):
                    print('Replacing {}'.format(stop_name))
                    stops[i].normalized_name = stop_name.replace(from_string[j], to_string[j])
                    stops[i].save()

            for k in range(0, len(present_strings)):
                if re.search(present_strings[k], stop_name):
                    print("Replacing {}".format(stop_name))
                    stops[i].normalized_name = stop_name.replace(present_strings[k], replace_strings[k])
                    stops[i].save()
    return render(request, 'gs/correspondence.html', {'context': context})


def make_conversion(request):
    return render(request, 'gs/conversion.html')
