import database
import pymysql

def run_migration():
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
            except pymysql.Error as e:
                err_code = e.args[0] if len(e.args) > 0 else None
                # 1060: Duplicate column name
                # 1091: Can't drop key (does not exist)
                # 1061: Duplicate key name
                # 1826: Duplicate foreign key constraint
                # 1050: Table already exists
                if err_code in (1060, 1091, 1061, 1826, 1050):
                    print(f"Warning (ignored): {e}")
                else:
                    print(f"Error executing statement: {e}")
                    raise e
    
    database.connection.commit()
    print("Migration completed successfully!")

if __name__ == '__main__':
    run_migration()
