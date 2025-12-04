import os
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from .models import Base
from . import patients as patient_crud
from . import reports as report_crud
from . import ai as ai_module
from . import schemas
from .schemas import AskRequest
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="MedNexus",
    version="1.0.0",
    description="MedNexus patient & AI analysis backend",
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CustomStaticFiles(StaticFiles):
    def is_corrupted(self, path):
        return False
    
    async def get_response(self, path, scope):
        response =await super().get_response(path, scope)
        if path.endswith(".js"):
            response.headers["Content-Type"] = "application/javascript"
        return response

app.mount("/static", CustomStaticFiles(directory=str(STATIC_DIR)), name="static")


def serve_html(name: str):
    path = STATIC_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return HTMLResponse(path.read_text(), media_type="text/html")

@app.get("/", response_class=HTMLResponse)
def page_index():
    return serve_html("index.html")

@app.get("/index", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def page_index_alias():
    return serve_html("index.html")

@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
def page_login():
    return serve_html("login.html")

@app.get("/login-patient", response_class=HTMLResponse)
@app.get("/login-patient.html", response_class=HTMLResponse)
def page_login_patient():
    return serve_html("login-patient.html")

@app.get("/about", response_class=HTMLResponse)
@app.get("/about.html", response_class=HTMLResponse)
def page_about():
    return serve_html("about.html")

@app.get("/contact", response_class=HTMLResponse)
@app.get("/contact.html", response_class=HTMLResponse)
def page_contact():
    return serve_html("contact.html")

@app.get("/chat", response_class=HTMLResponse)
@app.get("/chat.html", response_class=HTMLResponse)
def page_chat():
    return serve_html("chat.html")

@app.get("/chat-patient", response_class=HTMLResponse)
@app.get("/chat-patient.html", response_class=HTMLResponse)
def page_chat():
    return serve_html("chat-patient.html")

@app.get("/report", response_class=HTMLResponse)
@app.get("/report.html", response_class=HTMLResponse)
def page_report():
    return serve_html("report.html")

@app.get("/home", response_class=HTMLResponse)
@app.get("/home.html", response_class=HTMLResponse)
def page_home():
    return serve_html("home.html")



@app.get("/detail/{patient_id}", response_class=HTMLResponse)
@app.get("/detail.html/{patient_id}", response_class=HTMLResponse)
def page_detail(patient_id: int):
    return serve_html("detail.html")

@app.get("/api/patient-list", response_model=list[schemas.PatientResponse])
def patient_list(db: Session = Depends(get_db)):
    return patient_crud.get_patients(db)

@app.get("/api/patient/{patient_id}")
def patient_detail(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.post("/api/create-patient", response_model=schemas.PatientCreate)
def create_patient(req: schemas.PatientCreate, db: Session = Depends(get_db)):
    return patient_crud.create_patient(db, req)

@app.post("/api/patient/{patient_id}/knowledge")
def add_knowledge(patient_id: int, req: schemas.PatientKnowledgeCreate, db: Session = Depends(get_db)):
    return patient_crud.create_or_update_knowledge(db, patient_id, req)

@app.put("/api/update-patient/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(patient_id: int, req: schemas.PatientUpdate, db: Session = Depends(get_db)):
    updated = patient_crud.update_patient(db, patient_id, req)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated

@app.delete("/api/delete-patient/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    deleted = patient_crud.soft_delete_patient(db, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted"}

@app.get("/api/patient/{patient_id}/reports", response_model=list[schemas.ReportResponse])
def patient_reports(patient_id: int, db: Session = Depends(get_db)):
    return report_crud.get_reports_by_patient(db, patient_id)

@app.post("/api/report", response_model=schemas.ReportResponse)
def create_report(req: schemas.ReportCreate, db: Session = Depends(get_db)):
    return report_crud.create_report(db, req)

@app.get("/api/report/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
        a =  report_crud.create_report(db,report_id)
        return  a

@app.delete("/api/report/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    deleted = report_crud.soft_delete_report(db, report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted"}

@app.post("/api/ask")
def ask_patient(request: AskRequest, db: Session = Depends(get_db)):
    return ai_module.ask(
        db=db,
        question=request.question,
        patient_id=request.patient_id,
        is_doctor=request.is_doctor
    )
