from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import io
from reportlab.pdfgen import canvas

app = FastAPI(title="PDF Microservice", version="1.0")

class DiplomaRequest(BaseModel):
    titre: str
    etudiant_id: str
    institution_id: int
    date_diplome: Optional[str] = None
    mention: Optional[str] = None

@app.post("/generate-diploma", response_class=bytes)
async def generate_diploma(req: DiplomaRequest):
    """Stateless PDF generation endpoint. Returns application/pdf binary."""
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, f"Diploma: {req.titre}")
        c.drawString(100, 730, f"Student ID: {req.etudiant_id}")
        c.drawString(100, 710, f"Institution ID: {req.institution_id}")
        if req.mention:
            c.drawString(100, 690, f"Mention: {req.mention}")
        if req.date_diplome:
            c.drawString(100, 670, f"Date: {req.date_diplome}")
        c.showPage()
        c.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
