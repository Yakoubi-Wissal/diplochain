from sqlalchemy import Column, Integer, Date, Numeric, DateTime, String
from sqlalchemy.sql import func
from core.database import Base

class DashboardMetricsDaily(Base):
    __tablename__ = "dashboard_metrics_daily"
    __table_args__ = {'extend_existing': True}

    metric_date = Column(Date, primary_key=True)
    nb_diplomes_emis = Column(Integer, nullable=False, default=0)
    nb_diplomes_microservice = Column(Integer, nullable=False, default=0)
    nb_diplomes_upload = Column(Integer, nullable=False, default=0)
    nb_nouveaux_etudiants = Column(Integer, nullable=False, default=0)
    nb_institutions_actives = Column(Integer, nullable=False, default=0)
    nb_diplomes_confirmes = Column(Integer, nullable=False, default=0)
    nb_diplomes_pending = Column(Integer, nullable=False, default=0)
    nb_diplomes_revoques = Column(Integer, nullable=False, default=0)
    nb_verifications = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, nullable=False, server_default=func.now())

class InstitutionStatistics(Base):
    __tablename__ = "institution_statistics"
    __table_args__ = {'extend_existing': True}
    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer)
    nb_students = Column(Integer)

class StudentStatistics(Base):
    __tablename__ = "student_statistics"
    __table_args__ = {'extend_existing': True}
    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer)
    nb_diplomas = Column(Integer)

class StabilityHistory(Base):
    __tablename__ = "stability_history"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now())
    stability = Column(Numeric(5, 2))
    security = Column(Numeric(5, 2))
    network = Column(Numeric(5, 2))
    anomaly = Column(Numeric(5, 2))

class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, server_default=func.now())
    service = Column(String(50))
    event_type = Column(String(50))
    details = Column(String(500))
    severity = Column(String(20)) # INFO, WARNING, CRITICAL
