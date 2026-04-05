import streamlit as st
import requests
import os

st.title("Your App Prototype")

# Use Render environment variable
API_URL = os.getenv("API_URL")

if not API_URL:
    st.error("API_URL not set")
else:
    if st.button("Fetch Data"):
        try:
            response = requests.get(f"{API_URL}/data")
            if response.status_code == 200:
                st.json(response.json())
            else:
                st.error("Error fetching data")
        except Exception as e:
            st.error(f"Request failed: {e}")
