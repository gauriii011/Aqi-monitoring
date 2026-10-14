"""
src/prediction.py
Machine Learning AQI prediction pipeline using trained RandomForestRegressor.
Loads aqi_model.pkl and feature_columns.pkl, performs validation,
handles live feature mapping, and provides model explainability.
"""

import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from src.live_aqi import get_aqi_category_info

# Historical median values from city_day.csv for safe imputation of unmonitored gases
HISTORICAL_MEDIANS = {
    "PM2.5": 48.57,
    "PM10": 95.68,
    "NO": 9.89,
    "NO2": 21.69,
    "NOx": 23.52,
    "NH3": 15.85,
    "CO": 0.89,     # mg/m³
    "SO2": 9.16,
    "O3": 30.84,
    "Benzene": 1.07,
    "Toluene": 2.97,
    "Xylene": 0.98
}

# Verified Model Evaluation Metrics from training code & notebook validation
MODEL_METRICS = {
    "algorithm": "Random Forest Regressor",
    "n_estimators": 100,
    "random_state": 42,
    "dataset": "city_day.csv (Indian Central Pollution Control Board stations)",
    "training_rows": 24848,
    "test_rows": 6212,
    "split_ratio": "80% Train / 20% Test",
    "mae": 20.55,           # Verified from notebook cell 20
    "r2_score": 0.9096,     # Verified from notebook cell 20 (90.96% variance explained)
    "previous_mae_baseline": 19.96,
    "previous_r2_baseline": 0.8803
}


@st.cache_resource(show_spinner=False)
def load_ml_model():
    """
    Loads serialized Random Forest model and exact feature column order.
    Returns (model, feature_columns, error_message).
    """
    model_path = "aqi_model.pkl"
    features_path = "feature_columns.pkl"

    if not os.path.exists(model_path):
        return None, None, f"Model file '{model_path}' not found in root directory."
    if not os.path.exists(features_path):
        return None, None, f"Feature columns file '{features_path}' not found in root directory."

    try:
        model = joblib.load(model_path)
        feature_columns = joblib.load(features_path)
        return model, feature_columns, None
    except Exception as e:
        return None, None, f"Failed to load model files: {str(e)}"


def get_feature_importances(model, feature_columns) -> pd.DataFrame:
    """
    Extracts feature importances from trained RandomForestRegressor.
    """
    if model is None or not hasattr(model, "feature_importances_"):
        return pd.DataFrame()

    importances = model.feature_importances_
    df_fi = pd.DataFrame({
        "Feature": feature_columns,
        "Importance": importances,
        "Percentage": [round(x * 100, 2) for x in importances]
    }).sort_values("Importance", ascending=False)

    return df_fi


def predict_aqi(pollutant_dict: dict, use_medians_for_missing: bool = True) -> dict:
    """
    Generates predicted AQI using the trained Random Forest model.
    
    Parameters:
    - pollutant_dict: dictionary containing pollutant names as keys.
      Expected units:
        CO: mg/m³
        all other pollutants: µg/m³
    - use_medians_for_missing: If True, fills missing unmonitored features with
      historical medians; if False, passes NaN to model.
      
    Returns dictionary with:
    - predicted_aqi: float
    - category: string (Good, Satisfactory, Moderate, Poor, Very Poor, Severe)
    - category_info: dict with color and summary
    - missing_features: list of features that were absent/imputed
    - feature_values_used: dict of the exact input row fed into model
    """
    model, feature_columns, error_msg = load_ml_model()
    if error_msg:
        return {
            "success": False,
            "error": error_msg
        }

    input_data = {}
    missing_features = []

    for col in feature_columns:
        val = pollutant_dict.get(col)
        if val is None or (isinstance(val, (int, float)) and np.isnan(val)):
            missing_features.append(col)
            if use_medians_for_missing:
                input_data[col] = HISTORICAL_MEDIANS.get(col, 10.0)
            else:
                input_data[col] = np.nan
        else:
            try:
                input_data[col] = float(val)
            except (ValueError, TypeError):
                missing_features.append(col)
                input_data[col] = HISTORICAL_MEDIANS.get(col, 10.0)

    # Build single-row DataFrame in the exact training column order
    input_df = pd.DataFrame([input_data])[feature_columns]

    try:
        raw_pred = model.predict(input_df)[0]
        pred_value = max(0.0, round(float(raw_pred), 1))
        category_info = get_aqi_category_info(pred_value)

        return {
            "success": True,
            "predicted_aqi": pred_value,
            "category": category_info["name"],
            "category_info": category_info,
            "missing_features": missing_features,
            "imputed_count": len(missing_features),
            "feature_values_used": input_data,
            "input_df": input_df
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Prediction failed during model inference: {str(e)}"
        }


def predict_from_live_data(live_pollutants: dict) -> dict:
    """
    Adapts live API pollutant readings into the format expected by the ML model.
    Converts CO from µg/m³ to mg/m³ if needed, maps keys, and calls predict_aqi.
    """
    ml_input = {}
    
    # Map API keys to ML feature names
    mapping = {
        "PM2.5": "PM2.5",
        "PM10": "PM10",
        "NO2": "NO2",
        "SO2": "SO2",
        "O3": "O3",
        "NH3": "NH3"
    }

    for src_key, target_col in mapping.items():
        if src_key in live_pollutants:
            p_obj = live_pollutants[src_key]
            val = p_obj.get("value") if isinstance(p_obj, dict) else p_obj
            ml_input[target_col] = val

    # CO handling: ML model trained with CO in mg/m³
    if "CO" in live_pollutants:
        p_obj = live_pollutants["CO"]
        co_val = p_obj.get("value") if isinstance(p_obj, dict) else p_obj
        if co_val is not None:
            # If greater than 50, it is in µg/m³, convert to mg/m³
            ml_input["CO"] = (co_val / 1000.0) if co_val > 50.0 else co_val

    # Secondary volatile organics are not available from atmospheric satellite models
    ml_input["NO"] = None
    ml_input["NOx"] = None
    ml_input["Benzene"] = None
    ml_input["Toluene"] = None
    ml_input["Xylene"] = None

    return predict_aqi(ml_input, use_medians_for_missing=True)
