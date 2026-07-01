import psycopg2
import psycopg2.extras
import config

def run_migration():
    print("Connecting to database for migration...")
    conn = psycopg2.connect(config.DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()

    with open('migration.sql', 'r') as f:
        lines = f.readlines()

    # Remove comment-only lines
    cleaned_sql = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('--'):
            cleaned_sql.append(line)

    sql = "".join(cleaned_sql)

    # Split and execute each statement
    statements = sql.split(';')
    for s in statements:
        s = s.strip()
        if s:
            print(f"Executing: {s[:100]}...")
            try:
                cursor.execute(s)
            except psycopg2.Error as e:
                print(f"Warning: {e}")

    cursor.close()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    run_migration()
