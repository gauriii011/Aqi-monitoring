"""
src/health_advisory.py
Comprehensive Health Advisory System based on Indian National Air Quality Index (CPCB standards).
Provides targeted health guidance, risk factors for sensitive groups,
mask advice, indoor air quality precautions, and educational disclaimers.
"""

HEALTH_ADVISORY_DATA = {
    "Good": {
        "aqi_range": "0 – 50",
        "severity_level": "Minimal",
        "badge_color": "#00b050",
        "health_impact": "Air quality is considered satisfactory, and air pollution poses little or no risk.",
        "general_public": "Ideal conditions for all outdoor activities including jogging, cycling, and sports.",
        "sensitive_groups": "No special precautions required. Safe for infants, elderly, and respiratory patients.",
        "outdoor_activity": "Normal outdoor activities are completely unrestricted.",
        "ventilation": "Open windows and doors to allow fresh air circulation.",
        "masks": "Masks are not required for air pollution protection.",
        "key_recommendation": "Great day to enjoy nature and outdoor exercises!"
    },
    "Satisfactory": {
        "aqi_range": "51 – 100",
        "severity_level": "Low",
        "badge_color": "#92d050",
        "health_impact": "Air quality is acceptable. Minor breathing discomfort may occur in hypersensitive individuals.",
        "general_public": "Generally safe for outdoor recreational activities.",
        "sensitive_groups": "Individuals with extreme sensitivity to ozone or particulates should monitor for minor irritation.",
        "outdoor_activity": "Safe for regular routines. Sensitive individuals should take breaks if experiencing fatigue.",
        "ventilation": "Natural ventilation is safe and recommended during midday hours.",
        "masks": "Generally not required, except for hypersensitive individuals in traffic congestion.",
        "key_recommendation": "Maintain normal routine; sensitive individuals should observe body responses."
    },
    "Moderately Polluted": {
        "aqi_range": "101 – 200",
        "severity_level": "Moderate",
        "badge_color": "#ffc000",
        "health_impact": "May cause breathing discomfort to people with lung disease such as asthma, and discomfort to people with heart disease, children, and older adults.",
        "general_public": "Most healthy individuals can continue ordinary routines, but avoid strenuous outdoor exertion near busy roadways.",
        "sensitive_groups": "People with asthma, COPD, bronchitis, cardiovascular conditions, children, and elderly should limit prolonged outdoor exertion.",
        "outdoor_activity": "Shift high-intensity cardio exercises (running, HIIT) indoors or to early morning when traffic is light.",
        "ventilation": "Ventilate briefly when ambient air is clearest; close windows during peak traffic hours.",
        "masks": "Consider wearing a well-fitted surgical or N95 mask during prolonged outdoor exposure in congested areas.",
        "key_recommendation": "Sensitive groups should keep reliever inhalers handy and reduce prolonged heavy exertion."
    },
    "Poor": {
        "aqi_range": "201 – 300",
        "severity_level": "Unhealthy",
        "badge_color": "#ff6600",
        "health_impact": "Causes breathing discomfort to most people on prolonged exposure. May trigger coughing, shortness of breath, and throat irritation.",
        "general_public": "Everyone should reduce heavy outdoor exertion. Limit outdoor sports and jogging sessions.",
        "sensitive_groups": "High risk of exacerbations for asthma and heart patients. Elderly and children should strictly avoid strenuous outdoor activities.",
        "outdoor_activity": "Exercise indoors. Avoid jogging or cycling along major highways or during morning smog.",
        "ventilation": "Keep windows closed during morning and evening rush hours. Run HEPA air purifiers if available.",
        "masks": "Wear an N95 or N99 respirator mask when going outdoors for extended periods.",
        "key_recommendation": "Reduce outdoor time, use N95 masks in transit, and maintain indoor air filtration."
    },
    "Very Poor": {
        "aqi_range": "301 – 400",
        "severity_level": "Very Unhealthy",
        "badge_color": "#ff0000",
        "health_impact": "Causes respiratory illness to people on prolonged exposure. Severe triggering of asthma attacks, bronchitis, and cardiovascular stress.",
        "general_public": "Avoid all prolonged outdoor exertion. Healthy adults may experience throat scratchiness, wheezing, and stinging eyes.",
        "sensitive_groups": "Children, pregnant women, elderly, and respiratory/cardiac patients must stay indoors in clean environments.",
        "outdoor_activity": "Completely suspend outdoor cardio workouts, marathons, and outdoor sports matches.",
        "ventilation": "Keep windows and external vents tightly sealed. Use air purifiers with true HEPA filters on high mode.",
        "masks": "Mandatory N95 / N99 mask usage if stepping outside. Cloth and loose surgical masks offer inadequate PM2.5 filtration.",
        "key_recommendation": "Stay indoors with filtered air; vulnerable individuals must seek medical attention if symptoms worsen."
    },
    "Severe": {
        "aqi_range": "401 – 500+",
        "severity_level": "Hazardous / Emergency",
        "badge_color": "#7f0000",
        "health_impact": "Emergency health advisory: Healthy individuals experience acute respiratory symptoms and reduced lung capacity. Serious complications for elderly and sick.",
        "general_public": "Everyone must avoid all outdoor physical activity. Minimize travel outside homes or offices.",
        "sensitive_groups": "High vulnerability. Medical emergency precautions. Keep emergency rescue medication and nebulizers ready.",
        "outdoor_activity": "Strictly cancel all outdoor school activities, sports training, construction shifts, and commuting where possible.",
        "ventilation": "Seal window cracks. Do not smoke indoors. Avoid vacuuming without HEPA exhaust. Run purifiers continuously.",
        "masks": "N95 / N99 / FFP2 mask is strictly necessary for any essential outdoor transit. Avoid cloth masks.",
        "key_recommendation": "Public health alert: Stay indoors, operate air purifiers, seal drafts, and avoid all unnecessary outdoor exposure."
    }
}


def get_advisory_by_category(category_name: str) -> dict:
    """
    Returns complete advisory details for a given category name.
    Falls back to 'Moderately Polluted' if unknown.
    """
    for key, data in HEALTH_ADVISORY_DATA.items():
        if key.lower() in category_name.lower():
            return data
    return HEALTH_ADVISORY_DATA["Moderately Polluted"]


def evaluate_activity_safety(aqi: int, user_group: str, activity_type: str) -> dict:
    """
    Educational risk calculator that assesses safe activity duration based on:
    - aqi: current AQI value
    - user_group: 'General Healthy Adult', 'Child / Senior', 'Asthma / Heart Condition', 'Pregnant Woman'
    - activity_type: 'Indoor Relaxing', 'Casual Walking / Commuting', 'Outdoor Jogging / Sports', 'Heavy Construction / Manual Labor'
    """
    if aqi <= 50:
        return {
            "verdict": "SAFE",
            "badge_color": "#00b050",
            "message": "Conditions are ideal. You can participate in this activity with zero restrictions.",
            "mask_needed": False
        }
    elif aqi <= 100:
        if user_group in ["Asthma / Heart Condition"]:
            return {
                "verdict": "MODERATE CAUTION",
                "badge_color": "#92d050",
                "message": "Generally okay, but keep emergency inhaler ready if doing heavy exertion.",
                "mask_needed": False
            }
        return {
            "verdict": "SAFE",
            "badge_color": "#00b050",
            "message": "Air quality is satisfactory. Safe to proceed.",
            "mask_needed": False
        }
    elif aqi <= 200:
        if user_group in ["Asthma / Heart Condition", "Child / Senior", "Pregnant Woman"]:
            if activity_type in ["Outdoor Jogging / Sports", "Heavy Construction / Manual Labor"]:
                return {
                    "verdict": "UNSAFE - AVOID",
                    "badge_color": "#ffc000",
                    "message": "Sensitive individuals should avoid strenuous outdoor exertion. Exercise indoors instead.",
                    "mask_needed": True
                }
            return {
                "verdict": "CAUTION",
                "badge_color": "#ffc000",
                "message": "Limit exposure duration and avoid busy traffic intersections.",
                "mask_needed": True
            }
        return {
            "verdict": "MODERATE",
            "badge_color": "#ffc000",
            "message": "Safe for healthy adults, but reduce long continuous outdoor workouts.",
            "mask_needed": False
        }
    elif aqi <= 300:
        if activity_type == "Indoor Relaxing":
            return {
                "verdict": "SAFE INDOORS",
                "badge_color": "#00b050",
                "message": "Safe inside. Keep windows closed and run purifiers if available.",
                "mask_needed": False
            }
        if user_group in ["Asthma / Heart Condition", "Child / Senior", "Pregnant Woman"]:
            return {
                "verdict": "STRICTLY AVOID",
                "badge_color": "#ff6600",
                "message": "High risk of respiratory distress. Stay indoors.",
                "mask_needed": True
            }
        return {
            "verdict": "UNHEALTHY",
            "badge_color": "#ff6600",
            "message": "Avoid heavy cardio outdoors. If you must go outside, wear an N95 mask.",
            "mask_needed": True
        }
    else:  # Very Poor or Severe
        if activity_type == "Indoor Relaxing":
            return {
                "verdict": "SAFE INDOORS (WITH PURIFIER)",
                "badge_color": "#ffc000",
                "message": "Stay indoors with windows closed. Run air cleaners.",
                "mask_needed": False
            }
        return {
            "verdict": "HAZARDOUS - DO NOT PROCEED",
            "badge_color": "#7f0000",
            "message": "Dangerous air pollution. Suspend outdoor activities immediately. Wear N95/N99 if transit is unavoidable.",
            "mask_needed": True
        }


DISCLAIMER_TEXT = """
**Medical Disclaimer:**
*The health advisories and activity recommendations provided by AirWatch India are intended solely for educational, academic, and general awareness purposes according to guidelines published by the Central Pollution Control Board (CPCB) and the World Health Organization (WHO). This application does not provide clinical diagnosis, medical prescriptions, or emergency healthcare services. Individual susceptibility to air pollution varies substantially based on personal medical history, genetics, age, and pre-existing conditions. Always consult a qualified medical doctor or healthcare professional for individualized health advice.*
"""
