import os
from dotenv import load_dotenv
from app.settings.base import BaseSettings

load_dotenv()

class ProductionSettings(BaseSettings):
    @property
    def LOG_LEVEL(self):
        return "INFO"
    
    @property
    def S3_BUCKET_NAME(self):
        return os.getenv("S3_PROD_BUCKET_NAME")

    @property
    def OPEN_SEARCH_HOST(self):
        return os.getenv("OPEN_SEARCH_PROD_HOST")

    @property
    def OPEN_SEARCH_USERNAME(self):
        return os.getenv("OPEN_SEARCH_PROD_USERNAME")

    @property
    def OPEN_SEARCH_PASSWORD(self):
        return os.getenv("OPEN_SEARCH_PROD_PASSWORD")
    
    @property
    def OPEN_SEARCH_INDEX_NAME(self):
        return os.getenv("OPEN_SEARCH_PROD_INDEX_NAME")