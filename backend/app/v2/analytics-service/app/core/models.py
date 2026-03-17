from sqlalchemy import Column, Integer, Date, Numeric, DateTime
from sqlalchemy.sql import func
from core.database import Base

class DashboardMetricsDaily(Base):
    __tablename__ = "dashboard_metrics_daily"

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
    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    institution_id = Column(Integer)
    nb_students = Column(Integer)

class StudentStatistics(Base):
    __tablename__ = "student_statistics"
    stat_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer)
    nb_diplomas = Column(Integer)
