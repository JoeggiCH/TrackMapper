"""
This python script
- takes a GeoJSON file as input
- creates a HTML output file with a map
- the includes several basemap/tile options
- the map renders the GeoJSON FeatureCollection

The script is based on the python folium library,
which is based on the Javascript leaflet.js library

Joerg Kummer 8. Oct 2023
"""

import folium
import folium.plugins
import json
import pyproj
import random
from os.path import expanduser

# The following variables are made global and are set prior to
# exececuting ImportSchweizmobil()
# Because of this, the importer can overwrite these values
# and the values defined here are defaults

# debug levels
# 0 - no console outputs
# 1 - filenames, API calls
debug=1

# some defaults, which are likely to be overwritten by main
infile=expanduser('~')+'/Documents/TrackMapper/GeoJSON/schweizmobil.GeoJSON'
outfileo =expanduser('~')+'/Documents/TrackMapper/PMoutput/map.html'

# OpenTopoMap - gutes Shading, Höhenlinien
otattr = (
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    'Contributors, &copy; <a href="http://viewfinderpanoramas.org">SRTM</a>'
    'Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>'
    '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
)
ottiles = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"

# ESRI Worldimagery
attr= 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'

# OpenStreetMap.CH, Höhenlinien und gutes Shading aber nur Schweiz
osmchattr= '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
osmchtiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"

#SwissFederalGeoportal_SWISSIMAGE
tiles='https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg'
attr='&copy; <a href="https://www.swisstopo.admin.ch/">swisstopo</a>'
# minZoom: 2,
# maxZoom: 19,
#	bounds: [[45.398181, 5.140242], [48.230651, 11.47757]]


#SwissFederalGeoportal_NationalMap
#	minZoom: 2,
#	maxZoom: 18,
#	bounds: [[45.398181, 5.140242], [48.230651, 11.47757]]
attr='&copy; <a href="https://www.swisstopo.admin.ch/">swisstopo</a>'
# From https://www.geo.admin.ch/en/wmts-available-services-and-data
# https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/{Time}/3857/{TileMatrix}/{TileCol}/{TileRow}.jpeg
tilesCHCol='https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg'
tilesCHBW='https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.landeskarte-grau-10/default/current/3857/{z}/{x}/{y}.png'

def Prepare_Map():
    # Create a Map instance
    m = folium.Map(tiles=None,location=[47.278106, 7.820381],
                       zoom_start=9, crs="EPSG3857",control_scale=True)
    if (debug>0): print (f"folium.Map done")

    folium.TileLayer(tilesCHCol,attr=attr,name='Swisstopo Color',overlay=False,show=True).add_to(m)
    folium.TileLayer(tiles=tilesCHBW,attr=attr,name='Swisstopo Gray',overlay=False,show=False).add_to(m)
    folium.TileLayer(tiles=tiles,attr=attr,name='Swisstopo Swissimage',overlay=False,show=False).add_to(m)
    folium.TileLayer(tiles=ottiles,attr=otattr,name='OSM OpenTopo',overlay=False,show=False).add_to(m)
    folium.TileLayer(tiles=osmchtiles,attr=osmchattr,name='OSM CH',overlay=False,show=False).add_to(m)

    if (debug>0): print (f"folium.TileLayers added")
    
    # styles : https://leafletjs.com/reference.html#path-option
    # red color variations
    stl=lambda feature: {
        'weight':'5','color':"#ff"+hex(random.randrange(255))[2:]+"80",'opacity':'0.7'}

    # blue color variations
    stl=lambda feature: {
        'weight':'5','color':"#"+hex(random.randrange(255))[2:]+"40ff",'opacity':'0.6'}

    # green for highlight
    hlf=lambda feature: {'fillColor': 'green','weight':'8','color':'#ff0000','opacity':1.0}

    fields=['Name','Track type','Duration','Length',
            'Total up','Total down','Min elevation','Max elevation','User date','Track modified','URL']

    folium.GeoJson(infile,
                   name="Schweizmobil.ch Tracks",
                   tooltip=folium.GeoJsonTooltip(fields=['Name']),
                   popup=folium.GeoJsonPopup(fields=fields,localize=False),
                   style_function=stl,
                   highlight_function=hlf,
                   zoom_on_click=True
                   ).add_to(m)
    
    if (debug>0): print (f"folium.GeoJSON added")

    folium.plugins.Geocoder().add_to(m)
    folium.FeatureGroup("test",overlay=True)
    folium.LayerControl().add_to(m)

    # Save the map
    m.save(outfile)
    if (debug>0): print (f"Written HTML {outfile}")
