import psycopg2
import psycopg2.extras
import config

connection = psycopg2.connect(config.DATABASE_URL)

connection.cursor_factory = psycopg2.extras.RealDictCursor

print("Database Connected Successfully!")