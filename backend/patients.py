from sqlalchemy.orm import Session

from . import models, schemas


def get_patients(db: Session):
    return db.query(models.Patient).all()


def get_patient(db: Session, patient_id: int):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    patient_knowledge =  db.query(models.PatientKnowledge).filter(models.Patient.id == patient_id).first()
    images = db.query(models.PatientImage).filter(models.PatientImage.patient_id == patient_id).all()
    return {
        "patient" : patient,
        "knowledge": patient_knowledge,
        "images": images
    }


def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(
        national_id=patient.national_id,
        full_name=patient.full_name,
        complaint=patient.complaint,
        age=patient.age,
        gender=patient.gender.lower(),
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate):
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None

    data = patient.dict(exclude_unset=True)

    if "gender" in data and data["gender"]:
        data["gender"] = data["gender"].lower()

    for field, value in data.items():
        setattr(db_patient, field, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient

def soft_delete_patient(db: Session, patient_id: int):
    """
    Eski isimle bırakıyoruz ama DB'de gerçekten siliyoruz.
    ON DELETE CASCADE sayesinde bağlı kayıtlar da gidiyor.
    """
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    db.delete(db_patient)
    db.commit()
    return db_patient

def create_or_update_knowledge(db, patient_id, data):
    kn = db.query(models.PatientKnowledge).filter(models.PatientKnowledge.patient_id == patient_id).first()

    if not kn:
        kn = models.PatientKnowledge(patient_id=patient_id)

    for field, value in data.dict().items():
        setattr(kn, field, value)

    db.add(kn)
    db.commit()
    db.refresh(kn)
    return kn
