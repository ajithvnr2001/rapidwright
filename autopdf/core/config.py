import os
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()

class Settings(BaseSettings):
    glpi_url: str = "https://ltimindtree.in1.glpi-network.cloud"
    glpi_app_token: str = "bnVEfEQ6n7kYpzFCEiF1UgCCWJkd5bWyU7UiQXd3"
    glpi_user_token: str = "hN04d5lgFrkmprGz183sPfUhXt04102DF10pUFsN"
    meilisearch_url: str = "https://ms-6c0bfee744cb-18789.nyc.meilisearch.io"
    meilisearch_master_key: str = "289e33eaa93280a3955fbed03a73fce65048d51c"
    wasabi_endpoint: str = "s3.ap-northeast-1.wasabisys.com"
    wasabi_access_key: str = "WFDR91CL1S6EII3LFKHV"
    wasabi_secret_key: str = "rGnTDbiXOm3IFpRiaAZm9jGkfXJTGpylrJbuZ0et"
    openai_api_base: str = "https://chatapi.akash.network/api/v1"
    openai_api_key: str = "sk-lw2UYlqYhjaXkboZ0pHv9A"
    model_name: str = "DeepSeek-R1"
    bucket_name: str = "rapidwrite"
    max_rag_iterations: int = 3

settings = Settings()
