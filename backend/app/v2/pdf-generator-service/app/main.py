from fastapi import FastAPI, APIRouter, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io
from reportlab.pdfgen import canvas

app = FastAPI(
    title="DiploChain PDF Generator Service",
    version="1.0.0",
    description="Microservice to generate diploma PDFs without DB access"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="", tags=["PDF"])

class StudentData(BaseModel):
    nom: str
    prenom: str
    date_naissance: Optional[str] = "N/A"      # ← optionnel
    numero_etudiant: str

class DiplomaData(BaseModel):
    titre: str
    mention: str
    date_emission: str
    annee_promotion: Optional[str] = "N/A"     # ← optionnel

class InstitutionData(BaseModel):
    nom: str
    logo_url: Optional[str] = ""               # ← optionnel
    responsable: str

class GenerateRequest(BaseModel):
    template_id: Optional[str] = "standard_v1" # ← optionnel
    student: StudentData
    diploma: DiplomaData
    institution: InstitutionData

@router.post("/generate-diploma", response_class=Response)
async def generate_diploma(request: GenerateRequest):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, f"Institution: {request.institution.nom}")
    c.drawString(100, 700, f"Diplôme: {request.diploma.titre}")
    c.drawString(100, 650, f"Délivré à: {request.student.prenom} {request.student.nom}")
    c.drawString(100, 600, f"Date: {request.diploma.date_emission}")
    c.showPage()
    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return Response(content=pdf_bytes, media_type="application/pdf")

@router.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"service": "pdf-generator-service", "status": "running"}

@app.get("/health")
async def app_health():
    return {"status": "healthy"}

app.include_router(router)