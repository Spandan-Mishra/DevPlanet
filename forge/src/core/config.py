from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FORGE_", case_sensitive=False)

    app_name: str = "DevPlanet Forge Procedural Engine"
    version: str = "0.1.0"
    port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "info"


settings = Settings()
