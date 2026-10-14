"""
src/data_processing.py
Dataset management for historical analysis and offline ML validation.
Handles data/city_day.csv with safe fallbacks, caching, and analytics aggregations.
"""

import os
import zipfile
import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def load_historical_data() -> pd.DataFrame:
    """
    Loads historical Indian city air quality dataset.
    Searches in:
    1. data/city_day.csv
    2. city_day.csv/city_day.csv
    3. city_day.csv.zip (auto-extract)
    """
    candidates = [
        os.path.join("data", "city_day.csv"),
        os.path.join("city_day.csv", "city_day.csv"),
        "city_day.csv"
    ]

    for path in candidates:
        if os.path.exists(path) and os.path.isfile(path):
            try:
                df = pd.read_csv(path)
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                return df
            except Exception:
                continue

    # Try extracting zip if file not found
    zip_path = "city_day.csv.zip"
    if os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall("data")
            extracted_path = os.path.join("data", "city_day.csv")
            if os.path.exists(extracted_path):
                df = pd.read_csv(extracted_path)
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                return df
        except Exception:
            pass

    return pd.DataFrame()


def get_available_cities(df: pd.DataFrame) -> list:
    """Returns sorted list of available cities in historical dataset."""
    if df.empty or "City" not in df.columns:
        return []
    return sorted(df["City"].dropna().unique().tolist())


def get_city_historical_stats(df: pd.DataFrame, city_name: str) -> dict:
    """
    Computes summary metrics and yearly averages for a given city.
    """
    if df.empty or "City" not in df.columns:
        return {}

    cdf = df[df["City"] == city_name].copy()
    if cdf.empty:
        return {}

    valid_aqi = cdf["AQI"].dropna()
    if valid_aqi.empty:
        return {}

    cdf["Year"] = cdf["Date"].dt.year
    yearly = cdf.groupby("Year")["AQI"].mean().reset_index()

    stats = {
        "city": city_name,
        "total_records": len(cdf),
        "valid_aqi_records": len(valid_aqi),
        "min_date": cdf["Date"].min().strftime("%Y-%m-%d") if not cdf["Date"].isna().all() else "N/A",
        "max_date": cdf["Date"].max().strftime("%Y-%m-%d") if not cdf["Date"].isna().all() else "N/A",
        "mean_aqi": round(float(valid_aqi.mean()), 1),
        "median_aqi": round(float(valid_aqi.median()), 1),
        "max_aqi": round(float(valid_aqi.max()), 1),
        "min_aqi": round(float(valid_aqi.min()), 1),
        "yearly_trend": yearly
    }
    return stats


def get_multi_city_historical_comparison(df: pd.DataFrame, cities: list) -> pd.DataFrame:
    """
    Returns aggregated mean AQI and pollutant concentrations for selected cities.
    """
    if df.empty or not cities:
        return pd.DataFrame()

    sub = df[df["City"].isin(cities)].copy()
    if sub.empty:
        return pd.DataFrame()

    agg_cols = ["AQI", "PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
    existing_cols = [c for c in agg_cols if c in sub.columns]

    comp = sub.groupby("City")[existing_cols].mean().round(1).reset_index()
    return comp
