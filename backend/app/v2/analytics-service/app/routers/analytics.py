from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import logging
from datetime import datetime

from core.database import AsyncSessionLocal
from core.models import DashboardMetricsDaily, InstitutionStatistics, StudentStatistics, StabilityHistory
from core.schemas import DashboardMetricsRead, StabilityScoreRead

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
    from sqlalchemy import select
    result = await db.execute(select(DashboardMetricsDaily))
    return result.scalars().all()

@router.get("/metrics/stability/history")
async def get_stability_history(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(StabilityHistory).order_by(StabilityHistory.timestamp.desc()).limit(10))
    return result.scalars().all()

@router.post("/security/scan")
async def receive_security_scan(scan: dict, db: AsyncSession = Depends(get_db)):
    # Process scan findings and update security scores
    findings = scan.get('findings', [])
    num_findings = len(findings)
    logger.info(f"Received security scan findings: {num_findings}")

    # Simple heuristic for scores
    security_score = max(0, 100 - (num_findings * 10))
    stability_score = 95.0 # Placeholder
    network_score = 98.0   # Placeholder
    anomaly_score = 90.0   # Placeholder

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
    # Fetch the latest metrics from history
    result = await db.execute(select(StabilityHistory).order_by(StabilityHistory.timestamp.desc()).limit(1))
    latest = result.scalar_one_or_none()

    if latest:
        return {
            "stability": float(latest.stability),
            "security": float(latest.security),
            "network": float(latest.network),
            "anomaly": float(latest.anomaly),
            "recommendations": [
                "Upgrade user-service dependency 'httpx' to 0.27+",
                "Enable IPFS garbage collection to save 2.4GB"
            ]
        }

    # Default if no history yet
    return {
        "stability": 100.0,
        "security": 100.0,
        "network": 100.0,
        "anomaly": 100.0,
        "recommendations": ["System initialized. Waiting for first scan..."]
    }
