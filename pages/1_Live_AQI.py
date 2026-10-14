"""
pages/1_Live_AQI.py
Detailed City Air Quality Page for AirWatch India.
Displays comprehensive live atmospheric data, interactive gauge charts,
multi-pollutant breakdown tables, and 72-hour trends.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

from src.live_aqi import (
    MAJOR_INDIAN_CITIES,
    search_indian_cities,
    fetch_live_air_quality,
    get_aqi_category_info
)
from src.health_advisory import get_advisory_by_category

st.set_page_config(
    page_title="Live AQI Details | AirWatch India",
    page_icon="🌐",
    layout="wide"
)

# Load styling
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🌐 City Live Air Quality Deep-Dive")
st.markdown("Inspect real-time atmospheric measurements, pollutant distributions, and geographic monitoring stations.")

# City selector in sidebar
with st.sidebar:
    st.subheader("📍 Target City")
    city_names = list(MAJOR_INDIAN_CITIES.keys())
    default_city = st.session_state.get("selected_city", "Delhi")
    idx = city_names.index(default_city) if default_city in city_names else 0
    
    selected_city = st.selectbox("Select Indian City:", city_names, index=idx)
    
    # Custom search
    q = st.text_input("Or Search Indian Location:", placeholder="e.g. Nagpur...")
    if q:
        matches = search_indian_cities(q, max_results=3)
        if matches:
            for m in matches:
                if st.button(f"📌 {m['name']} ({m['state']})", key=f"p1_search_{m['name']}"):
                    st.session_state.selected_city = m["name"]
                    st.session_state.selected_lat = m["lat"]
                    st.session_state.selected_lon = m["lon"]
                    st.session_state.selected_state = m["state"]
                    st.rerun()

    if selected_city in MAJOR_INDIAN_CITIES:
        st.session_state.selected_city = selected_city
        st.session_state.selected_lat = MAJOR_INDIAN_CITIES[selected_city]["lat"]
        st.session_state.selected_lon = MAJOR_INDIAN_CITIES[selected_city]["lon"]
        st.session_state.selected_state = MAJOR_INDIAN_CITIES[selected_city]["state"]

    if st.button("🔄 Force Refresh Data", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()

lat = st.session_state.get("selected_lat", 28.6139)
lon = st.session_state.get("selected_lon", 77.2090)
city = st.session_state.get("selected_city", "Delhi")
state = st.session_state.get("selected_state", "Delhi NCT")

with st.spinner(f"Querying atmospheric sensors for {city}..."):
    data = fetch_live_air_quality(lat, lon, city)

if data.get("status") == "ERROR":
    st.error(f"Data Fetch Error: {data.get('error_message')}")
    st.stop()

aqi = data.get("indian_aqi")
category = data.get("indian_category")
cat_info = data.get("category_info", {})
dominant_pol = data.get("dominant_pollutant", "PM2.5")
pollutants = data.get("pollutants", {})
sub_indices = data.get("sub_indices", {})
timestamp = data.get("timestamp")
source = data.get("source")

# Metadata Bar
st.markdown(
    f"""
    <div class="info-strip">
        <span>📍 <strong>{city}, {state}</strong> (Coordinates: {lat:.4f}°N, {lon:.4f}°E)</span>
        <span>🕒 Latest Available Reading: <strong>{timestamp}</strong></span>
        <span>📡 External Provider: <strong>{source}</strong></span>
    </div>
    """,
    unsafe_allow_html=True
)

# Gauge Chart and Geographic Location Row
col_gauge, col_map = st.columns([1.1, 1])

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi if aqi is not None else 0,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>CPCB Indian AQI — {city}</b><br><span style='font-size:16px;color:{cat_info.get('color')}'>{category} (Dominant: {dominant_pol})</span>", 'font': {'size': 20}},
        number={'suffix': "", 'font': {'size': 44, 'color': cat_info.get('color', '#0f766e')}},
        gauge={
            'axis': {'range': [0, 500], 'tickwidth': 1, 'tickcolor': "#334155"},
            'bar': {'color': cat_info.get('color', "#0f766e")},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#cbd5e1",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(0, 176, 80, 0.25)'},
                {'range': [51, 100], 'color': 'rgba(146, 208, 80, 0.25)'},
                {'range': [101, 200], 'color': 'rgba(255, 192, 0, 0.25)'},
                {'range': [201, 300], 'color': 'rgba(255, 102, 0, 0.25)'},
                {'range': [301, 400], 'color': 'rgba(255, 0, 0, 0.25)'},
                {'range': [401, 500], 'color': 'rgba(127, 0, 0, 0.25)'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.75,
                'value': aqi if aqi is not None else 0
            }
        }
    ))
    fig_gauge.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_map:
    map_df = pd.DataFrame([{
        "lat": lat,
        "lon": lon,
        "city": city,
        "aqi": aqi
    }])
    st.markdown(f"##### 🗺️ Geographic Monitoring Coordinate ({lat}°, {lon}°)")
    st.map(map_df, latitude="lat", longitude="lon", size=30, zoom=9)

st.markdown("---")

# Sub-index breakdown and international comparison
col_breakdown, col_intl = st.columns([1.4, 1])

with col_breakdown:
    st.subheader("📊 Pollutant Concentrations & CPCB Sub-Indices")
    table_rows = []
    for p_name, p_data in pollutants.items():
        v = p_data.get("value")
        u = p_data.get("unit")
        s = p_data.get("sub_index")
        c_info = get_aqi_category_info(s) if s is not None else {}
        table_rows.append({
            "Pollutant": p_name,
            "Concentration": f"{v:.2f} {u}" if v is not None else "Not Available",
            "CPCB Sub-Index": int(round(s)) if s is not None else "N/A",
            "Category": c_info.get("name", "N/A")
        })
    df_table = pd.DataFrame(table_rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

with col_intl:
    st.subheader("🌐 Global Index Comparison")
    us_val = data.get("us_aqi")
    eu_val = data.get("european_aqi")
    
    st.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px;">
            <div style="margin-bottom: 12px;">
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 700;">INDIAN CPCB NAQI</span><br>
                <span style="font-size: 1.8rem; font-weight: 800; color: {cat_info.get('color')};">{aqi}</span>
                <span style="font-size: 0.9rem; color: #475569;">({category})</span>
            </div>
            <div style="margin-bottom: 12px;">
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 700;">UNITED STATES EPA AQI</span><br>
                <span style="font-size: 1.8rem; font-weight: 800; color: #0284c7;">{us_val if us_val is not None else 'N/A'}</span>
                <span style="font-size: 0.85rem; color: #64748b;">(US EPA Breakpoint Scale)</span>
            </div>
            <div>
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 700;">EUROPEAN EAQI</span><br>
                <span style="font-size: 1.8rem; font-weight: 800; color: #0d9488;">{eu_val if eu_val is not None else 'N/A'}</span>
                <span style="font-size: 0.85rem; color: #64748b;">(European Environment Agency)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.caption("ℹ️ **Why indices differ:** CPCB India, US EPA, and European EAQI utilize distinct averaging periods, breakpoint thresholds, and criteria weights adapted to regional health baselines.")

st.markdown("---")

# Full 72-Hour Interactive Chart
st.subheader("📈 Multi-Pollutant 72-Hour Time-Series (History & Forecast)")
hourly_df = data.get("hourly_df")
if hourly_df is not None and not hourly_df.empty:
    selected_pols = st.multiselect(
        "Select Pollutants to Plot:",
        options=["pm2_5", "pm10", "no2", "so2", "o3", "us_aqi"],
        default=["pm2_5", "pm10", "no2"],
        format_func=lambda x: {"pm2_5": "PM2.5", "pm10": "PM10", "no2": "NO₂", "so2": "SO₂", "o3": "O₃", "us_aqi": "US AQI"}.get(x, x)
    )

    if selected_pols:
        fig_multi = px.line(
            hourly_df,
            x="time",
            y=selected_pols,
            labels={"time": "Date & Time (IST)", "value": "Concentration (µg/m³)"},
            template="plotly_white",
            title=f"Atmospheric Dynamics for {city} (72 Hours)"
        )
        fig_multi.update_layout(height=420, hovermode="x unified", legend_title="Trace")
        st.plotly_chart(fig_multi, use_container_width=True)
    else:
        st.info("Select at least one pollutant to render the time-series graph.")
else:
    st.warning("Hourly time-series data is currently pending from the provider.")

st.markdown("---")
st.caption("Notice: AirWatch India receives and visualizes data from external monitoring providers (Copernicus CAMS & Open-Meteo). It does not measure physical air quality on-site.")
