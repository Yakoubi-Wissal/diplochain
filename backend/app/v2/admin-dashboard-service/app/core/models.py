from sqlalchemy import Column, Integer, Date, String, DateTime
from datetime import date, datetime
from .database import Base

class DashboardMetricsDaily(Base):
    __tablename__ = "dashboard_metrics_daily"

    metric_date = Column(Date, primary_key=True)
    nb_diplomes_emis = Column(Integer, default=0)
    nb_diplomes_microservice = Column(Integer, default=0)
    nb_diplomes_upload = Column(Integer, default=0)
    nb_nouveaux_etudiants = Column(Integer, default=0)
    nb_institutions_actives = Column(Integer, default=0)
    nb_diplomes_confirmes = Column(Integer, default=0)
    nb_diplomes_pending = Column(Integer, default=0)
    nb_diplomes_revoques = Column(Integer, default=0)
    nb_verifications = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)
