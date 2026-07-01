import psycopg2
import psycopg2.extras
import config

_connection = None

def get_db_url():
    """Normalize DATABASE_URL - psycopg2 requires postgresql:// scheme."""
    url = config.DATABASE_URL or ""
    # Render/Neon sometimes provide 'psql://' or 'postgres://' — normalize both
    if url.startswith("psql://"):
        url = url.replace("psql://", "postgresql://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

def get_connection():
    """Return a live database connection, reconnecting if needed."""
    global _connection
    try:
        if _connection is None or _connection.closed:
            raise psycopg2.OperationalError("No connection")
        # Quick liveness check
        _connection.cursor().execute("SELECT 1")
    except Exception:
        _connection = psycopg2.connect(
            get_db_url(),
            cursor_factory=psycopg2.extras.RealDictCursor,
            connect_timeout=10,
        )
        _connection.autocommit = False
        print("Database Connected Successfully!")
    return _connection

# Backwards-compatible alias so existing `from database import connection`
# imports still work — but now returns a live connection on every call
class _LazyConnection:
    """Proxy object that behaves like a psycopg2 connection."""
    def cursor(self, *args, **kwargs):
        return get_connection().cursor(*args, **kwargs)

    def commit(self):
        return get_connection().commit()

    def rollback(self):
        return get_connection().rollback()

    def close(self):
        if _connection:
            _connection.close()

    @property
    def closed(self):
        return _connection is None or _connection.closed

connection = _LazyConnection()