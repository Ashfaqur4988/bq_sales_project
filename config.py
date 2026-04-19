from dotenv import load_dotenv
import os

load_dotenv()
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-123")
DATABASE_URL = "postgresql+psycopg2://postgres:your_strong_password@34.131.86.254:5432/sales-db"
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False