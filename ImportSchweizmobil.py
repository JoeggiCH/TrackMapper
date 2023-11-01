"""
This python script
- authenticates to schweizmobil.ch with a given username/password
- obtains the list of tracks
- per track finds the detail info, e.g. all coordinates and metadata
- assembles a GeoJSON Feature Collection object containing all tracks
- stores the assembled object

BUGS: - error handling
- what if files can't be written?
- what if format of cache files is "wrong"

Joerg Kummer 10. Oct 2023
"""

import requests
import json
import pyproj
from os.path import isfile,exists,expanduser
from datetime import datetime, timedelta
import PySimpleGUI as sg

# The following variables are made global and are set prior to
# exececuting ImportSchweizmobil()
# Because of this, the importer can overwrite these values
# and the values defined here become defaults

Filter={
        "hike":True,        "bike":True,
        "MinDuration":0,    "MaxDuration":1000,
        "MinLength":0,      "MaxLength":500,
        "MinUp":0,          "MaxUp":5000,
        "Nincludes":"",     "Nexcludes":"",
        "MinLon":5.7,       "MaxLon":10.8,
        "MinLat":45.7,      "MaxLat":48.0,
        "MinMdate":'01/01/1970',    "MaxMdate":'01/01/2050',
        "MinUdate":'01/01/1970',    "MaxUdate":'01/01/2050',
        "id":""
        }

# debug levels
# 0 - no console outputs
# 1 - filenames, API calls
# 2 - details on certain params
# 3 - full GeoJSON output; include 20 tracks only
debug=1

# folder for the output files
outfp=expanduser('~')+'/Documents/python/TrackMapper/'

# defines type of features in the output file:
# 0 - rectangles covering the via points of each track
# 1 - the via points of the track
# 2 - the full track coordinates (without elevation data)
opo=2

# This is the schweizmobil.ch API prefix
pre= 'https://map.schweizmobil.ch/api/'

# username / password for schweizmobil.ch
creds = json.dumps({
  "username": "username goes in here",
  "password": "password goes in here"
    })

def Import_Schweizmobil():

    # The following variables are made global and are set inside
    # ImportSchweizmobil()
    # Because of this, the importer can not incluence what values
    # this module will use, but the importer can read the values
    # after invoking ImportSchweizmobil()

    global SchweizmobCacheDir
    SchweizmobCacheDir='cache/schweizmobil.ch/'

    global trksfn
    trksfn=outfp+SchweizmobCacheDir+"tracks response.geojson"

    global outfn
    outfn=outfp+"GeoJSON/schweizmobil.GeoJSON"

    # init requests object
    session = requests.Session()
    session.headers={}

    try:
        #login
        response = session.post(pre+'4/login',data=creds)

        rst=response.status_code
        ErrC=response.json()['loginErrorCode']
        if (rst!=200 or ErrC!=200):
            raise Exception (f"Authentication failed; ({rst}/{ErrC})")

        # fetch the list of tracks
        response = session.get(pre+'5/tracks')
        if debug>1: print ("Tracks API call ",response.status_code)

        if response.status_code==200:
            tracks=response.json()
            # API was reachable, so let's write the response to a file, in case the API is
            # unreachable the next time around
            fi=open(trksfn,mode="w")
            print(response.text,file=fi)
            fi.close()
            if debug>0: print ("Tracks API response cached",trksfn)
        else:
            raise Exception(f"Status Code {response.status_code}")
    except Exception as e:
        print (e)
        print("Issues talking to schweizmobil.ch! Credentials? Offline ? Wrong API prefix?")
        try:
            print ("Trying to continue based on response cached earlier")
            fi=open(trksfn,mode="r")
            tracks=json.load(fi)
            fi.close()
        except:
            print ("No cache file - giving up !")
            return

    # setup progress bar
    # layout the form
    layout = [[sg.Text(f'Processing {len(tracks)} tracks')],
              [sg.ProgressBar(max_value=len(tracks), orientation='h', size=(20, 20), key='progress')]]

    window = sg.Window('Progress', layout, finalize=True)
    progress_bar = window['progress']

    # setup transformer object to transform
    # Swiss LV03 coordinates used by schweizmobil.ch to WGS84
    trafo=pyproj.Transformer.from_crs(21781,4326)

    # start building the GeoJSON FeatureCollection
    geo={'type':'FeatureCollection',
         'features':[]
         }

    k=0
    included=0
    # process each track in the tracks reponse
    if debug>0: print("Start fetching track details")
    for i in tracks:
        if ((debug>1) and (k==20)): break
        k=k+1
        progress_bar.update_bar(k)
        iid=i['id']
        ts=i['modified_at'].replace(":", "" )
        trkn=f'{outfp}{SchweizmobCacheDir}track {iid}-{ts}.geojson'

        # write a cache file, if not present
        # to offload the API and speed up processing
        # result is the "track" dict representing the GeoJSON provided
        # by the schweizmobil.ch
        if not isfile(trkn):
            # API call to fetch the track detail
            response = session.get(pre+'4/tracks/'+str(iid))
            if response.status_code!=200:
                print (f'API call to obtain details on track {iid}\
                    failed with status {response.status_code}')
                return
            if debug>1: print (f"Track API call for {iid} successful")

            # prepare the dict "track" from response
            track=response.json()

            fi=open(trkn,mode="w")
            print (response.text,file=fi)
            fi.close()
            if debug>0: print ("wrote track cache ", trkn)

        else: # read from cache file
            fi=open(trkn,mode="r")
            # make dict track from file
            track=json.load(fi)
            fi.close()
            if debug>1:print ("read track cache ", trkn)

        # reformat properties
        # handling exceptions here as the format/availability of the
        # properties is up to schweizmobil.ch and may change
        try:
            props=track["properties"]

            fmt='%Y-%m-%dT%H:%M:%SZ'
            mstmp=datetime.strptime(i['modified_at'],'%Y-%m-%dT%H:%M:%SZ')
            datestr=mstmp.strftime("%d. %b %Y")

            if (props['userdate']!="null" and props['userdate']!=None):
                ustmp=datetime.strptime(props['userdate'],'%Y-%m-%d')
                ud=ustmp.strftime("%d. %b %Y")

            # Winter hike and snowshoe hike unhandled for the time being
            if i['timetype']=="wander":
                tt="hike"
                minutes=round(props['meta']['walking'])
                ttime=str(timedelta(minutes=minutes))

            else:
                tt="bike"
                minutes=round(props['meta']['biking'])
                ttime=str(timedelta(minutes=minutes))

            # newprops will go into the new GeoJSON feature we are building
            newprops={
                'id':iid,
                'Name':i['name'],
                'URL': f'https://map.schweizmobil.ch/?trackId={iid}',
                'User date':ud,
                'Modified':i['modified_at'],
                'Track modified':datestr,
                'Track type':tt,
                'Duration':ttime,
                'Length':str(round(props['meta']['length'])/1000)+" km",
                'Total up':str(round(props['meta']['totalup']))+" m",
                'Total down':str(round(props['meta']['totaldown']))+" m",
                'Min elevation':str(round(props['meta']['elemin']))+" m",
                'Max elevation':str(round(props['meta']['elemax']))+" m"
             }
        except Exception as e:
            if debug>0: print (f'Track {iid}: properties incomplete - skipping')
            print(str(e))
            continue

        # Check against Filter values related to the properties (not the coordinates)
        if (minutes<int(Filter["MinDuration"]) or minutes>int(Filter["MaxDuration"])):
            if debug>1: print (f"skipping track {iid} because of duration filter")
            continue

        x=round(props['meta']['length'])/1000
        if (x<float(Filter["MinLength"]) or x>float(Filter["MaxLength"])):
            if debug>1: print (f"skipping track {iid} because of length filter")
            continue

        x=round(props['meta']['totalup'])
        if (x<float(Filter["MinUp"]) or x>float(Filter["MaxUp"])):
            if debug>1: print (f"skipping track {iid} because of Total up filter")
            continue

        if Filter["Nincludes"]:
            if not Filter["Nincludes"].lower() in i["name"].lower():
                if debug>1: print (f"skipping track {iid} because of Name includes filter")
                continue

        if Filter["Nexcludes"]:
            if Filter["Nexcludes"].lower() in i["name"].lower():
                if debug>1: print (f"skipping track {iid} because of Name excludes filter")
                continue

        mminf=datetime.strptime(Filter["MinMdate"],'%d/%m/%Y')
        mmaxf=datetime.strptime(Filter["MaxMdate"],'%d/%m/%Y')
        if mstmp<mminf or mstmp>mmaxf:
            if debug>1:
                print (f"skipping track {iid} because of modified date filter")
            continue

        if (props['userdate']!="null" and props['userdate']!=None):
            mminf=datetime.strptime(Filter["MinUdate"],'%d/%m/%Y')
            mmaxf=datetime.strptime(Filter["MaxUdate"],'%d/%m/%Y')
            if ustmp<mminf or ustmp>mmaxf:
                if debug>1:
                    print (f"skipping track {iid} because of user date filter")
                continue

        if Filter["id"]:
            if str(i["id"])!=Filter["id"]:
                if debug>1: print (f"skipping track {iid} because of id filter")
                continue

        if (i['timetype']=="wander") and (not Filter["hike"]):
            if debug>1: print (f"skipping track {iid} because of track type filter")
            continue

        if (i['timetype']=="velo") and (not Filter["bike"]):
            if debug>1: print (f"skipping track {iid} because of track type filter")
            continue

        # transform/reformat coordinates, find enclosing rectangle etc
        # finish constructing the feature dict representing the track

        # skip this track if the format does not contain the
        # expected properties.via_points dict
        try:
            via=json.loads(props["via_points"])
        except:
            if debug>0: print (f'Track {iid}: no via data - skipping')
            continue

        # find the coordinates of the rectangle enclosing
        # the via max/min values
        # via points are the points selected by the schweizmobil.ch user
        # when drawing the track. The other coordinates are extrapolated
        # by schweizmobil.ch
        latmax=0; lonmax=0
        latmin=1000000; lonmin=1000000

        for j in via:
            (j[1],j[0])=trafo.transform(j[0],j[1])
            latmax=max(latmax,j[1])
            latmin=min(latmin,j[1])
            lonmax=max(lonmax,j[0])
            lonmin=min(lonmin,j[0])

        # skip tracks if they are outside the coordinate filter
        if (lonmin>float(Filter["MaxLon"]) or lonmax<float(Filter["MinLon"])):
            if debug>1: print (f"skipping track {iid} because of longitude filter")
            continue

        if (latmin>float(Filter["MaxLat"]) or latmax<float(Filter["MinLat"])):
            if debug>1:
                print (f"skipping track {iid} because of latitude filter")
            continue

        # prepare feature structure
        if opo==0:
            feature={
                'type':'Feature',
                'geometry': {
                    'type':'Polygon',
                    'coordinates':[[
                        [lonmax,latmax],
                        [lonmax,latmin],
                        [lonmin,latmin],
                        [lonmin,latmax],
                        [lonmax,latmax]
                    ]]
                },
                'properties': newprops
            }

        if opo==1:
            feature={
                'type':'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates':via
                },
                'properties': newprops
            }

        if opo==2:
            try:
                coord=track['geometry']['coordinates']
                for j in coord:
                    (j[1],j[0])=trafo.transform(j[0],j[1])
            except:
                if debug>0: print (f'Track {iid}: no Geometry.Coordinates data - skipping')
                continue

            feature={
                'type':'Feature',
                'geometry': track['geometry'],
                'properties': newprops
            }

        # append the feature dict (current track) to the geo dict (collection of tracks)
        if (opo==0 or opo==1 or opo==2):
            geo['features'].append(feature)
            included+=1

    # close the progress bar window
    window.close()

    if geo['features']!=[]:
        if debug>0:
            match opo:
                case 0: print ("Output includes only a bounding box")
                case 1: print ("Output includes via coordinates")
                case 2: print ("Output includes full track coordinates")
                case _: print ("Unsupported opo parameter value - no track/features written")
            print (f"Included {included} of {len(tracks)} tracks")

        f=open(f'{outfn}',mode="w")
        if debug<2:
            print (json.dumps(geo),file=f)
        else:
            print (json.dumps(geo, indent="\t"),file=f)
        f.close()

        if debug>0: print(f"GeoJSON with schweizmobil.ch tracks written: {outfn}")
    else:
        print("\nAfter filtering there were no more tracks, map not updated!\n")
