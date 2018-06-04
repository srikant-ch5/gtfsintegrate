from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import ListView
from multigtfs.models import Feed

from .forms import GTFSInfoForm
from .models import GTFSForm
from .tasks import download_feed_task, reset_feed


def feed_form(request):
    if request.method == 'POST':
        form = GTFSInfoForm(request.POST)
        # check if the url is already since the timestamp changes for every entry django creates a gtfs form
        is_feed_present = GTFSForm.objects.filter(url=request.POST['url'], osm_tag=request.POST['osm_tag'],
                                                  gtfs_tag=request.POST['gtfs_tag'])

        if is_feed_present.count() > 0:
            print('Feed already exists with name trying to renew the feed in DB')
            context = 'Feed already exists'

            formId = is_feed_present[0].id
            reset_feed(formId)

        else:
            context = "Creating new feed"
            print(context)

            if form.is_valid():
                print("Going through this")
                gtfs_feed_info = form.save(commit=False)
                gtfs_feed_info.save()

                download_feed_task(gtfs_feed_info.id)

        return render(request, 'gs/load.html', {'form': form, 'context': context})
    else:
        form = GTFSInfoForm()
        return render(request, 'gs/form.html', {'form': form})


def home(request):
    return render(request, 'gs/option.html')


def map(request):
    return render(request, 'gs/map.html')


def download(request):
    if request.method == 'POST' and request.FILES['gtfsfile']:

        if (Feed.objects.filter(name=name).exists()):
            context = 'File is already present in the Database'
            print(context)
        else:
            feeds = Feed.objects.create(name=name)
            feeds.import_gtfs(gtfs_feed)
            context = name + "GTFS file is uploaded to Database"

    return render(request, 'gs/map.html', {'context': context})


class FeedListView(ListView):
    model = Feed
    template_name = 'gs/feeds.html'

    def get_queryset(self):
        return Feed.objects.all().order_by('id').reverse()
