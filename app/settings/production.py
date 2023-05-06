from dotenv import load_dotenv
from app.settings.base import BaseSettings

load_dotenv()

class ProductionSettings(BaseSettings):
    @property
    def LOG_LEVEL(self):
        return "INFO"
