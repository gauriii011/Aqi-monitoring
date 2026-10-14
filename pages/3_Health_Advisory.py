"""
pages/3_Health_Advisory.py
Health Advisory Portal for AirWatch India.
Educational health guidance based on Indian National AQI (CPCB standards).
Includes interactive activity safety calculator, category guidelines,
and protective equipment advice.
"""

import streamlit as st
import os

from src.health_advisory import (
    HEALTH_ADVISORY_DATA,
    evaluate_activity_safety,
    DISCLAIMER_TEXT
)
from src.live_aqi import MAJOR_INDIAN_CITIES, fetch_live_air_quality

st.set_page_config(
    page_title="Health Advisory & Risk Guidelines | AirWatch India",
    page_icon="🏥",
    layout="wide"
)

# Load styling
css_path = os.path.join("assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🏥 Health Advisory & Personal Air Risk Assessment")
st.markdown("Actionable, educational guidance aligned with Central Pollution Control Board (CPCB) and World Health Organization (WHO) environmental health baselines.")

# ==============================================================================
# SECTION 1: INTERACTIVE OUTDOOR ACTIVITY RISK CHECKER
# ==============================================================================
st.subheader("⚡ Personalized Activity Safety Checker")
st.markdown("Determine if it is safe to exercise, commute, or spend time outdoors based on current air pollution levels.")

col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    mode = st.radio("Choose Air Quality Source:", ["Use Live City Reading", "Simulate Custom AQI"], horizontal=True)
    if mode == "Use Live City Reading":
        city_list = list(MAJOR_INDIAN_CITIES.keys())
        default_city = st.session_state.get("selected_city", "Delhi")
        chosen_city = st.selectbox("Select City:", city_list, index=city_list.index(default_city) if default_city in city_list else 0)
        meta = MAJOR_INDIAN_CITIES[chosen_city]
        d = fetch_live_air_quality(meta["lat"], meta["lon"], chosen_city)
        active_aqi = d.get("indian_aqi", 150)
        st.info(f"Live CPCB AQI for {chosen_city}: **{active_aqi}** ({d.get('indian_category')})")
    else:
        active_aqi = st.slider("Simulate AQI Value (0 - 500):", min_value=10, max_value=500, value=180, step=5)

with col_input2:
    user_group = st.selectbox(
        "Who is Participating?",
        [
            "General Healthy Adult",
            "Child / Senior",
            "Asthma / Heart Condition",
            "Pregnant Woman"
        ]
    )

with col_input3:
    activity = st.selectbox(
        "Planned Activity:",
        [
            "Indoor Relaxing",
            "Casual Walking / Commuting",
            "Outdoor Jogging / Sports",
            "Heavy Construction / Manual Labor"
        ]
    )

result = evaluate_activity_safety(active_aqi, user_group, activity)

# Render Safety Verdict Card
st.markdown(
    f"""
    <div style="background-color: #ffffff; border-radius: 12px; border: 2px solid {result['badge_color']}; padding: 18px 24px; margin: 15px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Safety Evaluation</span>
                <h3 style="margin: 4px 0; color: {result['badge_color']}; font-weight: 800;">{result['verdict']}</h3>
            </div>
            <div>
                <span style="background-color: {result['badge_color']}; color: #ffffff; padding: 6px 14px; border-radius: 999px; font-weight: 700; font-size: 0.9rem;">
                    AQI: {active_aqi}
                </span>
            </div>
        </div>
        <p style="font-size: 1.05rem; color: #1e293b; margin: 12px 0 6px 0;">
            {result['message']}
        </p>
        <div style="margin-top: 8px; font-size: 0.9rem; color: #475569;">
            😷 <strong>Mask Recommended:</strong> {'Yes, wear N95 or N99 respirator' if result['mask_needed'] else 'Not strictly necessary, but helpful in heavy traffic'}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ==============================================================================
# SECTION 2: OFFICIAL INDIAN CPCB CATEGORY HEALTH CARDS
# ==============================================================================
st.subheader("📚 Detailed Health Guidelines by Indian AQI Category")
st.markdown("Click on any category to view tailored precautions, physiological impacts, and vulnerable group warnings.")

for cat_name, info in HEALTH_ADVISORY_DATA.items():
    with st.expander(f"🔹 {cat_name} (AQI {info['aqi_range']}) — Severity: {info['severity_level']}"):
        col_c1, col_c2 = st.columns([1.5, 1])
        
        with col_c1:
            st.markdown(f"**Health Impact:** {info['health_impact']}")
            st.markdown(f"**General Population Advice:** {info['general_public']}")
            st.markdown(f"**Vulnerable Groups (Children, Elderly, Patients):** {info['sensitive_groups']}")
            st.markdown(f"**Key Recommendation:** *{info['key_recommendation']}*")

        with col_c2:
            st.markdown(
                f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;">
                    <div style="font-weight: 700; color: #334155; margin-bottom: 6px;">Actionable Checklist:</div>
                    <ul style="font-size: 0.88rem; color: #475569; padding-left: 18px; margin-bottom: 0;">
                        <li><strong>Outdoor Action:</strong> {info['outdoor_activity']}</li>
                        <li><strong>Ventilation:</strong> {info['ventilation']}</li>
                        <li><strong>Mask Usage:</strong> {info['masks']}</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown("---")

# ==============================================================================
# SECTION 3: PROTECTIVE GEAR & INDOOR AIR GUIDANCE
# ==============================================================================
st.subheader("🛡️ Personal Protective Equipment & Indoor Air Management")

col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown("##### 😷 Respiratory Mask Comparison")
    st.markdown(
        """
        | Mask Type | PM2.5 Filtration | Fit & Seal | Best Used When |
        | :--- | :--- | :--- | :--- |
        | **N95 / N99 / FFP2** | **95% – 99%** | Tight, airtight seal | AQI > 200 (Poor to Severe) |
        | **Surgical 3-Ply** | ~60% – 70% | Loose at edges | Dust & coarse droplets |
        | **Cloth / Cotton** | < 30% | Very loose | Ineffective against PM2.5 |
        
        💡 **BCS Exam Tip:** PM2.5 particles are less than 2.5 microns in diameter — 30 times thinner than human hair. Only certified electrostatic filters (N95/N99) can trap these microscopic particles.
        """
    )

with col_m2:
    st.markdown("##### 🏠 Indoor Air Quality Best Practices")
    st.markdown(
        """
        1. **HEPA Air Purifiers:** Ensure filters use True HEPA (captures 99.97% of particles down to 0.3 microns) with adequate CADR rating for your room size.
        2. **Ventilation Timing:** Avoid opening windows during morning (6 AM – 9 AM) and evening rush hours when thermal inversion traps ground pollutants.
        3. **Indoor Emission Reduction:** Avoid lighting incense sticks (agarbatti), mosquito coils, or smoking indoors, which generate severe PM2.5 spikes.
        4. **Natural Air Purifying Plants:** Areca Palm, Snake Plant (Sansevieria), and Money Plant help naturally oxygenate indoor spaces.
        """
    )

st.markdown("---")

# Medical Disclaimer
st.markdown(DISCLAIMER_TEXT)
