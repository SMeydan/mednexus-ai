import numpy as np
import pickle
import pandas as pd
import cv2
import json
from tensorflow.keras.models import load_model
from .models import PatientHeartDisease
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input
import os
from joblib import load
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
STATIC_DIR = os.path.join(BASE_DIR, "static")
def model_path(name):
    return os.path.join(MODELS_DIR, name)
# ---------------------------
#  Load All Models Once
# ---------------------------
# DIABETES MODELLERI
diabetes_model = load_model(model_path("diabet_csv.h5"))
diabetes_scaler = load(model_path("diabet_csv_scaler.joblib"))

# HYPERTENSION (SKLEARN)
with open(model_path("hypertension.pkl"), "rb") as f:
    hypertension_model = pickle.load(f)

# HEART DISEASES
with open(model_path("heart_diseases_csv.pkl"), "rb") as f:
    heart_model = pickle.load(f)

heart_scaler = load(model_path("heart_diseases_scaler.pkl"))

# VISUAL MODELS (KERAS)
hypertension_visual_model = load_model(model_path("hypertension_visual.h5"))


IMG_SIZE = (128,128)

# -------------------------------------
# Image Preprocess Functions
# -------------------------------------
def preprocess_eff(img_path):
    if img_path.startswith("/static/"):
        relative = img_path.lstrip("/")  # static/imgs/...
        img_path = os.path.join(BASE_DIR, relative)
    else:
        img_path = img_path 
    img = image.load_img(img_path, target_size=(224,224))
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)
    return np.expand_dims(img_array, axis=0)

def preprocess_128(img_path):
    if img_path.startswith("/static/"):
        relative = img_path.lstrip("/")  # static/imgs/...
        img_path = os.path.join(BASE_DIR, relative)
    else:
        img_path = img_path 
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, IMG_SIZE)
    img = img / 255.0
    return np.expand_dims(img, axis=0)


# -------------------------------------
# MAIN RISK PIPELINE
# -------------------------------------
def run_risk_pipeline(patient, knowledge, heart, images,db):
    """
    Returns {
        diabetes_risk,
        hypertension_risk,
        heart_disease_risk,
        diabetes_diagnosis,
        hypertension_diagnosis,
        heart_disease_diagnosis,
        visual: {...}
    }
    """

    # ==================================
    # 1) NUMERIC MODELLER
    # ==================================

    # ---- Diabetes numeric ----
    gender_female = 1 if patient.gender == "female" else 0
    gender_male = 1 if patient.gender == "male" else 0

    smoking = "current" if knowledge.smoking else "never"
    smoking_current = 1 if smoking == "current" else 0
    smoking_ever = 0
    smoking_former = 0
    smoking_never = 1 if smoking == "never" else 0
    smoking_notcurrent = 0

    diabetes_features = np.array([[
        patient.age,
        1 if knowledge.prevalent_hypertension else 0,
        1 if knowledge.heart_disease else 0,
        knowledge.bmi or 0,
        knowledge.hba1c or 0,
        knowledge.glucose or 0,
        gender_female, gender_male,
        smoking_current, smoking_ever, smoking_former,
        smoking_never, smoking_notcurrent
    ]])

    diabetes_scaled = diabetes_scaler.transform(diabetes_features)
    diabetes_prob = float(diabetes_model.predict(diabetes_scaled)[0][0])


    # ---- Hypertension numeric ----
    hypertension_df = pd.DataFrame([{
        "gender": 1 if patient.gender == "male" else 0,
        "age": patient.age,
        "age_group" : pd.cut([patient.age], bins=[0, 30, 45, 60, 75, 100], labels=["young", "adult", "mid", "senior", "elder"])[0],
        "diabetes": 1 if knowledge.diabetes else 0,
        "heart_disease": 1 if knowledge.heart_disease else 0,
        "smoking_history": 1 if smoking == "current" else 0,
        "bmi": knowledge.bmi or 0,
        "bmi_category": pd.cut([knowledge.bmi or 0], bins=[0, 18.5, 24.9, 29.9, 100], labels=["under", "normal", "over", "obese"])[0],
        "glucose_hba1c": knowledge.hba1c or 0,
        "HbA1c_level": knowledge.hba1c or 0,
        "blood_glucose_level": knowledge.glucose or 0,
        "glucose_category" : pd.cut([knowledge.glucose or 0], bins=[0, 99, 125, 300], labels=["normal", "prediabetic", "high"])[0]
    }])
    df = hypertension_df

    # 1) glucose_hba1c
    df["glucose_hba1c"] = df["blood_glucose_level"] * df["glucose_hba1c"]

    # 2) age_group (categorical)
    df["age_group"] = pd.cut(
        df["age"], bins=[0, 30, 45, 60, 120],
        labels=["young", "adult", "mid", "senior"]
    )

    # 3) bmi_categoryz
    df["bmi_category"] = pd.cut(
        df["bmi"], bins=[0, 18.5, 25, 30, 100],
        labels=["under", "normal", "over", "obese"]
    )

    # 4) glucose_category
    df["glucose_category"] = pd.cut(
        df["blood_glucose_level"],
        bins=[0, 100, 200, 500],
        labels=["normal", "prediabetic", "high"]
    )

    # 5) age_bmi
    df["age_bmi"] = df["age"] * df["bmi"]

    # 6) age_glucose
    df["age_glucose"] = df["age"] * df["blood_glucose_level"]

    # 7) cardiovascular_risk
    df["cardiovascular_risk"] = df["bmi"] * 0.25 + df["blood_glucose_level"] * 0.15

    # 8) metabolic_risk
    df["metabolic_risk"] = df["bmi"] * 0.3 + df["glucose_hba1c"] * 0.4

    # 9) diabetes_risk_score
    df["diabetes_risk_score"] = (
        df["blood_glucose_level"] * 0.3 +
        df["glucose_hba1c"] * 0.5 +
        df["bmi"] * 0.2
    )

    hypertension_df = df
    hypertension_prob = float(hypertension_model.predict_proba(hypertension_df)[0][1])

    # ---- Heart disease numeric ----
    heart_numeric = pd.DataFrame([{
        "age": patient.age,
        "bmi": knowledge.bmi or 0,
        "bpmeds": 1 if heart.bp_meds else 0,
        "cigs_per_day": knowledge.cigarettes_per_day or 0,
        "diabp": heart.diastolic_bp or 0,
        "glucose": knowledge.glucose or 0,
        "heartrate": heart.heart_rate or 0,
        "sysbp": heart.systolic_bp or 0,
        "totchol": knowledge.total_cholesterol or 0,
        "cp_atypical_angina": 1 if heart.chest_pain == "atypical" else 0,
        "cp_non_anginal": 1 if heart.chest_pain == "non-anginal" else 0,
        "cp_typical_angina": 1 if heart.chest_pain == "typical" else 0,
        "cp_unknown": 0,
        "current_smoker_1.0": smoking_current,
        "diabetes_1.0": 1 if knowledge.diabetes else 0,
        "restecg_1": 0,
        "restecg_2": 0,
        "restecg_Unknown": 0,
        "restecg_lv hypertrophy": 0,
        "restecg_normal": 1,
        "restecg_st-t abnormality": 0,
        "slope_1": 0,
        "slope_2": 1,
        "slope_3": 0,
        "slope_Unknown": 0,
        "slope_downsloping": 0,
        "slope_flat": 1,
        "slope_upsloping": 0,
        "prevalent_hyp_1.0": 1 if knowledge.prevalent_hypertension else 0,
        "prevalent_stroke_1.0": 1 if knowledge.prevalent_stroke else 0
    }])

    heart_scaled = heart_scaler.transform(heart_numeric)
    heart_prob = float(heart_model.predict_proba(heart_scaled)[0][1])

    # ==================================
    # 2) VISUAL ANALYSIS
    # ==================================
    visual = {}

    # hypertension visual
    h_imgs = [img.image_path for img in images if img.disease.lower() == "hypertension"]
    if h_imgs:
        arr = preprocess_eff(h_imgs[0])
        visual["hypertension_visual"] = float(hypertension_visual_model.predict(arr)[0][0])
    else:
        visual["hypertension_visual"] = None


    # ==================================
    # 3) DIAGNOSIS LABELS
    # ==================================
    def diag(p):
        if p < 0.33: return "Low risk"
        if p < 0.66: return "Moderate risk"
        return "High risk"

    return {
        "diabetes_risk": diabetes_prob,
        "hypertension_risk": hypertension_prob,
        "heart_disease_risk": heart_prob,

        "diabetes_diagnosis": diag(diabetes_prob),
        "hypertension_diagnosis": diag(hypertension_prob),
        "heart_disease_diagnosis": diag(heart_prob),

        "visual": visual
    }
