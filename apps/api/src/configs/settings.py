from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    APP_USERNAME: str
    APP_PASSWORD: str
    WALLABAG_ENABLED: bool
    WALLABAG_URL: str
    WALLABAG_CLIENT_ID: str
    WALLABAG_CLIENT_SECRET: str
    WALLABAG_USERNAME: str
    WALLABAG_PASSWORD: str

    class Config:
        env_file = ".env.dev"


settings = Settings()
