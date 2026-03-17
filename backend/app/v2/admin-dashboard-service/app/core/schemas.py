from pydantic import BaseModel
from datetime import date, datetime

class DashboardMetricsDailyRead(BaseModel):
    metric_date: date
    nb_diplomes_emis: int
    nb_nouveaux_etudiants: int
    nb_institutions_actives: int
    nb_diplomes_confirmes: int
    nb_diplomes_pending: int
    updated_at: datetime
    
    model_config = {"from_attributes": True}
