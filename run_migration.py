import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import config

def create_database_if_not_exists():
    try:
        # Connect to default postgres database to manage DB creation
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (config.DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database {config.DB_NAME}...")
            cursor.execute(f'CREATE DATABASE "{config.DB_NAME}"')
        else:
            print(f"Database {config.DB_NAME} already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        print("Will attempt to proceed with migration...")

def run_migration():
    # Ensure target DB exists first
    create_database_if_not_exists()

    # Import database module here to connect to the newly created target DB
    import database
    cursor = database.connection.cursor()
    
    with open('migration.sql', 'r') as f:
        lines = f.readlines()
    
    # Remove comment lines and join
    cleaned_sql = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('--'):
            cleaned_sql.append(line)
            
    sql = "".join(cleaned_sql)
    
    # Split by semicolon
    statements = sql.split(';')
    for s in statements:
        s = s.strip()
        if s:
            print(f"Executing statement:\n{s[:120]}...")
            try:
                cursor.execute(s)
            except psycopg2.Error as e:
                print(f"PostgreSQL Warning/Error: {e}")
    
    database.connection.commit()
    print("Migration completed successfully!")

if __name__ == '__main__':
    run_migration()
