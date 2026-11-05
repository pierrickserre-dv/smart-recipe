from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_cloud_project: str = "sandbox-pserre"
    google_cloud_location: str = "global"
    storage_bucket: str = "sandbox-pserre.firebasestorage.app"
    cors_origins: list[str] = ["http://localhost:4200"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
