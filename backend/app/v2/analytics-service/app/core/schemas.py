from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class DashboardMetricsRead(BaseModel):
    metric_date: date
    nb_diplomes_emis: int
    nb_diplomes_microservice: int
    nb_diplomes_upload: int
    nb_nouveaux_etudiants: int
    nb_institutions_actives: int
    nb_diplomes_confirmes: int
    nb_diplomes_pending: int
    nb_diplomes_revoques: int
    nb_verifications: int
    updated_at: datetime

    model_config = {"from_attributes": True}

class StabilityScoreRead(BaseModel):
    stability: float
    security: float
    network: float
    anomaly: float
    recommendations: List[str]

    model_config = {"from_attributes": True}

class AuditEventCreate(BaseModel):
    service: str
    event_type: str
    details: str
    severity: str = "INFO"

class AuditEventRead(AuditEventCreate):
    id: int
    timestamp: datetime

    model_config = {"from_attributes": True}
