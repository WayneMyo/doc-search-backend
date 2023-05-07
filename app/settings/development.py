import os
from dotenv import load_dotenv
from app.settings.base import BaseSettings

load_dotenv()

class DevelopmentSettings(BaseSettings):
    @property
    def LOG_LEVEL(self):
        return "DEBUG"
    
    @property
    def S3_BUCKET_NAME(self):
        return os.getenv("S3_DEV_BUCKET_NAME")
    
    @property
    def OPEN_SEARCH_HOST(self):
        return os.getenv("OPEN_SEARCH_DEV_HOST")

    @property
    def OPEN_SEARCH_USERNAME(self):
        return os.getenv("OPEN_SEARCH_DEV_USERNAME")

    @property
    def OPEN_SEARCH_PASSWORD(self):
        return os.getenv("OPEN_SEARCH_DEV_PASSWORD")
    
    @property
    def OPEN_SEARCH_INDEX_NAME(self):
        return os.getenv("OPEN_SEARCH_DEV_INDEX_NAME")
