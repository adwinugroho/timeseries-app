import os


class Config:
    APP_NAME = os.getenv("APP_NAME", "timeseries-app")
    APP_ENV = os.getenv("APP_ENV", "local")
    PORT = os.getenv("PORT", "9003")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
