import psycopg2
import psycopg2.extras
import config

connection = psycopg2.connect(
    host=config.DB_HOST,
    port=config.DB_PORT,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME
)

connection.cursor_factory = psycopg2.extras.RealDictCursor

print("Database Connected Successfully!")