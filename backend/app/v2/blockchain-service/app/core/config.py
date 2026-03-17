from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    FABRIC_GATEWAY_HOST: str
    FABRIC_GATEWAY_PORT: int
    FABRIC_CHANNEL: str = "channel-esprit"
    FABRIC_CHAINCODE: str = "diplochain-cc"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()