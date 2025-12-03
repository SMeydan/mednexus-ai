from sqlalchemy.orm import Session

from .models import Result, Patient, PatientKnowledge, PatientHeartDisease, PatientImage
from . import schemas


def get_reports_by_patient(db: Session, patient_id: int):
    return (
        db.query(Result)
        .filter(Result.patient_id == patient_id)
        .all()
    )


def create_report(db: Session, req: int) -> schemas.ReportResponse:
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
    result = db.query(Result).filter(
        Result.patient_id == req
    ).first()

    if not result:
        result = Result(
            patient_id=req,
            diabetes_risk=0.15,
            hypertension_risk=0.35,
            heart_disease_risk=0.20,
            diabetes_diagnosis="Low risk",
            hypertension_diagnosis="Borderline high",
            heart_disease_diagnosis="Moderate risk",
            source="rule_based_stub",
            result="Auto generated placeholder summary. Replace with real model output."
        )
        db.add(result)
        db.commit()
        db.refresh(result)

    return schemas.ReportResponse(
        patient=patient,
        knowledge=knowledge,
        heart=heart,
        images=images,
        result=result,
    )


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
