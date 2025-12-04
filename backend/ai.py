from google import genai
import json
from sqlalchemy.orm import Session
from .models import Patient, PatientKnowledge, PatientHeartDisease, PatientImage, Result

# Configure Gemini once

def ask(db: Session, question: str, patient_id: int, is_doctor: bool = True):

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    knowledge = db.query(PatientKnowledge).filter(PatientKnowledge.patient_id == patient_id).first()
    heart = db.query(PatientHeartDisease).filter(PatientHeartDisease.patient_id == patient_id).first()
    images = db.query(PatientImage).filter(PatientImage.patient_id == patient_id).all()
    result = db.query(Result).filter(Result.patient_id == patient_id).order_by(Result.id.desc()).first()

    # Prepare data
    patient_data = {
        "patient": patient.__dict__,
        "knowledge": knowledge.__dict__ if knowledge else {},
        "heart": heart.__dict__ if heart else {},
        "images": [i.__dict__ for i in images],
        "result": result.__dict__ if result else {}
    }

    # Build prompt
    if is_doctor:
        prompt = doctor_prompt(json.dumps(patient_data, default=str), question)
    else:
        prompt = patient_prompt(json.dumps(patient_data, default=str), question)

    # Gemini client
    client = genai.Client(api_key="AIzaSyAjVS78vPCCT-OeOxiSVSSPqOHuMcWHdbU")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {"answer": response.text}


def doctor_prompt(patient_data, question):
    return f"""
    You are a clinical assistant AI.
    You receive structured patient data.

    PATIENT DATA (JSON):
    {patient_data}

    DOCTOR'S QUESTION:
    {question}

    RESPONSE RULES:
    - Max 5 sentences
    - Must be medically accurate
    - Reference exact patient metrics when useful
    - Never hallucinate missing data
    """


def patient_prompt(patient_data, question):
    return f"""
    You are a friendly health assistant AI.
    The data below belongs to a patient.

    PATIENT DATA (JSON):
    {patient_data}

    PATIENT QUESTION:
    {question}

    RESPONSE RULES:
    - Max 5 sentences
    - Simple language
    - Give lifestyle & diet advice
    - Use their actual metrics if relevant
    - Never hallucinate
    """
