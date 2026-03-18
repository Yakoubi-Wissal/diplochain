from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import date

from core.database import AsyncSessionLocal
from core.models import Student
from core.schemas import StudentCreate, StudentRead

router = APIRouter(prefix="", tags=["Students"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.post("/", response_model=StudentRead)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    db_student = Student(**student.model_dump())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

@router.get("/{etudiant_id}", response_model=StudentRead)
async def read_student(etudiant_id: str, db: AsyncSession = Depends(get_db)):
    student = await db.get(Student, etudiant_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/search", response_model=list[StudentRead])
async def search_students(
    nom: Optional[str] = None, 
    prenom: Optional[str] = None,
    email_etudiant: Optional[str] = None,
    institution_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    query_str = "SELECT * FROM etudiant"
    clauses = []
    params = {}
    if nom:
        clauses.append("nom ILIKE :nom")
        params["nom"] = f"%{nom}%"
    if prenom:
        clauses.append("prenom ILIKE :prenom")
        params["prenom"] = f"%{prenom}%"
    if email_etudiant:
        clauses.append("email_etudiant ILIKE :email_etudiant")
        params["email_etudiant"] = f"%{email_etudiant}%"
    if institution_id:
        clauses.append("institution_id = :institution_id")
        params["institution_id"] = institution_id
    if clauses:
        query_str += " WHERE " + " AND ".join(clauses)
    result = await db.execute(text(query_str), params)
    return result.mappings().all()
