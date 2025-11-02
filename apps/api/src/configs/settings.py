from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str

    class Config:
        env_file = ".env.dev"


settings = Settings()
