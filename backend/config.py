from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    groq_api_key: str
    drive_folder_id: str
    google_service_account_json: str = ""
    backend_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()