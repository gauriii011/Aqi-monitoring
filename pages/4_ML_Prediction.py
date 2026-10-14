"""
pages/4_ML_Prediction.py
Machine Learning AQI Inference & Model Intelligence Portal for AirWatch India.
Integrates trained RandomForestRegressor (aqi_model.pkl), provides live-to-ML inference,
interactive 12-feature simulator, historical ground-truth validation, and feature importance.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

from src.prediction import (
    load_ml_model,
    predict_aqi,
    predict_from_live_data,
    get_feature_importances,
    MODEL_METRICS,
    HISTORICAL_MEDIANS
)
from src.live_aqi import MAJOR_INDIAN_CITIES, fetch_live_air_quality, get_aqi_category_info
from src.health_advisory import get_advisory_by_category
from src.data_processing import load_historical_data

st.set_page_config(
    page_title="ML Prediction Engine | AirWatch India",
    page_icon="🤖",
    layout="wide"
)

# Load styling
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🤖 Machine Learning AQI Prediction Engine")
st.markdown("Inference pipeline leveraging the pre-trained **Random Forest Regressor** model trained on CPCB multi-station air quality data.")

# Load model
model, feature_columns, err_msg = load_ml_model()

if err_msg or model is None:
    st.error(f"⚠️ Model Loading Error: {err_msg}")
    st.info("Please ensure 'aqi_model.pkl' and 'feature_columns.pkl' are present in the project root directory.")
    st.stop()

# Model Architecture & Verified Evaluation Banner
with st.expander("ℹ️ Inspect Model Architecture & Verified College Evaluation Metrics", expanded=True):
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Algorithm", MODEL_METRICS["algorithm"], delta=f"{MODEL_METRICS['n_estimators']} Estimators")
    with col_m2:
        st.metric("Verified R² Score", f"{MODEL_METRICS['r2_score']:.4f}", delta="90.96% Variance (Notebook Cell 20)")
    with col_m3:
        st.metric("Verified MAE", f"{MODEL_METRICS['mae']:.2f} AQI", delta="Mean Absolute Error")
    with col_m4:
        st.metric("Training Dataset", "city_day.csv", delta="80/20 Train-Test Split")

    st.caption(
        "📝 **Verification Note for BCS Project Review:** The user's notebook validation recorded an **R² score of 0.9096** "
        "and **MAE of 20.55** on the 20% test split, demonstrating strong predictive accuracy compared to the initial baseline observation (R² ~0.8803, MAE ~19.96)."
    )

st.markdown("<br>", unsafe_allow_html=True)

# Three Modes
tab_live_bridge, tab_simulator, tab_historical_test, tab_importance = st.tabs([
    "⚡ Mode 1: Live City Telemetry → ML Predictor",
    "🎛️ Mode 2: Interactive 12-Feature Simulator",
    "🧪 Mode 3: Historical Dataset Ground-Truth Tester",
    "📈 Mode 4: Feature Importance & Explainability"
])

# ==============================================================================
# MODE 1: LIVE TELEMETRY TO ML BRIDGE
# ==============================================================================
with tab_live_bridge:
    st.subheader("⚡ Live City Telemetry to ML Predictor Bridge")
    st.markdown("Pulls real-time pollutant observations for an Indian city, adapts units (e.g. CO in mg/m³), feeds them into the trained Random Forest model, and contrasts the **ML Prediction** with the **Statutory CPCB Calculated AQI**.")

    col_lb1, col_lb2 = st.columns([1, 2])
    with col_lb1:
        city_options = list(MAJOR_INDIAN_CITIES.keys())
        default_city = st.session_state.get("selected_city", "Delhi")
        chosen_city = st.selectbox("Select Target City:", city_options, index=city_options.index(default_city) if default_city in city_options else 0, key="ml_live_city")
        meta = MAJOR_INDIAN_CITIES[chosen_city]
        
        live_data = fetch_live_air_quality(meta["lat"], meta["lon"], chosen_city)

    with col_lb2:
        if live_data.get("status") == "LIVE":
            live_aqi = live_data.get("indian_aqi")
            live_cat = live_data.get("indian_category")
            live_pols = live_data.get("pollutants", {})

            # Feed into ML model
            ml_result = predict_from_live_data(live_pols)
            
            if ml_result.get("success"):
                pred_aqi = ml_result["predicted_aqi"]
                pred_cat = ml_result["category"]
                pred_info = ml_result["category_info"]
                diff = round(pred_aqi - live_aqi, 1)

                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.metric(
                        label="🏛️ CPCB Statutory AQI",
                        value=live_aqi,
                        delta=f"Category: {live_cat}",
                        delta_color="off"
                    )
                with col_res2:
                    st.metric(
                        label="🤖 Random Forest Predicted AQI",
                        value=pred_aqi,
                        delta=f"Deviation: {diff:+} AQI",
                        delta_color="inverse" if abs(diff) > 25 else "normal"
                    )
                with col_res3:
                    st.metric(
                        label="🏷️ Predicted Category",
                        value=pred_cat,
                        delta=f"{ml_result['imputed_count']} Features Imputed"
                    )

                st.markdown(
                    f"""
                    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 14px; margin-top: 14px;">
                        <strong>🔍 Scientific Comparison Insight:</strong><br>
                        • <strong>Statutory CPCB AQI ({live_aqi}):</strong> Uses a regulatory <em>maximum sub-index breakpoint</em> formula dictated by the dominant pollutant ({live_data.get('dominant_pollutant')}).<br>
                        • <strong>Machine Learning AQI ({pred_aqi}):</strong> Uses a non-linear regression ensemble that integrates simultaneous interactions across all pollutants simultaneously.<br>
                        • <strong>Data Imputation Notice:</strong> The live atmospheric API measures PM2.5, PM10, NO2, SO2, CO, O3, and NH3. Secondary volatile organics (Benzene, Toluene, Xylene) are imputed with historical dataset medians for ML inference.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error(ml_result.get("error"))
        else:
            st.error("Live telemetry unavailable for selected city.")

# ==============================================================================
# MODE 2: INTERACTIVE 12-FEATURE SIMULATOR
# ==============================================================================
with tab_simulator:
    st.subheader("🎛️ Interactive Pollutant Scenario Simulator")
    st.markdown("Adjust individual pollutant concentrations to simulate custom atmospheric conditions and predict the corresponding AQI.")

    # Preset scenarios
    st.markdown("##### ⚡ Quick Scenarios:")
    col_pre1, col_pre2, col_pre3, col_pre4 = st.columns(4)
    
    preset_values = None
    with col_pre1:
        if st.button("🌿 Clean Post-Monsoon Day", use_container_width=True):
            preset_values = {"PM2.5": 20.0, "PM10": 35.0, "NO": 5.0, "NO2": 15.0, "NOx": 18.0, "NH3": 8.0, "CO": 0.4, "SO2": 6.0, "O3": 25.0, "Benzene": 0.5, "Toluene": 1.2, "Xylene": 0.4}
    with col_pre2:
        if st.button("🏙️ Typical Urban Day", use_container_width=True):
            preset_values = {"PM2.5": 65.0, "PM10": 120.0, "NO": 18.0, "NO2": 32.0, "NOx": 35.0, "NH3": 20.0, "CO": 1.2, "SO2": 14.0, "O3": 45.0, "Benzene": 2.5, "Toluene": 6.0, "Xylene": 1.8}
    with col_pre3:
        if st.button("🌫️ Winter Inversion Smog", use_container_width=True):
            preset_values = {"PM2.5": 195.0, "PM10": 320.0, "NO": 45.0, "NO2": 68.0, "NOx": 80.0, "NH3": 38.0, "CO": 2.8, "SO2": 24.0, "O3": 35.0, "Benzene": 6.5, "Toluene": 14.0, "Xylene": 4.5}
    with col_pre4:
        if st.button("🏭 Industrial Hotspot Episode", use_container_width=True):
            preset_values = {"PM2.5": 280.0, "PM10": 450.0, "NO": 65.0, "NO2": 110.0, "NOx": 130.0, "NH3": 55.0, "CO": 4.5, "SO2": 65.0, "O3": 75.0, "Benzene": 12.0, "Toluene": 25.0, "Xylene": 8.0}

    # Sliders
    user_inputs = {}
    col_s1, col_s2, col_s3 = st.columns(3)

    configs = [
        ("PM2.5", 0.0, 500.0, 50.0, "µg/m³"),
        ("PM10", 0.0, 600.0, 95.0, "µg/m³"),
        ("NO", 0.0, 150.0, 10.0, "µg/m³"),
        ("NO2", 0.0, 200.0, 22.0, "µg/m³"),
        ("NOx", 0.0, 250.0, 25.0, "µg/m³"),
        ("NH3", 0.0, 200.0, 16.0, "µg/m³"),
        ("CO", 0.0, 25.0, 1.0, "mg/m³ (Note unit)"),
        ("SO2", 0.0, 150.0, 10.0, "µg/m³"),
        ("O3", 0.0, 250.0, 32.0, "µg/m³"),
        ("Benzene", 0.0, 50.0, 1.5, "µg/m³"),
        ("Toluene", 0.0, 100.0, 3.5, "µg/m³"),
        ("Xylene", 0.0, 50.0, 1.0, "µg/m³")
    ]

    for idx, (f_name, min_v, max_v, def_v, unit_str) in enumerate(configs):
        target_col = col_s1 if idx % 3 == 0 else (col_s2 if idx % 3 == 1 else col_s3)
        val = preset_values.get(f_name, def_v) if preset_values else def_v
        with target_col:
            user_inputs[f_name] = st.slider(
                f"{f_name} ({unit_str})",
                min_value=min_v,
                max_value=max_v,
                value=float(val),
                step=0.1 if f_name in ["CO", "Benzene", "Toluene", "Xylene"] else 1.0,
                key=f"slider_{f_name}"
            )

    st.markdown("---")
    
    if st.button("🔮 Predict AQI from Simulator", type="primary", use_container_width=True):
        sim_res = predict_aqi(user_inputs, use_medians_for_missing=False)
        if sim_res.get("success"):
            sim_aqi = sim_res["predicted_aqi"]
            sim_cat = sim_res["category"]
            sim_info = sim_res["category_info"]
            advisory = get_advisory_by_category(sim_cat)

            st.markdown(
                f"""
                <div style="background: #ffffff; border-radius: 14px; border: 2px solid {sim_info.get('color')}; padding: 22px; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.06); margin-top: 15px;">
                    <span style="font-size: 0.9rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Simulated AQI Result</span>
                    <div style="font-size: 4rem; font-weight: 800; color: {sim_info.get('color')}; line-height: 1.1; margin: 6px 0;">
                        {sim_aqi}
                    </div>
                    <div style="background-color: {sim_info.get('color')}; color: {sim_info.get('text_color')}; padding: 6px 20px; border-radius: 999px; display: inline-block; font-weight: 700; font-size: 1.2rem; margin-bottom: 12px;">
                        {sim_cat}
                    </div>
                    <p style="font-size: 1.05rem; color: #1e293b; max-width: 700px; margin: 0 auto;">
                        <strong>Health Advisory:</strong> {advisory.get('health_impact')}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.error(sim_res.get("error"))

# ==============================================================================
# MODE 3: HISTORICAL DATASET GROUND-TRUTH TESTER
# ==============================================================================
with tab_historical_test:
    st.subheader("🧪 Historical Dataset Ground-Truth Tester")
    st.markdown("Select an actual date and city from `city_day.csv` to run the model against real verified ground-truth AQI measurements recorded by CPCB stations.")

    df_hist = load_historical_data()
    if df_hist.empty:
        st.warning("Historical dataset 'city_day.csv' is missing or unreadable.")
    else:
        df_valid = df_hist.dropna(subset=["AQI"]).copy()
        test_cities = sorted(df_valid["City"].unique().tolist())
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            test_city = st.selectbox("Select Historical City:", test_cities, key="hist_test_city")
            city_rows = df_valid[df_valid["City"] == test_city]
            test_dates = sorted(city_rows["Date"].dt.strftime("%Y-%m-%d").unique().tolist(), reverse=True)
            
        with col_t2:
            test_date = st.selectbox("Select Observation Date:", test_dates[:100], key="hist_test_date")
            selected_row = city_rows[city_rows["Date"].dt.strftime("%Y-%m-%d") == test_date].iloc[0]

        actual_aqi = selected_row["AQI"]
        actual_bucket = selected_row.get("AQI_Bucket", "N/A")

        # Run prediction on this historical row
        row_dict = {col: selected_row[col] for col in feature_columns if col in selected_row}
        pred_hist_res = predict_aqi(row_dict, use_medians_for_missing=True)

        if pred_hist_res.get("success"):
            pred_hist_aqi = pred_hist_res["predicted_aqi"]
            hist_cat = pred_hist_res["category"]
            error = round(abs(pred_hist_aqi - actual_aqi), 2)
            pct_error = round((error / actual_aqi) * 100, 1)

            col_eval1, col_eval2, col_eval3, col_eval4 = st.columns(4)
            with col_eval1:
                st.metric("🎯 Recorded Ground Truth AQI", f"{actual_aqi:.1f}", delta=f"Bucket: {actual_bucket}")
            with col_eval2:
                st.metric("🤖 ML Model Predicted AQI", f"{pred_hist_aqi:.1f}", delta=f"Category: {hist_cat}")
            with col_eval3:
                st.metric("📏 Absolute Error", f"{error} AQI", delta="Difference")
            with col_eval4:
                st.metric("📊 Percentage Error", f"{pct_error}%", delta="Relative Margin")

            st.markdown("##### 📋 Input Features for Selected Historical Day:")
            feature_display_df = pd.DataFrame([row_dict]).T.reset_index()
            feature_display_df.columns = ["Pollutant Feature", "Recorded Value"]
            st.dataframe(feature_display_df, use_container_width=True, hide_index=True)

# ==============================================================================
# MODE 4: FEATURE IMPORTANCE & EXPLAINABILITY
# ==============================================================================
with tab_importance:
    st.subheader("📈 Random Forest Feature Importance & Model Explainability")
    st.markdown("Inspect which pollutants exercise the greatest mathematical weight in determining the AQI prediction within the ensemble trees.")

    df_fi = get_feature_importances(model, feature_columns)
    
    if not df_fi.empty:
        fig_fi = px.bar(
            df_fi,
            x="Percentage",
            y="Feature",
            orientation="h",
            text="Percentage",
            color="Percentage",
            color_continuous_scale="teal",
            template="plotly_white",
            title="Relative Feature Importance (%) in Random Forest Regressor"
        )
        fig_fi.update_layout(yaxis=dict(autorange="reversed"), height=420)
        fig_fi.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig_fi, use_container_width=True)

        st.markdown(
            """
            **🔬 Academic Takeaway for Mini-Project Viva:**
            1. **PM2.5 Dominance:** Particulate Matter 2.5 contributes **~49.1%** of overall decision splits, aligning directly with medical evidence that fine respirable particulates drive severe air toxicity in Indian urban environments.
            2. **Carbon Monoxide (CO):** Represents **~36.8%** of model split importance, acting as a powerful proxy for combustion intensity and vehicular exhaust.
            3. **Coarse Particulates (PM10) & Nitrogen Oxides (NO/NOx):** Provide secondary split refinement.
            """
        )

st.markdown("---")
st.caption("College Mini-Project | AirWatch India | Machine Learning Pipeline powered by Scikit-learn Random Forest Regression")
