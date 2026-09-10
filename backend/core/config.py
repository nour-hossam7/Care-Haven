from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:4b"
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:8501,http://127.0.0.1:8501"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        if not self.SECRET_KEY.strip():
            raise ValueError("SECRET_KEY must be set to a non-empty value")
        return self

    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()