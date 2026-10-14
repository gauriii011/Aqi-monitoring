"""
pages/2_City_Comparison.py
City Comparison & Analytics for AirWatch India.
Provides live multi-city rankings, side-by-side pollutant comparisons,
and historical offline dataset trends from city_day.csv.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

from src.live_aqi import (
    MAJOR_INDIAN_CITIES,
    fetch_live_air_quality,
    get_aqi_category_info
)
from src.data_processing import load_historical_data, get_multi_city_historical_comparison

st.set_page_config(
    page_title="City Comparison & Analytics | AirWatch India",
    page_icon="📊",
    layout="wide"
)

# Load styling
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📊 Indian City Air Quality Comparison & Analytics")
st.markdown("Analyze live atmospheric variations across Indian metropolises and evaluate historical multi-year records.")

# Two distinct tabs: Live Comparison vs Historical Analysis
tab_live, tab_historical = st.tabs([
    "⚡ Live Multi-City Comparison (Real-Time API)",
    "🏛️ Historical Long-Term Trends (CPCB 2015–2020 Dataset)"
])

# ==============================================================================
# TAB 1: LIVE MULTI-CITY COMPARISON
# ==============================================================================
with tab_live:
    st.subheader("⚡ Real-Time Multi-City Leaderboard & Pollutant Comparison")
    st.caption("Live data retrieved via Open-Meteo Atmospheric Assimilation. Calculated using official Indian CPCB NAQI standard.")

    # Selection of cities to compare
    all_cities = list(MAJOR_INDIAN_CITIES.keys())
    default_compare = ["Delhi", "Mumbai", "Pune", "Bengaluru", "Kolkata", "Chennai", "Hyderabad"]
    
    selected_compare = st.multiselect(
        "Choose Indian Cities to Compare:",
        options=all_cities,
        default=default_compare,
        help="Select 2 or more cities to view live comparative rankings"
    )

    if len(selected_compare) < 2:
        st.warning("Please select at least 2 cities to generate comparative visualizations.")
    else:
        # Fetch live data for selected cities
        live_rows = []
        with st.spinner("Fetching live atmospheric telemetry for selected cities..."):
            for c_name in selected_compare:
                meta = MAJOR_INDIAN_CITIES[c_name]
                d = fetch_live_air_quality(meta["lat"], meta["lon"], c_name)
                if d.get("status") == "LIVE":
                    pols = d.get("pollutants", {})
                    live_rows.append({
                        "City": c_name,
                        "State": meta["state"],
                        "Indian AQI": d.get("indian_aqi"),
                        "Category": d.get("indian_category"),
                        "Dominant Pollutant": d.get("dominant_pollutant"),
                        "PM2.5 (µg/m³)": pols.get("PM2.5", {}).get("value"),
                        "PM10 (µg/m³)": pols.get("PM10", {}).get("value"),
                        "NO2 (µg/m³)": pols.get("NO2", {}).get("value"),
                        "SO2 (µg/m³)": pols.get("SO2", {}).get("value"),
                        "CO (mg/m³)": pols.get("CO", {}).get("value"),
                        "O3 (µg/m³)": pols.get("O3", {}).get("value"),
                        "US AQI": d.get("us_aqi"),
                        "color": d.get("category_info", {}).get("color", "#0f766e")
                    })

        if live_rows:
            df_live_comp = pd.DataFrame(live_rows).sort_values("Indian AQI", ascending=True)

            # Leaderboard Summary Cards
            cleanest = df_live_comp.iloc[0]
            most_polluted = df_live_comp.iloc[-1]

            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.metric("🌿 Cleanest Selected City", f"{cleanest['City']} ({cleanest['Indian AQI']})", delta=cleanest['Category'], delta_color="normal")
            with col_c2:
                st.metric("🏭 Most Polluted Selected City", f"{most_polluted['City']} ({most_polluted['Indian AQI']})", delta=most_polluted['Category'], delta_color="inverse")
            with col_c3:
                st.metric("📊 Average Selected AQI", f"{df_live_comp['Indian AQI'].mean():.1f}", delta=f"{len(df_live_comp)} Cities Monitored")

            st.markdown("<br>", unsafe_allow_html=True)

            # Bar Chart: Indian AQI Comparison
            fig_aqi_bar = px.bar(
                df_live_comp,
                x="City",
                y="Indian AQI",
                color="Category",
                color_discrete_map={
                    "Good": "#00b050",
                    "Satisfactory": "#92d050",
                    "Moderately Polluted": "#ffc000",
                    "Poor": "#ff6600",
                    "Very Poor": "#ff0000",
                    "Severe": "#7f0000"
                },
                text="Indian AQI",
                title="Live Indian CPCB National AQI Comparison (Ranked Cleanest to Most Polluted)",
                template="plotly_white"
            )
            fig_aqi_bar.update_traces(textposition="outside")
            fig_aqi_bar.update_layout(height=400, yaxis_range=[0, max(df_live_comp["Indian AQI"].max() * 1.2, 100)])
            st.plotly_chart(fig_aqi_bar, use_container_width=True)

            # Multi-Pollutant Grouped Bar Chart
            st.markdown("##### 🧪 Particulate & Gaseous Pollutants Across Cities")
            pollutant_choice = st.selectbox(
                "Filter Specific Pollutant:",
                options=["PM2.5 (µg/m³)", "PM10 (µg/m³)", "NO2 (µg/m³)", "SO2 (µg/m³)", "O3 (µg/m³)"]
            )
            fig_p_bar = px.bar(
                df_live_comp,
                x="City",
                y=pollutant_choice,
                color="City",
                text=pollutant_choice,
                template="plotly_white",
                title=f"Live {pollutant_choice} Comparison Across Selected Cities"
            )
            fig_p_bar.update_traces(textposition="outside")
            fig_p_bar.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig_p_bar, use_container_width=True)

            # Data Table
            st.markdown("##### 📋 Summary Telemetry Table")
            st.dataframe(
                df_live_comp.drop(columns=["color"]),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.error("Failed to retrieve live telemetry for selected cities.")

# ==============================================================================
# TAB 2: HISTORICAL OFFLINE DATASET ANALYSIS (city_day.csv)
# ==============================================================================
with tab_historical:
    st.subheader("🏛️ Historical Dataset Analysis (CPCB city_day.csv: 2015–2020)")
    st.info("📌 **Distinction Note:** These analyses reflect historical offline records from CPCB monitoring stations across India between 2015 and 2020. They are preserved for research and ML model context, separate from current live observations.")

    df_hist = load_historical_data()

    if df_hist.empty:
        st.warning("Historical dataset 'city_day.csv' could not be loaded. Please ensure data/city_day.csv is present.")
    else:
        hist_cities = sorted(df_hist["City"].dropna().unique().tolist())
        
        col_h1, col_h2 = st.columns([1, 2])
        with col_h1:
            selected_hist_cities = st.multiselect(
                "Select Historical Cities to Compare:",
                options=hist_cities,
                default=["Delhi", "Bengaluru", "Mumbai", "Kolkata", "Ahmedabad"] if all(c in hist_cities for c in ["Delhi", "Bengaluru", "Mumbai", "Kolkata", "Ahmedabad"]) else hist_cities[:4]
            )

        if selected_hist_cities:
            comp_hist = get_multi_city_historical_comparison(df_hist, selected_hist_cities)
            
            with col_h2:
                st.markdown("##### Historical Mean Pollutant Concentrations (2015–2020 Average)")
                st.dataframe(comp_hist, use_container_width=True, hide_index=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Multi-Year Annual Trend
            st.markdown("##### 📅 Multi-Year Annual AQI Trends")
            df_sub = df_hist[df_hist["City"].isin(selected_hist_cities)].copy()
            df_sub["Year"] = df_sub["Date"].dt.year
            df_yearly = df_sub.groupby(["City", "Year"])["AQI"].mean().reset_index()

            fig_trend = px.line(
                df_yearly,
                x="Year",
                y="AQI",
                color="City",
                markers=True,
                template="plotly_white",
                title="Historical Annual Average AQI (2015–2020)"
            )
            fig_trend.update_layout(height=400, hovermode="x unified")
            st.plotly_chart(fig_trend, use_container_width=True)

            # Distribution of AQI Buckets
            if "AQI_Bucket" in df_sub.columns:
                st.markdown("##### 🍩 Historical AQI Category Distribution")
                bucket_counts = df_sub.groupby(["City", "AQI_Bucket"]).size().reset_index(name="Days")
                fig_bucket = px.bar(
                    bucket_counts,
                    x="City",
                    y="Days",
                    color="AQI_Bucket",
                    title="Historical Days Recorded in Each AQI Category",
                    template="plotly_white",
                    barmode="stack",
                    color_discrete_map={
                        "Good": "#00b050",
                        "Satisfactory": "#92d050",
                        "Moderate": "#ffc000",
                        "Poor": "#ff6600",
                        "Very Poor": "#ff0000",
                        "Severe": "#7f0000"
                    }
                )
                fig_bucket.update_layout(height=380)
                st.plotly_chart(fig_bucket, use_container_width=True)

st.markdown("---")
st.caption("College Mini-Project | AirWatch India | Strict separation between Live Atmospheric Streams and Historical Records")
