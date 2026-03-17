from pydantic import BaseModel
from datetime import date

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
    updated_at: date

    model_config = {"from_attributes": True}
