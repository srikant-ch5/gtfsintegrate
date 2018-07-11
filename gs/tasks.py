from __future__ import unicode_literals

import os
import numpy as np
import requests
from django.utils import timezone
from multigtfs.models import Feed, Stop

from compare.models import CMP_Stop
from osmapp.models import Node, Tag, KeyValueString
from .models import GTFSForm
from django.db import connection
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import pdb
import operator

topleft_block_stops = []
topright_block_stops = []
bottomleft_block_stops = []
bottomright_block_stops = []


def save_comp(gtfs_stop, osm_stop, feed_id, stops_layer):
    context = {
        'match_success': 0,
        'error': ''
    }

    name_field = gtfs_stop['name_field']
    ref_field = gtfs_stop['ref_field']
    print('{} {}'.format(name_field, ref_field))
    xml = ''
    if name_field == 'normalized_name' and ref_field == 'stop_id':
        gtfs_feed_id = int(feed_id)
        gtfs_stop_id = gtfs_stop['ref_stop_id']

        osm_stop_id = osm_stop['node_id']
        osm_stop_name = osm_stop['comp_name']
        osm_stop_ref = osm_stop['ref']

        print('matching gtfs stop {0} with {1}'.format(gtfs_stop_id, osm_stop_id))
        try:
            gtfs_stop_obj = Stop.objects.get(feed=gtfs_feed_id, stop_id=gtfs_stop_id)
            print(gtfs_stop_obj)
            cmp_stop_obj = CMP_Stop.objects.get(gtfs_stop=gtfs_stop_obj)
            print(cmp_stop_obj)
            context['match_success'] = 1
        except Exception as e:
            print(e)
            context['match_success'] = 0
            context['error'] += 'gtfs stop doesnt exist or is undefined'

        try:
            osm_stop_obj = Node.objects.get(id=osm_stop_id, feed=gtfs_feed_id)
            context['match_success'] = 1
        except Exception as e:
            print(e)
            context['match_success'] = 0
            context['error'] += 'osm stop doesnt exist {}'.format(e)

        try:
            if cmp_stop_obj.fixed_match == None:
                print("Creating new match ")

                cmp_stop_obj.fixed_match = osm_stop_obj
                cmp_stop_obj.save()
            else:
                cmp_stop_obj.fixed_match = None
                cmp_stop_obj.save()
                cmp_stop_obj.fixed_match = osm_stop_obj
                cmp_stop_obj.save()

            print("Match made")
        except Exception as e:
            print("relation already exists")

        print("Creating tags in node")

        # get tags data
        # if the osm_name is not already then json will not include that as its undefined
        osm_name_defined = False

        try:
            osm_name = osm_stop['osm_name']
            osm_name_defined = True
        except Exception as e:
            osm_name_defined = False

        if osm_name_defined:
            osm_stop_name = osm_stop['osm_name']
        else:
            osm_stop_name = osm_stop['comp_name']

        # get all tags of node
        node_tags = osm_stop_obj.tags.all()

        name_tag_in_node = False
        ref_tag_in_node = False
        for node_tag in node_tags:
            if node_tag.value == 'name':
                name_tag_in_node = True
            elif node_tag.value == 'ref':
                ref_tag_in_node = True

        # create KeyValueString for name and ref if the data in osm table dosent have them

        if not name_tag_in_node:
            tag = Tag()
            name_tag = tag.add_tag('name', osm_stop_name)
            osm_stop_obj.tags.add(name_tag)

        if not ref_tag_in_node:
            tag = Tag()
            ref_tag = tag.add_tag('ref', osm_stop_ref)
            osm_stop_obj.tags.add(ref_tag)

        xml = cmp_stop_obj.to_xml('yes')

    return xml


def connect_to_JOSM(xml):
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    xmlfiledir = os.path.join(os.path.dirname(PROJECT_ROOT), 'osmapp', 'static')
    xmlfile = xmlfiledir + '/nodesosm/singlenode.osm'

    context = {
        'data': 'data'
    }
    with open(xmlfile, 'w') as fh:
        fh.write(xml)

    print("Opening the node  in josm")
    try:
        resp = requests.get(
            'http://127.0.0.1:8111/open_file?filename=/home/srikant/testwork/env/gtfsapp/gtfsintegrate/osmapp/static/nodesosm/singlenode.osm')
    except requests.exceptions.RequestException as e:
        context['error'] += 'JOSM not open {}'.format(e)


def get_keys(feed_id):
    key_strings = []
    tags = Node.objects.filter(feed=feed_id).values('tags').distinct()
    for tag in tags:
        key = Tag.objects.get(id=tag['tags']).key.value
        if not key in key_strings:
            key_strings.append(key)

    return key_strings


def getmidpoint(lat1, lon1, lat2, lon2):
    l = Geodesic.WGS84.InverseLine(lat1, lon1, lat2, lon2)

    m = l.Position(0.5 * l.s13)

    return m['lat2'], m['lon2']


def plotblock(v0, v1, v2, v3, stops_coordinates, block=None):
    lats_vect = np.array([v0[0], v1[0], v2[0], v3[0]])
    lons_vect = np.array([v0[1], v1[1], v2[1], v3[1]])

    lats_lon_vect = np.column_stack((lats_vect, lons_vect))
    polygon = Polygon(lats_lon_vect)

    points_in_bound = []
    points_not_in_bound = []

    for i in range(0, len(stops_coordinates)):
        x, y = stops_coordinates[i][0], stops_coordinates[i][1]
        point = Point(x, y)
        p = [x, y]
        if polygon.contains(point):
            block.append(point)
        else:
            points_not_in_bound.append(point)

    # print(len(points_not_in_bound))#includes points ne,nw,se,sw

    '''
    Display bound and a stop using matlpotlib
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()

    # Append first vertex to end of vector to close polygon when plotting
    lats_vect = np.append(lats_vect, lats_vect[0])
    lons_vect = np.append(lons_vect, lons_vect[0])
    plt.plot([lons_vect[0:-1], lons_vect[1:]], [lats_vect[0:-1], lats_vect[1:]],
             color='black', linewidth=1,
             transform=ccrs.Geodetic(),
             )

    plt.plot(-72.343421936, 43.729133606,
             '*',
             color='blue',
             markersize=8)

    plt.show()
    
    '''

    return block


def queries():
    query = ''


def dividemap(east=None, west=None, north=None, south=None, northeast_lat=None, northeast_lon=None, northwest_lat=None,
              northwest_lon=None, southeast_lat=None,
              southeast_lon=None, southwest_lat=None, southwest_lon=None, stops_coordinates=None):
    '''
    testing to get 1/4th of the bbbox using AdvanceTransit bounds

    northeast_lat = 43.729133606
    northeast_lon = -72.0132064819
    northwest_lat = 43.729133606
    northwest_lon = -72.343421936
    southeast_lat = 43.6245117188
    southeast_lon = - 72.0132064819
    southwest_lat = 43.6245117188
    southwest_lon = - 72.343421936
    '''

    northeast_lat = float(northeast_lat)
    northeast_lon = float(northeast_lon)
    northwest_lat = float(northwest_lat)
    northwest_lon = float(northwest_lon)
    southeast_lat = float(southeast_lat)
    southeast_lon = float(southeast_lon)
    southwest_lat = float(southwest_lat)
    southwest_lon = float(southwest_lon)

    print(' {} {} {} {} {} {} {} {}'.format(northeast_lat, northeast_lon, northwest_lat, northwest_lon, southeast_lat,
                                            southeast_lon, southwest_lat, southwest_lon))

    # points = plotblock(v0, v1, v2, v3, stops_coordinates)

    query = "SELECT ST_AsText(ST_Centroid(ST_Collect(geom))) FROM (VALUES "

    for i in range(0, len(stops_coordinates)):
        x, y = stops_coordinates[i][0], stops_coordinates[i][1]
        point = "('POINT (" + str(x) + " " + str(y) + ")'),"
        point = str(point)
        query += point

    query = query.rstrip(",")
    final_query = query + ") sq (geom);"

    cursor = connection.cursor()
    cursor.execute(final_query)
    result = cursor.fetchall()
    print(result)

    '''

    west = [0, 0]
    west[0], west[1] = getmidpoint(northwest_lat, northwest_lon, southwest_lat, southwest_lon)
    east = [0, 0]
    east[0], east[1] = getmidpoint(northeast_lat, northeast_lon, southeast_lat, southeast_lon)
    north = [0, 0]
    north[0], north[1] = getmidpoint(northeast_lat, northeast_lon, northwest_lat, northwest_lon)
    south = [0, 0]
    south[0], south[1] = getmidpoint(southwest_lat, southwest_lon, southeast_lat, southeast_lon)

    center = [0, 0]
    center[0], center[1] = getmidpoint(north[0], north[1], south[0], south[1])


    # whole block 

    v0 = [northwest_lat, northwest_lon]
    v1 = [northeast_lat, northeast_lon]
    v2 = [southeast_lat, southeast_lon]
    v3 = [southwest_lat, southwest_lon]

    plotblock(v0, v1, v2, v3, stops_coordinates)

    #top-left block 
    v0 = [northwest_lat, northwest_lon]
    v1 = north
    v2 = center
    v3 = west

    block1_len = plotblock(v0, v1, v2, v3, stops_coordinates, topleft_block_stops)

    #top right block
    v0 = north
    v1 = [northeast_lat, northeast_lon]
    v2 = east
    v3 = center

    block2_len = plotblock(v0, v1, v2, v3, stops_coordinates, topright_block_stops)

    #bottom right block
    v0 = center
    v1 = east
    v2 = [southeast_lat, southeast_lon]
    v3 = south
    block3_len = plotblock(v0, v1, v2, v3, stops_coordinates, bottomright_block_stops)

    #bottom left block
    v0 = west
    v1 = center
    v2 = south
    v3 = [southwest_lat, southwest_lon]
    block4_len = plotblock(v0, v1, v2, v3, stops_coordinates, bottomleft_block_stops)

    print('block I {} II {} III {} IV {} '.format(block1_len, block2_len, block3_len, block4_len))
    total_stops = len(stops_coordinates)

    # get that one block which has the highest number of stops
    blocks = [block1_len, block2_len, block3_len, block4_len]
    populated_block, value = max(enumerate(blocks), key=operator.itemgetter(1))

    ind = {
        '0': topleft_block_stops,
        '1': topright_block_stops,
        '2': bottomright_block_stops,
        '3': bottomleft_block_stops
    }
    s = str(populated_block)
    block = ind[s]

    print(block)

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.stock_img()

    # Append first vertex to end of vector to close polygon when plotting
    lats_vect = np.append(lats_vect, lats_vect[0])
    lons_vect = np.append(lons_vect, lons_vect[0])
    plt.plot([lons_vect[0:-1], lons_vect[1:]], [lats_vect[0:-1], lats_vect[1:]],
             color='black', linewidth=1,
             transform=ccrs.Geodetic(),
             )


    for i in range(0,len(points_in_bound)):
        y,x = points_in_bound[1],points_in_bound[0]
        plt.plot(y,x,
                 '*',
                 color='blue',
                 markersize=8)

    plt.show()
    '''


def rename_feed(name, formId):
    present_name = name
    feed = Feed.objects.get(name=name)
    agencies = feed.agency_set.all()
    update_name = ''

    for agency in agencies:
        agname = agency.name.replace(" ", "")
        update_name += agname
    # remove space
    # get if the feed names already exists
    update_name += '-'
    num = 0
    while True:

        if Feed.objects.filter(name=update_name + str(num)).exists():
            num = num + 1
        else:
            break

    update_name += str(num)
    user_form = GTFSForm.objects.get(id=formId)
    user_form.name = update_name
    user_form.save()
    feed.name = update_name
    feed.save()
    to_change = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gtfsfeeds/") + name + '.zip'
    update_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gtfsfeeds/") + update_name + '.zip'
    os.rename(to_change, update_name)


def download_feed_in_db(file, file_name, code, formId):
    feeds = Feed.objects.create(name=file_name)
    successfull_download = 0  # 0 = False
    error = 'No error while downloading the file'
    print("{} in down Feed init ".format(successfull_download))
    try:
        feeds.import_gtfs(file)
        feed = Feed.objects.latest('id')
        form = GTFSForm.objects.get(id=formId)
        print(form)
        successfull_download = 1  # 1 =True
        print("{} in  Feed import ".format(successfull_download))

    except Exception as e:
        error = "File was not downloaded properly because the url or the data is not right (failed)"
        successfull_download = 0

    if code == 'not_present':
        rename_feed(file_name, formId)

    print("{} in down Feed end ".format(successfull_download))
    return successfull_download, error


def download_feed_with_url(download_url, save_feed_name, code, formId):
    print("Downloading with url")
    r = requests.get(download_url, allow_redirects=True)

    feed_file = 'gs/gtfsfeeds/' + save_feed_name + '.zip'
    # temporary name for file
    if code == 'present':
        os.remove(feed_file)
        print("renewing feed file")

    open(feed_file, 'wb').write(r.content)

    feed_download_status, error = download_feed_in_db(feed_file, save_feed_name, code, formId)

    return feed_download_status, error


def download_feed_task(formId):
    # get url osm_tag gtfs_tag of the user entered form
    user_form = GTFSForm.objects.get(id=formId)
    entered_url = user_form.url
    entered_osm_tag = user_form.osm_tag
    entered_gtfs_tag = user_form.gtfs_tag
    entered_name = user_form.name
    user_form.timestamp = timezone.now()
    user_form.save()

    feed_name = ((lambda: entered_name, lambda: entered_osm_tag)[entered_name == '']())

    code = 'not_present'
    feed_download_status, error = download_feed_with_url(entered_url, feed_name, code, formId)

    print(feed_download_status)

    if feed_download_status == 0:
        form_to_delete = GTFSForm.objects.latest('id')
        feed_to_delete = Feed.objects.latest('id')

        form_to_delete.delete()
        feed_to_delete.delete()

    return error


def check_feeds_task():
    # keep on checking the feeds for every five days all the feeds are downloaded again into the database
    # 1. get all the feeds
    all_feeds = Feed.objects.all()

    feed_form_not_found = ''
    for feed in all_feeds:
        # get the name of the feed
        feed_name = feed.name
        print(feed_name)
        try:
            feed_form = GTFSForm.objects.get(name=feed_name)
            feed_url = feed_form.url
            feed_timestamp = feed_form.timestamp
            current_timestamp = timezone.now()
            print("{}  {}".format(feed_timestamp, current_timestamp))

            ts_diff = str(current_timestamp - feed_timestamp)[0]

            print(ts_diff)
            frequency = feed_form.frequency
            if int(ts_diff) > frequency:
                feed_form_not_found = "Downloading the feed again"
                print(feed_form_not_found)
                code = 'present'
                download_feed_with_url(feed_url, feed_name, code, feed_form.id)

            feed.delete()
        except Exception as e:
            feed_form_not_found = 'Form not found with present feed'

        print(feed_form_not_found)


def reset_feed(formId, associated_feed_id):
    form = GTFSForm.objects.get(id=formId)
    form_timestamp = form.timestamp
    print(form_timestamp)
    current_timestamp = timezone.now()
    form_name = form.name

    ts_diff = str(current_timestamp - form_timestamp)[0]
    status = 'The Feed is up to date'
    print("Diff is {}".format(ts_diff))
    form_reset = False
    code = 'present'
    frequency = form.frequency
    if int(ts_diff) > frequency:
        status = 'Reseting feed with latest data'
        print('Reseting Feed')
        form_reset = True
        form.timestamp = timezone.now()
        form.save()
        Feed.objects.get(name=form_name).delete()
        download_feed_with_url(form.url, form.name, code, formId)

    '''since form has one to one relationship with every feed so when the feed is renewed form.feed should be updated'''

    return status, form_reset
