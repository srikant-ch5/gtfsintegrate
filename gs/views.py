from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import ListView
from multigtfs.models import Feed

from .forms import GTFSInfoForm
from .models import GTFSForm
from .tasks import download_feed_task, reset_feed


def feed_form(request):
    form_entries = GTFSForm.objects.all()
    forms_list = []

    for form_entry in form_entries:
        forms_list.append(form_entry.id)

    context = {
        'feed_downloaded_status': '',
        'feed_id': -1,
        'forms_list': forms_list,
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
                context['error'] = reset_feed(formId)
                context['feed_id'] = form_entry.feed.id
                request.session['feed'] = Feed.objects.get(id=form_entry.feed.id).name
            except Exception as e:
                context['error'] = e
        else:
            if form.is_valid():
                try:
                    gtfs_feed_info = form.save(commit=False)
                    gtfs_feed_info.save()

                    context['error'] = download_feed_task(gtfs_feed_info.id)
                    if(context['error'].find("(failed)")) >= 0:
                        gform = GTFSForm.objects.get(id=gtfs_feed_info.id)
                        request.session['feed'] = gform.feed.name
                        context['feed_id'] = gform.feed.id
                except Exception as e:
                    GTFSForm.objects.all()[3].delete()
                    Feed.objects.all()[3].delete()
                    context['error'] = e

        return render(request, 'gs/load.html', {'form': form, 'context': context})
    else:
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
    request.session['feed'] = feed
    context = {
        'data': 'data',
    }
    context['feed_id'] = pk
    return render(request, 'gs/load.html', {'context': context})


class FeedListView(ListView):
    model = Feed
    template_name = 'gs/feeds.html'

    def get_queryset(self):
        return Feed.objects.all().order_by('id').reverse()
