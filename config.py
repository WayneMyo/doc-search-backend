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
