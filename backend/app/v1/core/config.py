from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME:    str  = "DiploChain API"
    APP_VERSION: str  = "6.0.0"
    DEBUG:       bool = True

    # ── Base de données ───────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT ───────────────────────────────────────────────────────────────────
    SECRET_KEY:                  str
    ALGORITHM:                   str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS:   int = 7

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # ── IPFS ──────────────────────────────────────────────────────────────────
    IPFS_HOST:    str = "ipfs"
    IPFS_PORT:    int = 5001
    IPFS_TIMEOUT: int = 30

    # ── Hyperledger Fabric ────────────────────────────────────────────────────
    FABRIC_GATEWAY_HOST:    str  = "fabric-gateway"
    FABRIC_GATEWAY_PORT:    int  = 7051
    FABRIC_CHANNEL_DEFAULT: str  = "channel-esprit"
    FABRIC_CHAINCODE_NAME:  str  = "diplochain-cc"
    FABRIC_STUB_MODE:       bool = True   # True = mode simulation sans Fabric réel

    # ── Microservice PDF ▶ NOUVEAU v6 ─────────────────────────────────────────
    PDF_SERVICE_URL:         str = "http://diploma-generator:8001"
    PDF_SERVICE_TIMEOUT:     int = 30
    PDF_SERVICE_MAX_RETRIES: int = 3

    # ── Retry Worker ▶ NOUVEAU v6 ─────────────────────────────────────────────
    RETRY_WORKER_INTERVAL_SECONDS: int = 60
    RETRY_WORKER_MAX_RETRIES:      int = 5
    RETRY_WORKER_BATCH_SIZE:       int = 20

    # ── Dashboard métriques ▶ NOUVEAU v6 ──────────────────────────────────────
    METRICS_REFRESH_INTERVAL_HOURS: int = 1

    # ── Email SMTP ────────────────────────────────────────────────────────────
    SMTP_HOST:     str = "smtp.mailgun.org"
    SMTP_PORT:     int = 587
    SMTP_USER:     str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM:     str = "DiploChain <no-reply@diplochain.com>"

    # ── Frontend (QR codes) ───────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    # ── Azure AD (Entreprise) ─────────────────────────────────────────────────
    AZURE_AD_TENANT_ID:     str = ""
    AZURE_AD_CLIENT_ID:     str = ""
    AZURE_AD_CLIENT_SECRET: str = ""
    AZURE_AD_AUDIENCE:      str = "api://diplochain"

    class Config:
        env_file = ".env"


settings = Settings()
