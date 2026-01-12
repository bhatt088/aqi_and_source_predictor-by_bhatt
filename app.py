import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import requests
import os

from dotenv import load_dotenv
load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


# Load trained model
model = joblib.load("aqi_model.pkl")

st.title("🌫️ AQI Prediction & Pollution Source App")
st.caption("Gas inputs in ppb | Converted internally for ML model")


import plotly.graph_objects as go   # ✅ REQUIRED

# ======================
# AQI GAUGE FUNCTION (ADD THIS HERE)
# ======================
def aqi_gauge(aqi):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi,
        title={'text': "Air Quality Index (AQI)"},
        gauge={
            'axis': {'range': [0, 500]},
            'bar': {'color': "white"},
            'steps': [
                {'range': [0, 50], 'color': "#00e400"},      # Good
                {'range': [51, 100], 'color': "#ffff00"},   # Satisfactory
                {'range': [101, 200], 'color': "#ff7e00"},  # Moderate
                {'range': [201, 300], 'color': "#ff0000"},  # Poor
                {'range': [301, 400], 'color': "#8f3f97"},  # Very Poor
                {'range': [401, 500], 'color': "#7e0023"}   # Severe
            ],
        }
    ))
    return fig





# api call
def fetch_city_data(city):
    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": city,
        "aqi": "yes"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        air = data["current"]["air_quality"]

        return {
            "PM2.5": air.get("pm2_5", 50),
            "PM10": air.get("pm10", 80),
            "SO2": air.get("so2", 5),
            "CO": air.get("co", 300),
            "OZONE": air.get("o3", 10),
            "NO2": air.get("no2", 20),
            "NH3": air.get("nh3", 20)
        }

    except Exception:
        return None

city = st.selectbox(
    "Select City",
    ["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai"]
)

city_pollution = fetch_city_data(city)

if city_pollution is None:
        st.warning("Live data not available. Using default values.")
        city_pollution = {
            "PM2.5": 50, "PM10": 80, "SO2": 5,
            "CO": 300, "OZONE": 10, "NO2": 20, "NH3": 20
        }


# ======================
# 1️⃣ SLIDERS (ppb)
# ======================
pm25 = st.slider("PM2.5 (µg/m³)", 0, 500, int(city_pollution["PM2.5"]))
pm10 = st.slider("PM10 (µg/m³)", 0, 500, int(city_pollution["PM10"]))

so2 = st.slider("SO2 (ppb)", 0, 200, int(city_pollution["SO2"]))
co = st.slider("CO (ppb)", 0, 2000, int(city_pollution["CO"]))

ozone = st.slider("OZONE (ppb)", 0, 200, int(city_pollution["OZONE"]))
no2 = st.slider("NO2 (ppb)", 0, 200, int(city_pollution["NO2"]))
nh3 = st.slider("NH3 (ppb)", 0, 200, int(city_pollution["NH3"]))


# ======================
# 2️⃣ UNIT CONVERSION (ppb → model scale)
# ======================
so2_model = so2 / 1000
co_model = co / 1000
ozone_model = ozone / 1000
no2_model = no2 / 1000
nh3_model = nh3 / 1000

# ======================
# 3️⃣ INPUT DATAFRAME
# ======================
input_data = pd.DataFrame([{
    'PM2.5': pm25,
    'PM10': pm10,
    'SO2': so2_model,
    'CO': co_model,
    'OZONE': ozone_model,
    'NO2': no2_model,
    'NH3': nh3_model
}])

# ======================
# 4️⃣ PREDICTION
# ======================
if st.button("Predict AQI"):
    aqi = model.predict(input_data)[0]

    # AQI category
    if aqi <= 50:
        category = "Good 😊"
    elif aqi <= 100:
        category = "Satisfactory 🙂"
    elif aqi <= 200:
        category = "Moderate 😐"
    elif aqi <= 300:
        category = "Poor 😷"
    elif aqi <= 400:
        category = "Very Poor 🤒"
    else:
        category = "Severe ☠️"

    # Pollution source (use ORIGINAL ppb values)
    if no2 > 60 and co > 300:
        source = "Vehicular Pollution 🚗"
    elif so2 > 40:
        source = "Industrial Pollution 🏭"
    elif pm10 > 200:
        source = "Dust / Construction 🌫️"
    elif pm25 > 150:
        source = "Biomass / Crop Burning 🔥"
    else:
        source = "Mixed Sources 🌍"

    st.success(f"Predicted AQI: {int(aqi)}")
    st.info(f"AQI Category: {category}")
    st.warning(f"Major Pollution Source: {source}")

    st.plotly_chart(aqi_gauge(aqi), use_container_width=True)


