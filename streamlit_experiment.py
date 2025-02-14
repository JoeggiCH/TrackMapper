import streamlit as st

import streamlit as st
from datetime import date

# Streamlit form
st.title("Filter schweizmobil.ch tracks")

with st.form(key='filter_form'):
    col1, col2 = st.columns(2)
    
    with col1:
        min_duration = st.number_input("Min Duration [mins]", min_value=0, value=0)
        min_length = st.number_input("Min length [km]", min_value=0, value=0)
        min_meters_uphill = st.number_input("Min meters uphill", min_value=0, value=0)
        track_name_includes = st.text_input("Track name includes", "")
        min_longitude = st.number_input("Min Longitude", value=5.7)
        min_latitude = st.number_input("Min Latitude", value=45.7)
        min_mod_date = st.date_input("Min mod'd date [dd/mm/yy]", value=date(1970, 1, 1))
        min_user_date = st.date_input("Min User Date", value=date(1970, 1, 1))
        track_id = st.text_input("Track id", "")

    with col2:
        max_duration = st.number_input("Max Duration [mins]", min_value=0, value=1000)
        max_length = st.number_input("Max length [km]", min_value=0, value=500)
        max_meters_uphill = st.number_input("Max meters uphill", min_value=0, value=5000)
        track_name_excludes = st.text_input("Track name excludes", "")
        max_longitude = st.number_input("Max Longitude", value=10.8)
        max_latitude = st.number_input("Max Latitude", value=48.0)
        max_mod_date = st.date_input("Max mod'd date [dd/mm/yy]", value=date(2050, 1, 1))
        max_user_date = st.date_input("Max User Date", value=date(2050, 1, 1))

    hike = st.checkbox("Hike", value=True)
    bike = st.checkbox("Bike", value=True)

    submit_button = st.form_submit_button(label='Set Filter')

if submit_button:
    # Output the filter inputs (for demonstration purposes)
    st.write("Filters applied:")
    st.write("Min Duration [mins]:", min_duration)
    st.write("Max Duration [mins]:", max_duration)
    st.write("Min length [km]:", min_length)
    st.write("Max length [km]:", max_length)
    st.write("Min meters uphill:", min_meters_uphill)
    st.write("Max meters uphill:", max_meters_uphill)
    st.write("Track name includes:", track_name_includes)
    st.write("Track name excludes:", track_name_excludes)
    st.write("Min Longitude:", min_longitude)
    st.write("Max Longitude:", max_longitude)
    st.write("Min Latitude:", min_latitude)
    st.write("Max Latitude:", max_latitude)
    st.write("Min mod'd date [dd/mm/yy]:", min_mod_date)
    st.write("Max mod'd date [dd/mm/yy]:", max_mod_date)
    st.write("Min User Date:", min_user_date)
    st.write("Max User Date:", max_user_date)
    st.write("Track id:", track_id)
    st.write("Hike:", hike)
    st.write("Bike:", bike)
