import re

from django.shortcuts import render

from gs.forms import CorrespondenceForm
from multigtfs.models import Stop
from .models import Correspondence


def save_correspondence(request):
    if request.method == 'POST':

        form = CorrespondenceForm(request.POST)
        feed_id = -1
        if form.is_valid():
            entered_corr_form = form.save(commit=False)
            form_feed_id = entered_corr_form.feed_id

            if Correspondence.objects.filter(feed_id=entered_corr_form.feed_id).exists():
                corr_form = Correspondence.objects.get(feed_id=entered_corr_form.feed_id)
                form_feed_id = entered_corr_form.feed_id
                corr_form.stop_id = entered_corr_form.stop_id
                corr_form.stop_code = entered_corr_form.stop_code
                corr_form.stop_name = entered_corr_form.stop_name
                corr_form.stop_desc = entered_corr_form.stop_desc
                corr_form.stop_zone = entered_corr_form.stop_zone
                corr_form.stop_url = entered_corr_form.stop_url
                corr_form.stop_location_type = entered_corr_form.stop_location_type
                corr_form.stop_parent_station = entered_corr_form.stop_parent_station
                corr_form.stop_timezone = entered_corr_form.stop_timezone
                corr_form.save()

            else:
                entered_corr_form.save()

    # get stop names with . in it an display it in conversion view
    stops_of_feed = Stop.objects.filter(feed=form_feed_id)
    print(stops_of_feed)
    stops_with_abbr = []
    for stop in stops_of_feed:
        if re.search('\.', stop.name):
            stops_with_abbr.append(stop.name)

    context = {
        'feed_id': form_feed_id,
        'stops_for_conversion': stops_with_abbr
    }

    return render(request, 'gs/conversion.html', {'context': context})


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

        conversion_dict = {
            ' Street ': [' St. ', ' St ', ' St.'],
            ' Street': ['\sSt$', '\sSt.$'],
            ' Road ': [' Rd. ', ' Rd ', ' Rd.'],
            ' Road': [' [Rd]$', ' [Rd.]$'],
            ' Opposite ': ['\sOpp.\s', '\sOpp\s'],
            'Opposite ': ['Opp.\s', 'Opp\s']
        }

        corr_form_id = request.POST.get('corr_form_id')
        feed_id = int(request.POST.get('feed_id'))
        stops = Stop.objects.filter(feed=feed_id)
        print("converting stop names")

        for i in range(0, len(stops)):
            stop_name = stops[i].name
            normalizedName = str(stop_name).replace('&','&amp;').replace("'","&apos;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

            for key, value in conversion_dict.items():
                for v in value:
                    if re.search(v, normalizedName):
                        print('Replacing {} with {}'.format(stop_name, normalizedName))
                        normalizedName = normalizedName.replace(v, key)

            for k in range(0, len(present_strings)):
                if re.search(present_strings[k], normalizedName):
                    print("Replacing {} again".format(stop_name))
                    normalizedName = normalizedName.replace(present_strings[k], replace_strings[k])

            stops[i].normalized_name = normalizedName
            stops[i].save()

    return render(request, 'gs/conversion.html', {'context': context})


def make_conversion(request):
    return render(request, 'gs/conversion.html')
