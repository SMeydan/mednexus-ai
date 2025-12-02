from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    national_id = Column(String(11), unique=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    complaint = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    knowledge = relationship(
        "PatientKnowledge",
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan",
    )
    heart_disease = relationship(
        "PatientHeartDisease",
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan",
    )
    images = relationship(
        "PatientImage",
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    results = relationship(
        "Result",
        back_populates="patient",
        cascade="all, delete-orphan",
    )


class PatientKnowledge(Base):
    __tablename__ = "patient_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)

    glucose = Column(Float, nullable=True)
    diabetes = Column(Boolean, nullable=True)
    heart_disease = Column(Boolean, nullable=True)
    bmi = Column(Float, nullable=True)
    hba1c = Column(Float, nullable=True)

    smoking = Column(Boolean, nullable=True)
    cigarettes_per_day = Column(Integer, nullable=True)

    physical_activity = Column(Boolean, nullable=True)
    stress = Column(Boolean, nullable=True)
    alcohol = Column(Boolean, nullable=True)
    chronic_disease = Column(Boolean, nullable=True)

    prevalent_hypertension = Column(Boolean, nullable=True)
    prevalent_stroke = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    patient = relationship("Patient", back_populates="knowledge")


class PatientHeartDisease(Base):
    __tablename__ = "patient_heart_disease"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)

    bp_meds = Column(Boolean, nullable=True)
    diastolic_bp = Column(Integer, nullable=True)
    systolic_bp = Column(Integer, nullable=True)
    heart_rate = Column(Integer, nullable=True)

    chest_pain = Column(String(20), nullable=True)
    resting_ecg = Column(String(20), nullable=True)
    exercise_slope = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="heart_disease")


class PatientImage(Base):
    __tablename__ = "patient_images"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)

    image_path = Column(Text, nullable=False)
    disease = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="images")


class Result(Base):
    __tablename__ = "result"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)

    diabetes_risk = Column(Float, nullable=True)
    hypertension_risk = Column(Float, nullable=True)
    heart_disease_risk = Column(Float, nullable=True)

    diabetes_diagnosis = Column(String(30), nullable=True)
    hypertension_diagnosis = Column(String(30), nullable=True)
    heart_disease_diagnosis = Column(String(30), nullable=True)

    source = Column(String(300), nullable=True)
    result = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="results")
