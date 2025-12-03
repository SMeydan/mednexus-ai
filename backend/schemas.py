from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# --------------------
# Patient
# --------------------


class PatientBase(BaseModel):
    national_id: str
    full_name: str
    complaint: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class PatientDetail(BaseModel):
    id: int


# --------------------
# Patient Knowledge
# --------------------


class PatientKnowledgeBase(BaseModel):
    glucose: Optional[float] = None
    diabetes: Optional[bool] = None
    heart_disease: Optional[bool] = None
    bmi: Optional[float] = None
    hba1c: Optional[float] = None

    smoking: Optional[bool] = None
    cigarettes_per_day: Optional[int] = None

    physical_activity: Optional[bool] = None
    stress: Optional[bool] = None
    alcohol: Optional[bool] = None
    chronic_disease: Optional[bool] = None

    prevalent_hypertension: Optional[bool] = None
    prevalent_stroke: Optional[bool] = None


class PatientKnowledgeCreate(PatientKnowledgeBase):
    pass


class PatientKnowledgeUpdate(PatientKnowledgeBase):
    pass


class PatientKnowledgeResponse(PatientKnowledgeBase):
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# --------------------
# Patient Heart Disease
# --------------------


class PatientHeartDiseaseBase(BaseModel):
    bp_meds: Optional[bool] = None
    diastolic_bp: Optional[int] = None
    systolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None

    chest_pain: Optional[str] = None
    resting_ecg: Optional[str] = None
    exercise_slope: Optional[str] = None


class PatientHeartDiseaseCreate(PatientHeartDiseaseBase):
    patient_id: int


class PatientHeartDiseaseUpdate(PatientHeartDiseaseBase):
    pass


class PatientHeartDiseaseResponse(PatientHeartDiseaseBase):
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# --------------------
# Patient Image
# --------------------


class PatientImageBase(BaseModel):
    image_path: str
    disease: Optional[str] = None


class PatientImageCreate(PatientImageBase):
    patient_id: int


class PatientImageUpdate(PatientImageBase):
    pass


class PatientImageResponse(PatientImageBase):
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# --------------------
# Result / Report (result tablosu)
# --------------------


class ResultBase(BaseModel):
    diabetes_risk: Optional[float] = None
    hypertension_risk: Optional[float] = None
    heart_disease_risk: Optional[float] = None

    diabetes_diagnosis: Optional[str] = None
    hypertension_diagnosis: Optional[str] = None
    heart_disease_diagnosis: Optional[str] = None

    source: Optional[str] = None
    result: Optional[str] = None


class ReportCreate(ResultBase):
    patient_id: int


class ReportUpdate(ResultBase):
    pass


class ReportResponse(ResultBase):
    id: int
    patient_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# --------------------
# Toplu hasta detayı (istersen kullanırsın)
# --------------------


class PatientDetailResponse(PatientResponse):
    knowledge: Optional[PatientKnowledgeResponse] = None
    heart_disease: Optional[PatientHeartDiseaseResponse] = None
    images: List[PatientImageResponse] = []
    results: List[ReportResponse] = []


# --------------------
# Ask / Analyze
# --------------------


class AskRequest(BaseModel):
    patient_id: int
    question: str


class AnalyzeRequest(BaseModel):
    patient_id: int

from pydantic import BaseModel
from typing import Optional, List


class ReportCreate(BaseModel):
    patient_id: int


class ReportPatient(BaseModel):
    id: int
    national_id: str
    full_name: str
    complaint: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

    model_config = {"from_attributes": True}


class ReportKnowledge(BaseModel):
    glucose: Optional[float] = None
    diabetes: Optional[bool] = None
    heart_disease: Optional[bool] = None
    bmi: Optional[float] = None
    hba1c: Optional[float] = None
    smoking: Optional[bool] = None
    cigarettes_per_day: Optional[int] = None
    physical_activity: Optional[bool] = None
    stress: Optional[bool] = None
    alcohol: Optional[bool] = None
    chronic_disease: Optional[bool] = None
    total_cholesterol: Optional[float] = None
    prevalent_hypertension: Optional[bool] = None
    prevalent_stroke: Optional[bool] = None

    model_config = {"from_attributes": True}


class ReportHeart(BaseModel):
    bp_meds: Optional[bool] = None
    diastolic_bp: Optional[int] = None
    systolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None
    chest_pain: Optional[str] = None
    resting_ecg: Optional[str] = None
    exercise_slope: Optional[str] = None

    model_config = {"from_attributes": True}


class ReportImage(BaseModel):
    id: int
    image_path: str
    disease: Optional[str] = None

    model_config = {"from_attributes": True}


class ReportResult(BaseModel):
    diabetes_risk: Optional[float] = None
    hypertension_risk: Optional[float] = None
    heart_disease_risk: Optional[float] = None

    diabetes_diagnosis: Optional[str] = None
    hypertension_diagnosis: Optional[str] = None
    heart_disease_diagnosis: Optional[str] = None

    source: Optional[str] = None
    result: Optional[str] = None  # uzun text summary

    model_config = {"from_attributes": True}


class ReportResponse(BaseModel):
    patient: ReportPatient
    knowledge: Optional[ReportKnowledge] = None
    heart: Optional[ReportHeart] = None
    images: List[ReportImage] = []
    result: Optional[ReportResult] = None
