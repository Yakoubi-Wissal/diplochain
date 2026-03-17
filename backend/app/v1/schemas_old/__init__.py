# schemas/__init__.py

from .schemas import (
    # AUTH
    LoginRequest,
    TokenResponse,

    # USER
    UserBase,
    UserCreate,
    UserUpdate,
    UserRead,

    # ROLE
    RoleBase,
    RoleCreate,
    RoleRead,

    # INSTITUTION
    InstitutionBase,
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionRead,

    # SPECIALITE
    SpecialiteBase,
    SpecialiteCreate,
    SpecialiteRead,

    # DIPLOME
    DiplomeBase,
    DiplomeCreate,
    DiplomeRead,
    DiplomeUpdateStatut,

    # HISTORIQUE
    HistoriqueOperationCreate,
    HistoriqueOperationRead,

    # QR CODE
    QrCodeRead,

    # ENTREPRISE
    EntrepriseBase,
    EntrepriseCreate,
    EntrepriseRead,
    EntrepriseValidationAction,

    # DASHBOARD
    DashboardMetricsRead
)