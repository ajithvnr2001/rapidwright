import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()

class Settings(BaseSettings):
    glpi_url: str = Field(..., env="GLPI_URL")
    glpi_app_token: str = Field(..., env="GLPI_APP_TOKEN")
    glpi_user_token: str = Field(..., env="GLPI_USER_TOKEN")
    meilisearch_url: str = Field(..., env="MEILISEARCH_URL")
    meilisearch_master_key: str = Field(..., env="MEILISEARCH_MASTER_KEY")
    wasabi_endpoint: str = Field(..., env="WASABI_ENDPOINT")
    wasabi_access_key: str = Field(..., env="WASABI_ACCESS_KEY")
    wasabi_secret_key: str = Field(..., env="WASABI_SECRET_KEY")
    openai_api_base: str = Field(..., env="OPENAI_API_BASE")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    model_name: str = Field(..., env="MODEL_NAME")
    bucket_name: str = Field(..., env="BUCKET_NAME")
    # REMOVE THIS LINE: glpi_session_token_key: str = Field(..., env="GLPI_SESSION_TOKEN_KEY")
    max_rag_iterations: int = 3

settings = Settings()
