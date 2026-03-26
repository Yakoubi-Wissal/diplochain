from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
import logging
from datetime import datetime, timedelta

from core.database import AsyncSessionLocal
from core.models import DashboardMetricsDaily, InstitutionStatistics, StudentStatistics, StabilityHistory, AuditEvent
from core.schemas import DashboardMetricsRead, StabilityScoreRead, AuditEventCreate, AuditEventRead

router = APIRouter(prefix="", tags=["Analytics"])
logger = logging.getLogger("analytics-service")

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.get("/metrics/daily", response_model=list[DashboardMetricsRead])
async def list_daily_metrics(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DashboardMetricsDaily))
    return result.scalars().all()

@router.get("/metrics/stability/history")
async def get_stability_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StabilityHistory).order_by(StabilityHistory.timestamp.desc()).limit(10))
    return result.scalars().all()

@router.post("/events", response_model=AuditEventRead)
async def create_audit_event(event: AuditEventCreate, db: AsyncSession = Depends(get_db)):
    db_event = AuditEvent(**event.dict())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

@router.get("/events", response_model=list[AuditEventRead])
async def list_audit_events(limit: int = 50, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit))
    return result.scalars().all()

@router.post("/security/scan")
async def receive_security_scan(scan: dict, db: AsyncSession = Depends(get_db)):
    findings = scan.get('findings', [])
    num_findings = len(findings)

    security_score = max(0, 100 - (num_findings * 10))
    stability_score = 95.0
    network_score = 98.0

    # Anomaly score based on recent non-INFO events
    event_count_result = await db.execute(select(func.count(AuditEvent.id)).where(AuditEvent.severity != "INFO"))
    event_count = event_count_result.scalar()
    anomaly_score = max(0, 100 - (event_count * 5))

    new_history = StabilityHistory(
        stability=stability_score,
        security=security_score,
        network=network_score,
        anomaly=anomaly_score
    )
    db.add(new_history)
    await db.commit()

    return {"status": "processed", "security_score": security_score}

@router.get("/metrics/stability", response_model=StabilityScoreRead)
async def get_stability_metrics(db: AsyncSession = Depends(get_db)):
    # 1. Fetch latest raw scores
    result = await db.execute(select(StabilityHistory).order_by(StabilityHistory.timestamp.desc()).limit(1))
    latest = result.scalar_one_or_none()

    # 2. Rule-based "AI" Recommendations
    recommendations = []

    # Check for brute force (many login failures in last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    login_fails = await db.execute(select(func.count(AuditEvent.id)).where(
        AuditEvent.event_type == "LOGIN_FAILED",
        AuditEvent.timestamp >= one_hour_ago
    ))
    if login_fails.scalar() > 5:
        recommendations.append("Potential brute force attack detected on user-service")

    # Check for service instability (frequent auto-heals)
    auto_heals = await db.execute(select(func.count(AuditEvent.id)).where(
        AuditEvent.event_type == "AUTO_FIX_SUCCESS",
        AuditEvent.timestamp >= one_hour_ago
    ))
    if auto_heals.scalar() > 2:
        recommendations.append("Frequent service instability detected; auto-healing triggered multiple times")

    # Check for upload failures
    upload_fails = await db.execute(select(func.count(AuditEvent.id)).where(
        AuditEvent.event_type == "FILE_UPLOAD_FAILURE",
        AuditEvent.timestamp >= one_hour_ago
    ))
    if upload_fails.scalar() > 0:
        recommendations.append("Storage service experiencing upload failures; check IPFS node connectivity")

    if not recommendations:
        if latest and latest.security < 100:
            recommendations.append("Apply missing security headers to improve integrity score")
        else:
            recommendations.append("System is performing within optimal parameters")

    if latest:
        return {
            "stability": float(latest.stability),
            "security": float(latest.security),
            "network": float(latest.network),
            "anomaly": float(latest.anomaly),
            "recommendations": recommendations
        }

    return {
        "stability": 100.0, "security": 100.0, "network": 100.0, "anomaly": 100.0,
        "recommendations": ["Initializing monitoring..."]
    }
