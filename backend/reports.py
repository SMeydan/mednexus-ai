import json
from sqlalchemy.orm import Session

from .models import Result, Patient, PatientKnowledge, PatientHeartDisease, PatientImage
from . import schemas
from .risk_models import run_risk_pipeline

def get_reports_by_patient(db: Session, patient_id: int):
    return (
        db.query(Result)
        .filter(Result.patient_id == patient_id)
        .all()
    )


def create_report(db: Session, req: int):
    patient = db.query(Patient).filter(
        Patient.id == req
    ).first()
    if not patient:
        raise ValueError("Patient not found")

    knowledge = db.query(PatientKnowledge).filter(
        PatientKnowledge.patient_id == req
    ).first()

    heart = db.query(PatientHeartDisease).filter(
        PatientHeartDisease.patient_id == req
    ).first()

    images = db.query(PatientImage).filter(
        PatientImage.patient_id == req
    ).all()

    # TODO : dummy
    # result = db.query(Result).filter(
    #     Result.patient_id == req
    # ).first()
    model_out = run_risk_pipeline(patient, knowledge, heart, images,db)

    #result = db.query(Result).filter(Result.patient_id == patient.id).first()
    result = None
    if not result:
        result = Result(patient_id=patient.id)
        db.add(result)

    result.diabetes_risk = model_out["diabetes_risk"]
    result.hypertension_risk = model_out["hypertension_risk"]
    result.heart_disease_risk = model_out["heart_disease_risk"]

    result.diabetes_diagnosis = model_out["diabetes_diagnosis"]
    result.hypertension_diagnosis = model_out["hypertension_diagnosis"]
    result.heart_disease_diagnosis = model_out["heart_disease_diagnosis"]

    # visual sonuçları JSON string olarak kaydediyorum
    result.source = "model_pipeline"
    result.result = json.dumps(model_out["visual"], indent=2)

    db.commit()
    db.refresh(result)

    return {
    "patient": {
        "id": patient.id,
        "national_id": patient.national_id,
        "full_name": patient.full_name,
        "complaint": patient.complaint,
        "age": patient.age,
        "gender": patient.gender,
        "created_at": patient.created_at.isoformat(),
    },
    "knowledge": {
        "glucose": knowledge.glucose,
        "diabetes": knowledge.diabetes,
        "heart_disease": knowledge.heart_disease,
        "bmi": knowledge.bmi,
        "hba1c": knowledge.hba1c,
        "smoking": knowledge.smoking,
        "cigarettes_per_day": knowledge.cigarettes_per_day,
    } if knowledge else None,
    "heart": {
        "bp_meds": heart.bp_meds,
        "diastolic_bp": heart.diastolic_bp,
        "systolic_bp": heart.systolic_bp,
        "heart_rate": heart.heart_rate,
        "chest_pain": heart.chest_pain,
        "resting_ecg": heart.resting_ecg,
        "exercise_slope": heart.exercise_slope,
        "created_at": heart.created_at.isoformat(),
    } if heart else None,
    "images": [
        {
            "id": img.id,
            "image_path": img.image_path,
            "disease": img.disease,
            "created_at": img.created_at.isoformat(),
        }
        for img in images
    ],
    "result": {
        "diabetes_risk": result.diabetes_risk,
        "hypertension_risk": result.hypertension_risk,
        "heart_disease_risk": result.heart_disease_risk,
        "diabetes_diagnosis": result.diabetes_diagnosis,
        "hypertension_diagnosis": result.hypertension_diagnosis,
        "heart_disease_diagnosis": result.heart_disease_diagnosis,
        "source": result.source,
        "result": result.result,
        "created_at": result.created_at.isoformat(),
    }
}




def update_report(db: Session, report_id: int, report: schemas.ReportUpdate):
    db_report = db.query(Result).filter(Result.id == report_id).first()
    if not db_report:
        return None

    data = report.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(db_report, field, value)

    db.commit()
    db.refresh(db_report)
    return db_report


def soft_delete_report(db: Session, report_id: int):
    db_report = db.query(Result).filter(Result.id == report_id).first()
    if not db_report:
        return None
    db.delete(db_report)
    db.commit()
    return db_report
