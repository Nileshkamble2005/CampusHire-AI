import os
from dotenv import load_dotenv

load_dotenv()

# Single database URL for both local and Render/Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "campushire_ai_secret_key"
)