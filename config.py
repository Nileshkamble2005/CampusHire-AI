import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB", "AI_Campus_Placement")
MYSQL_SSL = os.getenv("MYSQL_SSL", "False").lower() in ("true", "1", "yes")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")