# TrackMapper
schweizmobil.ch is a service to discover and plan (mostly) hiking/biking tracks in Switzerland. Viewing tracks does not require a paid subscription, drawing own tracks does. The schweizmobil.ch UI is great but unfortunately can only show one of the user-created tracks at a time. I have 300+ tracks and struggle to keep the overview of what I planned/did in a given region.

So, this project ..
* uses the schweizmobil.ch API described at https://github.com/JoeggiCH/schweizmobil.ch-API to download all tracks of a given user (with a paid subscription)
* allows users to filter tracks based on a number of criteria, such as the hike/bike length in kilometers, duration, meters uphill etc
* converts tracks into WGS84 coordinates and a GeoJSON FeatureCollection
* renders the FeatureCollection in a browser-viewable map (using python folium and leaflet.js)

I developed and tested this code (a little) under Windows. 
I also did an installation under a local Ubuntu and the code started but at least one button did not work as expected. Also, I had to install tkinter separately as a binary and pySimpleGUI required an extra step to register in order to get a named user license.

To start, please invoke '''python TrackMapper.pyw'''

Please note that I am not affiliated in any way with the schweizmobil.ch foundation and this repo is not an official publication of schweizmobil.ch. I created this repo for my training and because I was unable to find another solution for my need.

Joerg
