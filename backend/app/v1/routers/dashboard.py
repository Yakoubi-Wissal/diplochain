"""
routers/dashboard.py — Endpoints pour le Dashboard Super‑Admin (v6)
Contient les métriques journalières et les vues agrégées des diplômes
par étudiant / institution.  Les URLs sont préfixées par `/admin`.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user, require_role
from database import get_db
from models import DashboardMetricsDaily
from schemas import (
    DashboardMetricsRead,
    DiplomasPerStudent,
    DiplomasPerInstitution,
)

router = APIRouter(prefix="/admin", tags=["Dashboard"])


@router.get(
    "/metrics",
    response_model=List[DashboardMetricsRead],
    summary="Récupère les métriques quotidiennes (SUPER_ADMIN uniquement)",
)
async def get_metrics(
    date: Optional[date] = Query(None, description="Filtrer sur une date précise"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    # ADMIN_INSTITUTION verra normalement les métriques de sa propre institution
    # grâce aux politiques RLS; l'application ne fait pas de filtre supplémentaire.
    query = select(DashboardMetricsDaily)
    if date:
        query = query.where(DashboardMetricsDaily.metric_date == date)
    result = await db.execute(query.order_by(DashboardMetricsDaily.metric_date.desc()))
    return result.scalars().all()


@router.post(
    "/metrics/refresh",
    summary="Force le recalcul des métriques journalières",
)
async def refresh_metrics(
    target_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN")),
):
    # call the database function; the SQL takes care of idempotence
    d = target_date or date.today()
    await db.execute(text("SELECT fn_refresh_dashboard_metrics(:d)"), {"d": d})
    # session will be committed by the get_db dependency
    return {"status": "ok", "refreshed_for": d.isoformat()}


@router.get(
    "/students",
    response_model=List[DiplomasPerStudent],
    summary="Classement des étudiants par nombre de diplômes",
)
async def students_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    result = await db.execute(text("SELECT * FROM v_diplomas_per_student"))
    rows = result.mappings().all()
    return [DiplomasPerStudent(**row) for row in rows]


@router.get(
    "/institutions",
    response_model=List[DiplomasPerInstitution],
    summary="Classement des institutions par volume de diplômes",
)
async def institutions_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("SUPER_ADMIN", "ADMIN_INSTITUTION")),
):
    result = await db.execute(text("SELECT * FROM v_diplomas_per_institution"))
    rows = result.mappings().all()
    return [DiplomasPerInstitution(**row) for row in rows]
