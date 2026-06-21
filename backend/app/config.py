from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Blood Reach BD"
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15
    CORS_ORIGINS: list[str] = ["http://localhost:5500"]

    class Config:
        env_file = ".env"


settings = Settings()
