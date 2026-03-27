from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://diplochain_user:diplochain_pass@postgres:5432/diplochain_db"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "diplochain_user"
    POSTGRES_PASSWORD: str = "diplochain_pass"
    POSTGRES_DB: str = "diplochain_db"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service URLs
    USER_SERVICE_URL: str = "http://user-service:8001"
    DIPLOMA_SERVICE_URL: str = "http://diploma-service:8002"
    INSTITUTION_SERVICE_URL: str = "http://institution-service:8003"
    STUDENT_SERVICE_URL: str = "http://student-service:8004"
    BLOCKCHAIN_SERVICE_URL: str = "http://blockchain-service:8005"
    STORAGE_SERVICE_URL: str = "http://storage-service:8006"
    
    # Hyperledger Fabric
    FABRIC_ORG_NAME: str = "org1"
    FABRIC_CHANNEL_NAME: str = "diplomchannel"
    FABRIC_CONTRACT_NAME: str = "diplomcontract"
    FABRIC_MSP_ID: str = "Org1MSP"
    FABRIC_WALLET_PATH: str = "/app/wallet"
    FABRIC_CONNECTION_PROFILE: str = "/app/connection-profile.yaml"
    
    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Debug
    DEBUG: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
