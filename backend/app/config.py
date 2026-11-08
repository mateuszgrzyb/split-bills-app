from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_ttl_min: int = 15
    refresh_ttl_days: int = 7
    cookie_secure: bool = False  # True behind HTTPS


SETTINGS = Settings()
