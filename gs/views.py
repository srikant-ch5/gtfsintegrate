from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import ListView
from django.utils import timezone

from multigtfs.models import Feed
from .forms import GTFSInfoForm, CorrespondenceForm
from .models import GTFSForm
from .tasks import download_feed_task, reset_feed, get_keys
from osmapp.views import get_osm_data

from osmapp.models import KeyValueString, Tag, Node
import json


def feed_form(request):
    form_entries = GTFSForm.objects.all()
    forms_list = []

    for form_entry in form_entries:
        forms_list.append(form_entry.id)

    context = {
        'feed_id': -1,
        'forms_list': forms_list,
    }

    form = GTFSInfoForm()
    return render(request, 'gs/form.html', {'form': form, 'context': context})


def home(request):
    context = {
        'feed': 'Please enter some feed',
        'message': 'Message to be shown ',
    }

    try:
        context['feed'] = request.session['feed']
        context['feed_id'] = Feed.objects.get(name=context['feed']).id
        print(context['feed_id'])
        print(request.session['feed'])
    except Exception as e:
        request.session['feed'] = "No Feed"
        print("The session cannot feed be because user have not entered any feed")

    '''Get all the feeds ids and pass to home page'''
    feeds = Feed.objects.all()
    feeds_list = []

    for feed in reversed(feeds):
        feeds_list.append(feed.name)

    context['feeds'] = feeds_list

    '''First get all the valid form entry ids so that iteration is easy'''
    form_entries = GTFSForm.objects.all()
    forms_list = []

    for form_entry in form_entries:
        forms_list.append(form_entry.id)

    context['form_array'] = forms_list
    return render(request, 'gs/option.html', {'context': context})


def showmap(request, pk=None):
    feed = Feed.objects.get(id=pk).name
    print(pk)
    request.session['feed'] = feed
    context = {'data': 'data', 'type': 'normal_view', 'feed_name': feed, 'feed_id': pk}

    return render(request, 'gs/load.html', {'context': context})


class FeedListView(ListView):
    model = Feed
    template_name = 'gs/feeds.html'

    def get_queryset(self):
        return Feed.objects.all().order_by('id').reverse()


def correspondence_view(request):
    context = {
        'feed_downloaded_status': '',
        'feed_id': -1,
        'error': 'No Error',
    }

    if request.method == 'POST':
        form = GTFSInfoForm(request.POST)
        # check if the url is already since the timestamp changes for every entry django creates a gtfs form
        is_feed_present = GTFSForm.objects.filter(url=request.POST['url'], osm_tag=request.POST['osm_tag'],
                                                  gtfs_tag=request.POST['gtfs_tag'])

        if is_feed_present.count() > 0:
            try:
                print('Feed already exists with name trying to renew the feed in DB')
                context['feed_download_status'] = 'Feed already exists'
                form_entry = GTFSForm.objects.get(url=request.POST['url'], osm_tag=request.POST['osm_tag'],
                                                  gtfs_tag=request.POST['gtfs_tag'])
                formId = is_feed_present[0].id
                associated_feed_id = Feed.objects.get(name=is_feed_present[0].name).name
                context['error'], context['form_reset_'] = reset_feed(formId, associated_feed_id)
                feed_id = Feed.objects.get(name=form_entry.name).id
                context['feed_id'] = feed_id
                feed_name = Feed.objects.get(name=form_entry.name).name
                request.session['feed'] = feed_name
                context['feed_name'] = feed_name
                get_osm_data(feed_id)
                context['key_strings'] = get_keys(feed_id)

            except Exception as e:
                context['error'] = e
        else:
            if form.is_valid():

                gtfs_feed_info = form.save(commit=False)
                print('Feed Id {}'.format(gtfs_feed_info.url))
                gtfs_feed_info.save()

                context['error'] = download_feed_task(gtfs_feed_info.id)
                if (context['error'].find("(failed)")) < 0:
                    gform = GTFSForm.objects.get(id=gtfs_feed_info.id)
                    feed = Feed.objects.get(name=gform.name)
                    request.session['feed'] = feed.name
                    feed_id = feed.id
                    context['feed_id'] = feed_id
                    context['feed_name'] = feed.name
                    get_osm_data(feed_id)
                    context['key_strings'] = get_keys(feed_id)

                context['error'] = e

        corr_form = CorrespondenceForm()

        return render(request, 'gs/correspondence.html', {'form': corr_form, 'context': context})
    else:
        form = CorrespondenceForm()
        return render(request, 'gs/correspondence.html', {'form': form})


def correspondence_view(request):
    context = {
        'feed_downloaded_status': '',
        'feed_id': -1,
        'error': 'No Error',
    }

    if request.method == 'POST':
        form = GTFSInfoForm(request.POST)

        is_feed_present = GTFSForm.objects.filter(url=request.POST['url'], osm_tag=request.POST['osm_tag'],
                                                  gtfs_tag=request.POST['gtfs_tag'])

        if is_feed_present.exists():
            print('Feed already exists with name trying to renew the feed in DB')
            context['feed_download_status'] = 'Feed already exists'
            form_entry = GTFSForm.objects.get(url=request.POST['url'], osm_tag=request.POST['osm_tag'],
                                              gtfs_tag=request.POST['gtfs_tag'])
            associated_feed_id = form_entry.feed_id
            formId = form_entry.id
            context['error'], context['form_reset_'] = reset_feed(formId, associated_feed_id)

            feed_name = Feed.objects.get(id=associated_feed_id).name

            context['feed_id'] = associated_feed_id
            context['feed_name'] = feed_name

            get_osm_data(associated_feed_id)
            context['key_strings'] = get_keys(associated_feed_id)
        else:
            if form.is_valid():
                gtfs_feed_info = form.save()

                gtfs_form_obj = GTFSForm.objects.get(url=request.POST['url'], osm_tag=request.POST['osm_tag'],
                                                     gtfs_tag=request.POST['gtfs_tag'])

                print("Feed ID at creation {}".format(gtfs_form_obj.id))

                context['error'], feed_id = download_feed_task(gtfs_form_obj.id)
                feed_obj = Feed.objects.get(id=feed_id)
                gtfs_form_obj.name = feed_obj.name
                gtfs_form_obj.feed_id = feed_id
                gtfs_form_obj.timestamp = timezone.now()
                gtfs_form_obj.save()

                feed_obj = Feed.objects.get(id=feed_id)
                context['feed_id'] = feed_id
                context['feed_name'] = feed_obj.name

                get_osm_data(feed_id)
                context['key_strings'] = get_keys(feed_id)

        corr_form = CorrespondenceForm()

        return render(request, 'gs/correspondence.html', {'form': corr_form, 'context': context})

    else:
        form = CorrespondenceForm()
        return render(request, 'gs/correspondence.html', {'form': form})
