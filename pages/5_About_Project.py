"""
pages/5_About_Project.py
College Project Methodology, System Architecture & Technical Documentation.
Designed specifically for Third-Year BCS College Mini-Project presentation,
viva defense, and evaluator review.
"""

import streamlit as st
import os

st.set_page_config(
    page_title="About & Project Methodology | AirWatch India",
    page_icon="ℹ️",
    layout="wide"
)

# Load styling
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("ℹ️ Project Methodology & Technical Documentation")
st.markdown("Academic documentation and architecture overview for **AirWatch India — Live AQI Monitoring & Health Advisory System** (BCS 3rd Year Mini-Project).")

# Quick Project Metadata Card
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; border-radius: 14px; padding: 22px 28px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(0,0,0,0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <span style="color: #2dd4bf; font-weight: 700; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;">Bachelor of Computer Science (BCS) — Year III Mini-Project</span>
                <h2 style="color: #ffffff; margin: 6px 0; font-size: 1.8rem; font-weight: 800;">AirWatch India</h2>
                <p style="color: #94a3b8; margin: 0; font-size: 0.95rem;">Live Air Quality Telemetry, Statutory CPCB NAQI Engine, and Machine Learning Health Advisory System</p>
            </div>
            <div style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 12px 18px; text-align: right;">
                <span style="font-size: 0.8rem; color: #94a3b8;">Academic Session</span><br>
                <strong style="color: #ffffff; font-size: 1.05rem;">2025 – 2026</strong>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Table of Contents Tabs
tab_overview, tab_architecture, tab_ml_pipeline, tab_tech_stack, tab_limitations, tab_viva = st.tabs([
    "🎯 Project Overview",
    "🏗️ System Architecture & Data Flow",
    "🤖 Machine Learning Methodology",
    "💻 Technology Stack",
    "⚠️ Limitations & Future Scope",
    "🎓 BCS Viva Prep Q&A"
])

# ==============================================================================
# TAB 1: PROJECT OVERVIEW
# ==============================================================================
with tab_overview:
    col_ov1, col_ov2 = st.columns(2)

    with col_ov1:
        st.subheader("1. Problem Statement")
        st.markdown(
            """
            Air pollution represents one of the most critical public health emergencies across Indian cities. 
            Rapid urbanization, vehicular emissions, seasonal agricultural residue burning (stubble burning), 
            and industrial effluents frequently elevate ambient concentrations of fine particulate matter ($PM_{2.5}$ and $PM_{10}$) 
            to hazardous levels.
            
            However, existing public reporting tools often suffer from:
            - **Opaque Scales:** Displaying foreign AQI scales (e.g. US EPA) without converting to official Indian CPCB standards.
            - **Delayed Information:** Lack of actionable, personal health guidance adapted to specific vulnerable demographics (asthma patients, children, elderly).
            - **No Machine Learning Integration:** Inability to simulate custom pollutant scenarios or forecast environmental risks.
            """
        )

        st.subheader("2. Project Motivation")
        st.markdown(
            """
            As a computer science student in India, building an end-to-end, data-driven software platform provides 
            a tangible solution to bridge environmental sensor data with community health decisions. 
            The motivation is to combine **real-time atmospheric APIs**, **regulatory environmental mathematics**, 
            and **machine learning intelligence** into a responsive, accessible web application.
            """
        )

    with col_ov2:
        st.subheader("3. Core Objectives")
        st.markdown(
            """
            1. **Real-Time Data Integration:** Connect to reliable atmospheric telemetry (Copernicus CAMS & Open-Meteo) for major Indian cities with zero fabricated numbers.
            2. **Statutory CPCB Compliance:** Faithfully implement the official Indian National Air Quality Index (NAQI) mathematical sub-index piecewise breakpoint equations.
            3. **India-Only Geocoding:** Validate user queries to strictly isolate locations within the Republic of India and prevent ambiguous global collisions.
            4. **Machine Learning Deployment:** Serve a trained Random Forest Regressor to provide instant predictive modeling, scenario simulation, and explainability.
            5. **Dynamic Health Advisories:** Offer tailored health precautions for vulnerable groups, indoor air management, and respiratory protective gear (N95/N99).
            """
        )

# ==============================================================================
# TAB 2: SYSTEM ARCHITECTURE & DATA FLOW
# ==============================================================================
with tab_architecture:
    st.subheader("System Architecture & Data Pipelines")
    
    st.markdown("##### 1. Live Telemetry Pipeline Flow:")
    st.markdown(
        """
        ```
        +----------------------------+
        |   Open-Meteo / CAMS API    |  --> Real-time atmospheric observations (PM2.5, PM10, NO2, SO2, CO, O3, NH3)
        +----------------------------+
                      │
                      ▼
        +----------------------------+
        | Location & Data Validation |  --> Strict India bbox / country_code == 'IN' / Unit standardization
        +----------------------------+
                      │
                      ▼
        +----------------------------+
        |  CPCB NAQI Sub-Index Engine|  --> Piecewise linear interpolation: I = I_low + ((I_high - I_low)/(B_high - B_low))*(C - B_low)
        +----------------------------+
                      │
                      ▼
        +----------------------------+
        | Health Advisory & UI Layer |  --> Dynamic category color, sensitive group warnings, Plotly time-series
        +----------------------------+
        ```
        """
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 2. Machine Learning Training & Inference Pipeline Flow:")
    st.markdown(
        """
        ```
        +----------------------------+
        | Historical Dataset (CPCB)  |  --> city_day.csv (29,531 daily records from Indian monitoring stations)
        +----------------------------+
                      │
                      ▼
        +----------------------------+
        | Data Preprocessing         |  --> Drop non-predictive columns, remove rows with missing AQI, 12 feature columns
        +----------------------------+
                      │
                      ▼
        +----------------------------+
        | Train-Test Split & Train   |  --> 80% Train, 20% Test (RandomForestRegressor: 100 trees, random_state=42)
        +----------------------------+
                      │
                      ▼
        +----------------------------+
        | Model Evaluation           |  --> Verified MAE: 20.55 | Verified R²: 0.9096 (90.96% variance explained)
        +----------------------------+
                      │
                      ▼
        +----------------------------+
        | Serialization & Deployment |  --> joblib.dump() -> aqi_model.pkl & feature_columns.pkl
        +----------------------------+
                      │
                      ▼
        +----------------------------+
        | Real-Time & Sim Inference  |  --> Streamlit Web Interface (Live Telemetry Bridge & 12-Feature Simulator)
        +----------------------------+
        ```
        """
    )

# ==============================================================================
# TAB 3: MACHINE LEARNING METHODOLOGY
# ==============================================================================
with tab_ml_pipeline:
    st.subheader("Machine Learning Workflow & Metrics Verification")

    st.markdown(
        """
        ### Dataset: `city_day.csv`
        - **Source:** Central Pollution Control Board (CPCB) official continuous ambient air quality monitoring stations (CAAQMS).
        - **Total Records:** 29,531 daily observations across 26 major Indian cities (2015 to 2020).
        - **Target Variable ($y$):** Recorded Indian Air Quality Index (`AQI`).
        - **Input Features ($X$):** 12 air pollutant concentrations:
          `PM2.5`, `PM10`, `NO`, `NO2`, `NOx`, `NH3`, `CO`, `SO2`, `O3`, `Benzene`, `Toluene`, `Xylene`.

        ### Model Selection: Random Forest Regressor
        - **Why Random Forest?**
          1. **Non-Linear Relationships:** Atmospheric pollutant interactions exhibit complex non-linear photochemical dependencies that linear regression cannot capture.
          2. **Ensemble Averaging:** 100 decision trees reduce variance and resist overfitting.
          3. **Robustness to Collinearity:** Handles correlated features (such as $NO$, $NO_2$, and $NO_x$) effectively.
          4. **Feature Importance:** Provides native Gini-based importance metrics for interpretability.

        ### Confirmed Evaluation Metrics:
        """
    )

    col_met1, col_met2, col_met3 = st.columns(3)
    with col_met1:
        st.markdown(
            """
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; text-align: center;">
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 700;">VERIFIED TEST R² SCORE</span>
                <h2 style="color: #0f766e; margin: 4px 0;">0.9096</h2>
                <span style="font-size: 0.85rem; color: #475569;">90.96% of variance explained</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_met2:
        st.markdown(
            """
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; text-align: center;">
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 700;">VERIFIED TEST MAE</span>
                <h2 style="color: #0f766e; margin: 4px 0;">20.55</h2>
                <span style="font-size: 0.85rem; color: #475569;">Mean Absolute Error (AQI points)</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_met3:
        st.markdown(
            """
            <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px; text-align: center;">
                <span style="font-size: 0.85rem; color: #64748b; font-weight: 700;">INITIAL BASELINE COMPARISON</span>
                <h2 style="color: #64748b; margin: 4px 0;">~0.8803</h2>
                <span style="font-size: 0.85rem; color: #475569;">Observed baseline (MAE ~19.96)</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# ==============================================================================
# TAB 4: TECHNOLOGY STACK
# ==============================================================================
with tab_tech_stack:
    st.subheader("Technologies & Libraries Used")

    tech_data = [
        {"Category": "Programming Language", "Technology": "Python 3.13", "Purpose": "Core programming, backend logic, and ML pipeline"},
        {"Category": "Web Framework", "Technology": "Streamlit 1.43", "Purpose": "Reactive, component-based interactive multi-page web application"},
        {"Category": "Machine Learning", "Technology": "Scikit-Learn 1.6 / 1.9", "Purpose": "RandomForestRegressor training, evaluation metrics, and inference"},
        {"Category": "Model Persistence", "Technology": "Joblib 1.6", "Purpose": "High-efficiency serialization of trained model weights and feature schema"},
        {"Category": "Data Manipulation", "Technology": "Pandas & NumPy", "Purpose": "DataFrame processing, numerical interpolation, missing value imputation"},
        {"Category": "Data Visualization", "Technology": "Plotly Express & Graph Objects", "Purpose": "Interactive time-series charts, comparative rankings, and gauge indicators"},
        {"Category": "External Telemetry API", "Technology": "Open-Meteo Air Quality & CAMS", "Purpose": "Real-time atmospheric assimilation with no API key requirement"},
        {"Category": "HTTP & Networking", "Technology": "Requests & Python-Dotenv", "Purpose": "REST API client, error handling, timeout recovery, environment configuration"},
        {"Category": "UI & Styling", "Technology": "Custom Modern CSS", "Purpose": "Clean responsive cards, subtle shadows, typography, and Indian CPCB color palette"}
    ]

    st.dataframe(pd.DataFrame(tech_data), use_container_width=True, hide_index=True)

# ==============================================================================
# TAB 5: LIMITATIONS & FUTURE SCOPE
# ==============================================================================
with tab_limitations:
    col_lim1, col_lim2 = st.columns(2)

    with col_lim1:
        st.subheader("⚠️ Project Limitations")
        st.markdown(
            """
            1. **Satellite vs Ground Sensor Resolution:** Open-Meteo utilizes European Copernicus Atmosphere Monitoring Service (CAMS) assimilation models. While highly accurate across broad areas, extreme localized hyper-local spikes (e.g. roadside garbage burning) may differ from on-site CPCB continuous sensors.
            2. **Volatile Organics in Live Feeds:** Modern meteorological satellite models measure criteria gases ($PM_{2.5}, PM_{10}, NO_2, SO_2, CO, O_3, NH_3$), but do not report trace Volatile Organic Compounds (Benzene, Toluene, Xylene). These are safely imputed with historical medians for ML inference.
            3. **Static Regression vs Time-Series Forecasting:** The current Random Forest model predicts AQI from contemporary pollutant values rather than temporal recurrence.
            """
        )

    with col_lim2:
        st.subheader("🚀 Future Scope & Enhancements")
        st.markdown(
            """
            1. **Deep Learning Temporal Forecasting:** Integrate LSTM (Long Short-Term Memory) or GRU recurrent neural networks to forecast 24-hour ahead AQI based on meteorological lag.
            2. **IoT Sensor Mesh Integration:** Allow Arduino / Raspberry Pi low-cost optical particulate sensors (PMS5003 / SDS011) to stream localized readings via MQTT.
            3. **Automated SMS & WhatsApp Alerts:** Implement Twilio / Telegram bot notifications when AQI exceeds 'Poor' (200+) in user's home locality.
            4. **Satellite Aerosol Optical Depth (AOD) Mapping:** Render geospatial Heatmaps of India using NASA MODIS / Sentinel-5P imagery.
            """
        )

# ==============================================================================
# TAB 6: BCS VIVA PREP Q&A
# ==============================================================================
with tab_viva:
    st.subheader("🎓 BCS Viva Defense Preparation Questions & Answers")
    st.markdown("Review these key conceptual questions frequently asked by external BCS project examiners:")

    viva_qa = [
        {
            "q": "Q1: What is the difference between US EPA AQI and Indian CPCB NAQI?",
            "a": "Indian CPCB NAQI uses 6 distinct categories (Good, Satisfactory, Moderately Polluted, Poor, Very Poor, Severe) and higher concentration breakpoints adapted to India's ambient baseline. For example, PM2.5 'Good' in India is 0-30 µg/m³, whereas US EPA 'Good' is 0-12.0 µg/m³. Applying US categories directly to Indian concentrations without conversion produces misleading classifications."
        },
        {
            "q": "Q2: How is the overall Indian AQI calculated from multiple pollutants?",
            "a": "According to official CPCB rules, each monitored pollutant concentration is converted into a sub-index using piecewise linear interpolation between breakpoints. The overall AQI is the MAXIMUM of all sub-indices (the 'dominant pollutant'). Minimum statutory requirement: at least 3 pollutants must be monitored, of which at least one must be PM2.5 or PM10."
        },
        {
            "q": "Q3: Why was Random Forest chosen over Linear Regression or a Single Decision Tree?",
            "a": "Single decision trees suffer from high variance and prone to overfitting. Linear Regression assumes linear independence and fails to model non-linear chemical interactions between sunlight, NOx, and ozone. Random Forest builds an ensemble of 100 de-correlated decision trees with bootstrap aggregation (bagging), achieving an R² of 0.9096 (90.96% variance explained)."
        },
        {
            "q": "Q4: Why does the project use Open-Meteo instead of a static CSV for live data?",
            "a": "A college project must be a real data-connected software artifact, not a static demo. Open-Meteo provides real-time CAMS atmospheric telemetry for any Indian coordinates with zero fabricated readings, high uptime, and zero API key expiration hurdles."
        },
        {
            "q": "Q5: How do you prevent displaying foreign cities with the same name (e.g. Pune)?",
            "a": "We implemented an India-only geocoding validation filter that validates both curated major hubs and enforces country_code == 'IN' or country == 'India' on all geocoding API responses."
        }
    ]

    for item in viva_qa:
        with st.expander(f"📌 {item['q']}"):
            st.markdown(f"**Answer:** {item['a']}")

st.markdown("---")
st.caption("AirWatch India | College Mini-Project Technical Documentation | Third-Year BCS")
