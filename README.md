# TrackMapper

schweizmobil.ch is a service to discover and plan (mostly) hiking/biking tracks in Switzerland.
Viewing tracks does not require a paid subscription, designing own tracks does.

This project 
* uses the schweizmobil.ch API described at https://github.com/JoeggiCH/schweizmobil.ch-API to download all tracks of a given user (with a paid subscription)
* converts tracks into WGS84 coordinates and a GeoJSON FeatureCollection.
* renders the FeatureCollection in a browser-viewable map - using python folium and leaflet.js.
* Before rendering tracks can be filtered on multiple criteria, such as the length in kilometers, duration, meters uphill etc
