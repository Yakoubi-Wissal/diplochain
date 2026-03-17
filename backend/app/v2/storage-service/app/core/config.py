from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    IPFS_GATEWAY: str = "http://ipfs-node:8080"

    class Config:
        env_file = ".env"

settings = Settings()