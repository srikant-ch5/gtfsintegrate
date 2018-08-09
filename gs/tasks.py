from __future__ import unicode_literals

import os

import numpy as np
import requests
from django.db import connection
from django.utils import timezone
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from compare.models import CMP_Stop
from multigtfs.models import Feed, Stop
from osmapp.models import Node, Tag
from .models import GTFSForm
import requests
import webbrowser
from urllib.parse import urlencode

topleft_block_stops = []
topright_block_stops = []
bottomleft_block_stops = []
bottomright_block_stops = []


def check_stop_in_itineraries(all_itineraries, stop, index):
    stop_found = False
    for i in range(0, len(all_itineraries)):
        if len(all_itineraries[i]) - 1 >= index:
            if all_itineraries[i][index] == stop:
                stop_found = True
            else:
                stop_found = False

    return stop_found


def get_itineraries(route_id_db, feed_id, start):
    db_route_id = "'" + str(route_id_db) + "'"
    qfeed_id = "'" + str(feed_id) + "'"
    query = '''
            SELECT
                gtfs_stop.stop_id,
                gtfs_stop.code,
                gtfs_stop.normalized_name,
                gtfs_stop_time.stop_sequence,
                gtfs_trip.extra_data,
                gtfs_route.id,
                gtfs_route.route_id,
                gtfs_route.short_name,
                gtfs_route.long_name,
                gtfs_route.desc,
                gtfs_route.color,
                gtfs_route.extra_data,
                gtfs_stop.id
            FROM
                gtfs_route,
                gtfs_stop,
                gtfs_stop_time,
                gtfs_trip
            WHERE
                gtfs_stop.id = gtfs_stop_time.stop_id AND
                gtfs_stop_time.trip_id = gtfs_trip.id AND
                gtfs_trip.route_id = gtfs_route.id AND
                gtfs_route.id = ''' + db_route_id + ''' AND
                gtfs_route.feed_id = ''' + qfeed_id + '''
            ORDER BY
                gtfs_trip.id , gtfs_stop_time.stop_sequence;
            '''
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    data_all_itineraries = []
    i = 0
    while i < len(result):
        it = []
        if result[i][3] == 1:
            j = i + 1
            slat = Stop.objects.get(feed=feed_id, stop_id=result[i][0]).geom.x
            slon = Stop.objects.get(feed=feed_id, stop_id=result[i][0]).geom.y

            data = [result[i][3], result[i][2], slat, slon]
            it.append(data)

            while result[j][3] != 1 and j < len(result):
                slat = Stop.objects.get(feed=feed_id, stop_id=result[j][0]).geom.x
                slon = Stop.objects.get(feed=feed_id, stop_id=result[j][0]).geom.y
                dnormal_name = result[j][2].replace("'", "").replace('"', '').replace('\"', '')

                data = [result[j][3], dnormal_name, slat, slon]
                it.append(data)
                j = j + 1

                if j >= len(result):
                    break
        data_all_itineraries.append(it)
        i = j

    data_unique_itineraries = []
    for k in range(0, len(data_all_itineraries)):
        single_itinerary = data_all_itineraries[k]

        if single_itinerary not in data_unique_itineraries:
            data_unique_itineraries.append(single_itinerary)

    data_final_unique_array = data_unique_itineraries
    for data_single_itinerary in data_unique_itineraries:

        for compare_it in data_unique_itineraries:

            if data_single_itinerary in compare_it:
                data_final_unique_array.remove(data_single_itinerary)

    line = [result[0][8], result[0][5], data_final_unique_array]
    return line


def save_comp(gtfs_stop, osm_stop, feed_id, stops_layer):
    context = {
        'match_success': 0,
        'error': ''
    }

    name_field = gtfs_stop['name_field']
    ref_field = gtfs_stop['ref_field']
    print('{} {}'.format(name_field, ref_field))
    xml = ''
    # check if the supplied tags are present

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
            osm_stop_name = xmlsafe(osm_stop_obj.name)
            context['match_success'] = 1
        except Exception as e:
            print(e)
            context['match_success'] = 0
            context['error'] += 'osm stop doesnt exist {}'.format(e)

        try:
            if cmp_stop_obj.fixed_match is None:
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

        name_changed = False
        ref_changed = False
        name_tag_in_node = False
        ref_tag_in_node = False
        version_inc_cond = False

        for node_tag in node_tags:
            key = node_tag.key
            kvalue = node_tag.value

            if key.value == 'name':
                if not kvalue.value == osm_stop_name:
                    name_changed = True
                name_tag_in_node = True
            elif node_tag.value == 'ref':
                if not kvalue.value == osm_stop_ref:
                    ref_changed = True
                ref_tag_in_node = True

        # Condition 1 if name is not present and ref is not present
        if not name_tag_in_node and not ref_tag_in_node:
            version_inc_cond = True
        print("Version cond at firstcase {}".format(version_inc_cond))
        # create KeyValueString for name and ref if the data in osm table dosent have them
        if name_tag_in_node:
            if name_changed:
                version_inc_cond = True
        else:
            version_inc_cond = True
            tag = Tag()
            name_tag = tag.add_tag('name', osm_stop_name)
            osm_stop_obj.tags.add(name_tag)

        if ref_tag_in_node:
            if ref_changed:
                version_inc_cond = True
        else:
            version_inc_cond = True
            tag = Tag()
            ref_tag = tag.add_tag('ref', osm_stop_ref)
            osm_stop_obj.tags.add(ref_tag)

        outputparams = {'newline': '', 'indent': ''}
        xml = cmp_stop_obj.cmp_single_node_to_xml('yes', version_inc=version_inc_cond)

    return xml


def save_single_comp(gtfs_stop, osm_stop, feed_id, stops_layer):
    context = {
        'match_success': 0,
        'error': ''
    }

    name_field = gtfs_stop['name_field']
    ref_field = gtfs_stop['ref_field']
    print('{} {}'.format(name_field, ref_field))
    xml = ''
    # check if the supplied tags are present

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
            osm_stop_name = xmlsafe(osm_stop_obj.name)
            context['match_success'] = 1
        except Exception as e:
            print(e)
            context['match_success'] = 0
            context['error'] += 'osm stop doesnt exist {}'.format(e)

        try:
            if cmp_stop_obj.fixed_match is None:
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

        name_to_josm = osm_stop['osm_name']

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

        name_changed = False
        ref_changed = False
        name_tag_in_node = False
        ref_tag_in_node = False
        version_inc_cond = False

        for node_tag in node_tags:
            key = node_tag.key
            kvalue = node_tag.value

            if key.value == 'name':
                if not kvalue.value == osm_stop_name:
                    name_changed = True
                name_tag_in_node = True
            elif node_tag.value == 'ref':
                if not kvalue.value == osm_stop_ref:
                    ref_changed = True
                ref_tag_in_node = True

        # Condition 1 if name is not present and ref is not present
        if not name_tag_in_node and not ref_tag_in_node:
            version_inc_cond = True
        print("Version cond at firstcase {}".format(version_inc_cond))
        # create KeyValueString for name and ref if the data in osm table dosent have them
        if name_tag_in_node:
            if name_changed:
                version_inc_cond = True
        else:
            version_inc_cond = True
            tag = Tag()
            name_tag = tag.add_tag('name', osm_stop_name)
            osm_stop_obj.tags.add(name_tag)

        if ref_tag_in_node:
            if ref_changed:
                version_inc_cond = True
        else:
            version_inc_cond = True
            tag = Tag()
            ref_tag = tag.add_tag('ref', osm_stop_ref)
            osm_stop_obj.tags.add(ref_tag)

        outputparams = {'newline': '', 'indent': ''}
        xml = cmp_stop_obj.cmp_single_node_to_xml(is_present='yes', version_inc=version_inc_cond, name=name_to_josm)

    return xml


def connect_to_JOSM_using_file(xml):
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    xmlfiledir = os.path.join(os.path.dirname(PROJECT_ROOT), 'osmapp', 'static')
    xmlfile = xmlfiledir + '/nodesosm/singlenode.osm'

    context = {
        'data': 'data',
        'error': ''
    }
    with open(xmlfile, 'w') as fh:
        fh.write(xml)

    print("Opening the node  in josm")
    try:
        josm_url = 'http://127.0.0.1:8111/open_file?filename=' + xmlfile
        webbrowser.open(josm_url)
    except requests.exceptions.RequestException as e:
        context['error'] += 'JOSM not open {}'.format(e)


def connect_to_JOSM_using_link(link):
    print(link)
    webbrowser.open("http://localhost:8111/load_data?" + urlencode(link))


'''Methods for downloading and reseting feeds'''


def rename_feed(feed_id, formId):
    feed = Feed.objects.get(id=feed_id)
    name = feed.name
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


def download_feed_in_db(file, feed_name_in_form, code, formId):
    new_feed = Feed.objects.create(name=feed_name_in_form)
    successfull_download = 0  # 0 = False
    error = 'No error while downloading the file'

    new_feed.import_gtfs(file)
    feed_id = new_feed.id

    form = GTFSForm.objects.get(id=formId)
    print('{} is the form that was created '.format(form))
    successfull_download = 1  # 1 =True

    if code == 'not_present':
        rename_feed(feed_id, formId)

    return successfull_download, error, feed_id


def download_feed_with_url(download_url, save_feed_name_in_form, code, formId):
    print("Downloading with url")
    r = requests.get(download_url, allow_redirects=True)

    feed_file = 'gs/gtfsfeeds/' + save_feed_name_in_form + '.zip'
    # temporary name for file
    if code == 'present':
        os.remove(feed_file)
        print("removed feed file {}", format(feed_file))

    open(feed_file, 'wb').write(r.content)

    feed_download_status, error, feed_id = download_feed_in_db(feed_file, save_feed_name_in_form, code, formId)

    return feed_download_status, error, feed_id


def download_feed_task(formId):
    # get url osm_tag gtfs_tag of the user entered form
    user_form = GTFSForm.objects.get(id=formId)
    entered_url = user_form.url
    entered_name = user_form.name

    if entered_name == '':
        entered_name = 'samplename'
    code = 'not_present'
    feed_download_status, error, feed_id = download_feed_with_url(entered_url, entered_name, code, formId)

    print(feed_download_status)

    if feed_download_status == 0:
        print("Inside Feed download failed")
        form_to_delete = GTFSForm.objects.latest('id')
        feed_to_delete = Feed.objects.latest('id')

        form_to_delete.delete()
        feed_to_delete.delete()

    return error, feed_id


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

    ts_diff = str(current_timestamp - form_timestamp)[0]
    status = 'The Feed is up to date'
    print("Diff is {}".format(ts_diff))
    form_reset = False
    code = 'present'
    frequency = form.frequency
    feed_id = associated_feed_id

    if int(ts_diff) > frequency:
        status = 'Reset feed with latest data'
        print('Reseting Feed')
        form_reset = True

        Feed.objects.get(id=feed_id).delete()
        download_status, error, new_feed_id = download_feed_with_url(form.url, form.name, code, formId)

        form.timestamp = timezone.now()
        form.feed_id = new_feed_id
        form.save()

        feed_id = new_feed_id

    return status, form_reset, feed_id


'''Method for reducing the map into 1/4th part'''


def reduce_bounds(southeast, southwest, northeast, northwest):
    west = [0.0, 0.0]
    west[0], west[1] = getmidpoint(northwest[1], northwest[0], southwest[1], southwest[0])
    east = [0.0, 0.0]
    east[0], east[1] = getmidpoint(northeast[1], northeast[0], southeast[1], southeast[0])
    north = [0.0, 0.0]
    north[0], north[1] = getmidpoint(northeast[1], northeast[0], northwest[1], northwest[0])
    south = [0.0, 0.0]
    south[0], south[1] = getmidpoint(southwest[1], southwest[0], southeast[1], southeast[0])

    center = [0.0, 0.0]
    center[0], center[1] = getmidpoint(north[0], north[1], south[0], south[1])

    top_left = [0.0, 0.0]
    top_left[1], top_left[0] = getmidpoint(northwest[1], northwest[0], center[0], center[1])
    top_right = [0.0, 0.0]
    top_right[1], top_right[0] = getmidpoint(northeast[1], northeast[0], center[0], center[1])
    bottom_left = [0.0, 0.0]
    bottom_left[1], bottom_left[0] = getmidpoint(southwest[1], southwest[0], center[0], center[1])
    bottom_right = [0.0, 0.0]
    bottom_right[1], bottom_right[0] = getmidpoint(southeast[1], southeast[0], center[0], center[1])

    outerbound = [southwest, northwest, northeast, southeast]
    innerbound = [bottom_left, top_left, top_right, bottom_right]

    print('saved inner bound {} {} {} {} with operator {}'.format(top_left, top_right, bottom_left, bottom_right,
                                                                  feed_name))


def dividemap(east=None, west=None, north=None, south=None, northeast_lat=None, northeast_lon=None, northwest_lat=None,
              northwest_lon=None, southeast_lat=None,
              southeast_lon=None, southwest_lat=None, southwest_lon=None, stops_coordinates=None):
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


'''For gettings keys'''


def get_keys(feed_id, type_of_nodes):
    nodes_in_feed = Node.objects.filter(feed=feed_id, purpose=type_of_nodes)
    keys = []

    for node in nodes_in_feed:
        node_tags = node.tags

        for tag in node_tags.all():
            if not tag.key.value in keys:
                keys.append(tag.key.value)

    return keys
