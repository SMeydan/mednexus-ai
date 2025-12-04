from google.generativeai import GenerativeModel
import json
from sqlalchemy.orm import Session
from .models import Patient, PatientKnowledge, PatientHeartDisease, PatientImage, Result
def ask(db: Session,question: str, patient_id: int, is_doctor: bool = True):

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    knowledge = db.query(PatientKnowledge).filter(PatientKnowledge.patient_id == patient_id).first()
    heart = db.query(PatientHeartDisease).filter(PatientHeartDisease.patient_id == patient_id).first()
    images = db.query(PatientImage).filter(PatientImage.patient_id == patient_id).all()
    result = db.query(Result).filter(Result.patient_id == patient_id).order_by(Result.id.desc()).first()

    # RAW DATA → String haline çevir
    patient_data = {
        "patient": patient.__dict__,
        "knowledge": knowledge.__dict__ if knowledge else {},
        "heart": heart.__dict__ if heart else {},
        "images": [i.__dict__ for i in images],
        "result": result.__dict__ if result else {}
    }

    # --- GEMINI CALL ---
    model = GenerativeModel("gemini-1.5-flash")

    if is_doctor:
        prompt = doctor_prompt(json.dumps(patient_data, default=str), question)
    else:
        prompt = patient_prompt(json.dumps(patient_data, default=str), question)

    response = model.generate_content(prompt)

    return {"answer": response.text}

def doctor_prompt(patient_data, question):
    return f"""
    You are a clinical assistant AI. 
    The data below describes a real patient.

    PATIENT STRUCTURED DATA (JSON):
    {patient_data}

    QUESTION FROM DOCTOR:
    {question}

    TASK:
    Give a medically accurate, short answer (max 5 sentences).
    Use the patient's specific metrics, risks and image interpretations if useful.
    Never hallucinate missing data.
    """

def patient_prompt(patient_data, question):
    return f"""
    You are a helpful health assistant AI. 
    The data below describes a real patient.

    PATIENT STRUCTURED DATA (JSON):
    {patient_data}

    QUESTION FROM PATIENT:
    {question}

    TASK:
    Give diet and lifestyle advice in simple terms (max 5 sentences).
    Use the patient's specific metrics, risks and image interpretations if useful.
    Never hallucinate missing data.
    """