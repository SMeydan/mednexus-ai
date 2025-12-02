from sqlalchemy.orm import Session

from .models import Result
from . import schemas


def get_reports_by_patient(db: Session, patient_id: int):
    return (
        db.query(Result)
        .filter(Result.patient_id == patient_id)
        .all()
    )


def create_report(db: Session, report: schemas.ReportCreate):
    data = report.dict()
    patient_id = data.pop("patient_id")
    db_report = Result(patient_id=patient_id, **data)
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


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
    """
    Eski isim kalsın ama gerçekten siliyoruz.
    """
    db_report = db.query(Result).filter(Result.id == report_id).first()
    if not db_report:
        return None
    db.delete(db_report)
    db.commit()
    return db_report
