import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "AI_Campus_Placement")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "campushire_ai_secret_key"
)