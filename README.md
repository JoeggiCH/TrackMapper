# TrackMapper
schweizmobil.ch is a service to discover and plan (mostly) hiking/biking tracks in Switzerland. Viewing tracks does not require a paid subscription, drawing own tracks does. The schweizmobil.ch UI is great but unfortunately can only show one of the user-created tracks at a time. I have 300+ tracks and struggle to keep the overview of what I planned/did in a given region.

So, this project ..
* uses the schweizmobil.ch API described at https://github.com/JoeggiCH/schweizmobil.ch-API to download all tracks of a given user (with a paid subscription)
* allows users to filter tracks based on a number of criteria, such as the hike/bike length in kilometers, duration, meters uphill etc
* converts tracks into WGS84 coordinates and a GeoJSON FeatureCollection
* renders the FeatureCollection in a browser-viewable map (using python folium and leaflet.js)

I developed and tested this code (a little) under Windows. 
I also did an installation under a local Ubuntu and the code started but at least one button did not work as expected. Also, I had to install tkinter separately as a binary and pySimpleGUI required an extra step to register in order to get a named user license.

Please use ```python3 TrackMapper.pyw``` to start
- The button ```Set Filter``` brings up a window with filter criteria, which the code will apply to fetch track data from schweizmobil.ch
- The button ```Fetch Data & Apply Filter``` connects to schweizmobil.ch, obtains the track data - based on the filtering criteria - and creates a local map.html file
- the html file contains GeoJSON representations of the tracks and the leaflet code to render the tracks on various base maps 
- The button ```Open``` will open the local map.html file in the default browser
- ```Publish``` executes an external script 'update web.bat', which pushes map.html to a web server of your choice - IF you have modified 'update web.bat' to do so!
- ```Open``` will open the published version of map.html on the default web browser. 

And..
- TrackMapper.py will ask for your schweizmobil.ch credentials and will store them locally in an encrypted file.
- You can choose a password for the encryption of the password file. By default there is no password.
- At the next startup of TrackMapper.pyw, if the password file is available, the code will ask for the password. Just hitting 'return' will work for the empty, default password.
- TrackMapper.py creates a local cache of the tracks, which speeds up fetching tracks from the second time on.

Please note that I am not affiliated in any way with the schweizmobil.ch foundation and this repo is not an official publication of schweizmobil.ch. I created this repo for my training and because I was unable to find another solution for my need.

Feedback & questions are welcome !

Feb 2025, Joerg
