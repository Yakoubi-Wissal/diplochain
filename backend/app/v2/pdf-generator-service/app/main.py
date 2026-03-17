from fastapi import FastAPI, UploadFile, File, Form, HTTPException, APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
import io
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/pdf", tags=["PDF"])

app = FastAPI(
    title="DiploChain PDF Generator Service",
    version="1.0.0",
    description="Microservice to generate diploma PDFs without DB access"
)

class StudentData(BaseModel):
    nom: str
    prenom: str
    date_naissance: str
    numero_etudiant: str

class DiplomaData(BaseModel):
    titre: str
    mention: str
    date_emission: str
    annee_promotion: str

class InstitutionData(BaseModel):
    nom: str
    logo_url: str
    responsable: str

class GenerateRequest(BaseModel):
    template_id: str
    student: StudentData
    diploma: DiplomaData
    institution: InstitutionData

@router.post("/generate-diploma", response_class=Response)
async def generate_diploma(request: GenerateRequest):
    # This is a mockup of the PDF generation logic from the V6 architecture
    # In reality, this would use WeasyPrint or advanced ReportLab rendering
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

app.include_router(router)
