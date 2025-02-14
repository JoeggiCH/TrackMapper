import streamlit as st

import pandas as pd
df = pd.DataFrame({
  'first column': [1, 2, 3, 4,5],
  'second column': [10, 20, 30, 40,50]
})

df

if st.button("Say hello"):
    st.write("Why hello there")
else:
    st.write("Goodbye")

if st.button("Aloha", type="tertiary"):
    st.write("Ciao")