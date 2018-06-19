from __future__ import unicode_literals

import os
import numpy as np
import requests
from django.utils import timezone
from multigtfs.models import Feed

from .models import GTFSForm
from django.db import connection
from geographiclib.geodesic import Geodesic
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def getmidpoint(lat1, lon1, lat2, lon2):
    l = Geodesic.WGS84.InverseLine(lat1, lon1, lat2, lon2)

    m = l.Position(0.5 * l.s13)

    return m['lat2'], m['lon2']


def dividemap(east=None, west=None, north=None, south=None, northeast_lat=None, northeast_lon=None, northwest_lat=None,
              northwest_lon=None, southeast_lat=None,
              southeast_lon=None, southwest_lat=None, southwest_lon=None, coordinates_arr=None):
    '''testing to get 1/4th of the bbbox using AdvanceTransit bounds'''
    northeast_lat = 43.729133606
    northeast_lon = -72.0132064819
    northwest_lat = 43.729133606
    northwest_lon = -72.343421936
    southeast_lat = 43.6245117188
    southeast_lon = -72.0132064819
    southwest_lat = 43.6245117188
    southwest_lon = -72.343421936
    west = {'lat': 0.0, 'lon': 0.0}
    west['lat'], west['lon'] = getmidpoint(northwest_lat, northwest_lon, southwest_lat, southwest_lon)
    east = {'lat': 0.0, 'lon': 0.0}
    east['lat'], east['lon'] = getmidpoint(northeast_lat, northeast_lon, southeast_lat, southeast_lon)
    north = {'lat': 0.0, 'lon': 0.0}
    north['lat'], north['lon'] = getmidpoint(northeast_lat, northeast_lon, northwest_lat, northwest_lon)
    south = {'lat': 0.0, 'lon': 0.0}
    south['lat'], south['lon'] = getmidpoint(southwest_lat, southwest_lon, southeast_lat, southeast_lon)

    center = {'lat': 0, 'lon': 0}
    center['lat'], center['lon'] = getmidpoint(west['lat'], west['lon'], east['lat'], east['lon'])

    stops_coordinates = [[43.6377754211, -72.2750091553], [43.6361541748, -72.2879180908],
                         [43.6380233765, -72.3021316528], [43.640838623, -72.2555389404],
                         [43.6389656067, -72.2579574585], [43.638458252, -72.2679672241],
                         [43.7254447937, -72.3178710938], [43.7252197266, -72.3154678345],
                         [43.6798934937, -72.2944259644], [43.6651649475, -72.2574310303],
                         [43.7057113647, -72.2896499634], [43.696269989, -72.2799072266],
                         [43.6748428345, -72.2662124634], [43.7074584961, -72.2875900269],
                         [43.7040977478, -72.2895812988], [43.6856613159, -72.2933883667],
                         [43.6982765198, -72.280960083], [43.6755599976, -72.2722702026],
                         [43.6901817322, -72.2912979126], [43.7002906799, -72.2894287109],
                         [43.7016410828, -72.2893981934], [43.6999397278, -72.2897262573],
                         [43.627040863, -72.3246688843], [43.6245117188, -72.3240661621],
                         [43.625202179, -72.3226470947], [43.6269721985, -72.3195648193],
                         [43.6284980774, -72.3210296631], [43.6320724487, -72.316078186],
                         [43.6347846985, -72.3164520264], [43.6381568909, -72.3144989014],
                         [43.6547737122, -72.3273086548], [43.6539611816, -72.3244171143],
                         [43.6478118896, -72.310295105], [43.7027549744, -72.2817153931],
                         [43.6525802612, -72.3202972412], [43.6516189575, -72.316986084],
                         [43.6932029724, -72.2758560181], [43.7080116272, -72.2841567993],
                         [43.7007675171, -72.2886734009], [43.6901817322, -72.2914581299],
                         [43.646572113, -72.3344268799], [43.6605529785, -72.2530136108],
                         [43.7224464417, -72.3161239624], [43.6652259827, -72.2572860718],
                         [43.6447944641, -72.3320388794], [43.6428756714, -72.2524642944],
                         [43.6732368469, -72.2677688599], [43.6731948853, -72.2677688599],
                         [43.6352539063, -72.3164672852], [43.6383056641, -72.3148193359],
                         [43.7053909302, -72.3097839355], [43.7026901245, -72.3135452271],
                         [43.6457366943, -72.3095626831], [43.6403617859, -72.3047027588],
                         [43.6457710266, -72.3099822998], [43.7047386169, -72.3050765991],
                         [43.7026062012, -72.2949523926], [43.7032966614, -72.312538147],
                         [43.7053756714, -72.3095092773], [43.7027397156, -72.2949295044],
                         [43.7050323486, -72.3051223755], [43.7024307251, -72.2886505127],
                         [43.7050170898, -72.2877578735], [43.6415252686, -72.3339385986],
                         [43.6379165649, -72.2748336792], [43.6363372803, -72.2885665894],
                         [43.6577033997, -72.3154983521], [43.6649703979, -72.3128814697],
                         [43.6615371704, -72.3138809204], [43.6390647888, -72.258102417],
                         [43.6387138367, -72.2658004761], [43.6511306763, -72.3166046143],
                         [43.6409492493, -72.2556381226], [43.6558532715, -72.2493591309],
                         [43.6532287598, -72.2463226318], [43.6888771057, -72.269203186],
                         [43.6845932007, -72.2704315186], [43.7011833191, -72.2816390991],
                         [43.6462211609, -72.2535400391], [43.6428909302, -72.2516174316],
                         [43.6598167419, -72.3366699219], [43.6592712402, -72.3363037109],
                         [43.6546134949, -72.3274612427], [43.6534194946, -72.3239212036],
                         [43.652797699, -72.3188171387], [43.6585426331, -72.3148880005],
                         [43.6611671448, -72.3136672974], [43.6649208069, -72.3125076294],
                         [43.6448020935, -72.3323287964], [43.6441383362, -72.3287811279],
                         [43.6439743042, -72.3215637207], [43.641242981, -72.3201065063],
                         [43.6473960876, -72.3188552856], [43.6478919983, -72.3346710205],
                         [43.6493492126, -72.3206787109], [43.6455192566, -72.3413772583],
                         [43.6729164124, -72.2964553833], [43.6502418518, -72.3226394653],
                         [43.6497383118, -72.3188018799], [43.6480789185, -72.343421936],
                         [43.6599311829, -72.2525558472], [43.668258667, -72.3115692139],
                         [43.6729469299, -72.3093719482], [43.6546936035, -72.3087005615],
                         [43.6510353088, -72.3102722168], [43.695476532, -72.3194122314],
                         [43.685760498, -72.2934341431], [43.6903419495, -72.3203811646],
                         [43.6919708252, -72.3199920654], [43.6834373474, -72.3179550171],
                         [43.6868743896, -72.3210372925], [43.6760177612, -72.3093109131],
                         [43.6809768677, -72.3134613037], [43.6748962402, -72.2662353516],
                         [43.6888961792, -72.269317627], [43.675617218, -72.2723083496],
                         [43.6998062134, -72.2840270996], [43.6847114563, -72.2704391479],
                         [43.6471328735, -72.2536697388], [43.6428909302, -72.2516021729],
                         [43.6445541382, -72.2541427612], [43.631072998, -72.3240203857],
                         [43.6326789856, -72.3221664429], [43.7145996094, -72.3084182739],
                         [43.7154579163, -72.276260376], [43.7182273865, -72.3079681396],
                         [43.716960907, -72.3079681396], [43.6511306763, -72.3100357056],
                         [43.7192420959, -72.3093261719], [43.6546897888, -72.3086090088],
                         [43.6808395386, -72.2944641113], [43.6731338501, -72.2960586548],
                         [43.6936798096, -72.2759170532], [43.6556358337, -72.2493591309],
                         [43.6530418396, -72.2461929321], [43.6608314514, -72.3398513794],
                         [43.6463623047, -72.0132293701], [43.6462631226, -72.0132064819],
                         [43.6446342468, -72.1432342529], [43.6446342468, -72.1432342529],
                         [43.7080497742, -72.2842407227], [43.6963691711, -72.2802963257],
                         [43.729133606, -72.2674865723], [43.7256851196, -72.2696990967],
                         [43.7218475342, -72.2713088989], [43.7242507935, -72.2699737549],
                         [43.7152328491, -72.2758026123], [43.7185745239, -72.2734298706],
                         [43.7178459167, -72.3133850098], [43.7145500183, -72.3084869385],
                         [43.7235031128, -72.2710266113], [43.7193832397, -72.2733154297],
                         [43.692111969, -72.3195724487], [43.6902275085, -72.3200073242],
                         [43.6870231628, -72.3208236694], [43.6837005615, -72.3178482056],
                         [43.6816978455, -72.3141326904], [43.6761703491, -72.3091659546],
                         [43.673210144, -72.3091278076], [43.6685371399, -72.3108978271],
                         [43.6956787109, -72.3189849854]]

    v0 = [northwest_lat, northwest_lon]
    v1 = [northeast_lat, northeast_lon]
    v2 = [southwest_lat, southwest_lon]
    v3 = [southeast_lat, southeast_lon]

    lats_vect = np.array([v0[0], v1[0], v2[0], v3[0]])
    lons_vect = np.array([v0[1], v1[1], v2[1], v3[1]])

    x, y = 43.729133606, -72.2674865723

    lats_lon_vect = np.column_stack((lats_vect, lons_vect))
    polygon = Polygon(lats_lon_vect)
    point = Point(x, y)
    print(polygon.contains(point))

    '''
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(gtfs_stop.feed) FROM gtfs_feed INNER JOIN gtfs_stop ON gtfs_feed.id=15')
    result = cursor.fetchall()
    print(result)
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
        form.feed = feed
        form.save()

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


def reset_feed(formId):
    form = GTFSForm.objects.get(id=formId)
    form_timestamp = form.timestamp
    print(form_timestamp)
    current_timestamp = timezone.now()
    form_name = form.name

    ts_diff = str(current_timestamp - form_timestamp)[0]
    status = 'The Feed is up to date'

    code = 'present'
    frequency = form.frequency
    if int(ts_diff) > frequency:
        status = 'Reseting feed with latest data'
        form.timestamp = timezone.now()
        form.save()
        Feed.objects.filter(name=form_name).all().delete()
        download_feed_with_url(form.url, form.name, code, formId)

    '''since form has one to one relationship with every feed so when the feed is renewed form.feed should be updated'''

    return status
