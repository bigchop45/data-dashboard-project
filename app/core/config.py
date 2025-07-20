from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Real-Time Data Dashboard API"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()