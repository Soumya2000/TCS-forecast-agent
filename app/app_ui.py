import streamlit as st
import requests
import json

st.title("📊 TCS Financial Forecasting Dashboard")

st.write("Enter parameters below and click 'Generate Forecast'")

quarters = st.number_input("Number of past quarters to analyze", 1, 8, 3)
include_market = st.checkbox("Include Market Data")
task_note = st.text_area("Task Note", "Forecast the next quarter based on recent trends.")

if st.button("Generate Forecast"):
    payload = {
        "quarters": quarters,
        "include_market_data": include_market,
        "task_note": task_note
    }
    res = requests.post("http://127.0.0.1:8000/forecast", json=payload)
    if res.status_code == 200:
        forecast = res.json()
        st.json(forecast)
    else:
        st.error(f"Error: {res.status_code}")
        st.text(res.text)
