import os

app_env = os.environ.get("APP_ENV", "development")

if app_env == "development":
    from app.settings.development import DevelopmentSettings as Settings
elif app_env == "production":
    from app.settings.production import ProductionSettings as Settings
else:
    raise ValueError(f"Invalid APP_ENV value: {app_env}")

settings = Settings()
LOG_LEVEL = settings.LOG_LEVEL
S3_BUCKET_NAME = settings.S3_BUCKET_NAME
OPEN_SEARCH_HOST = settings.OPEN_SEARCH_HOST
OPEN_SEARCH_USERNAME = settings.OPEN_SEARCH_USERNAME
OPEN_SEARCH_PASSWORD = settings.OPEN_SEARCH_PASSWORD
OPEN_SEARCH_INDEX_NAME = settings.OPEN_SEARCH_INDEX_NAME
