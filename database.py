import psycopg2
import psycopg2.extras
import config

_connection = None


def get_db_url():
    """Normalize DATABASE_URL - psycopg2 requires postgresql:// scheme."""
    url = config.DATABASE_URL or ""
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Please add it to your Render environment variables."
        )
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
        cur = _connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
    except Exception:
        try:
            _connection = psycopg2.connect(
                get_db_url(),
                cursor_factory=psycopg2.extras.RealDictCursor,
                connect_timeout=10,
            )
            _connection.autocommit = False
            print("✅ Database Connected Successfully!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    return _connection


class _LazyConnection:
    """Proxy object that behaves like a psycopg2 connection."""
    def cursor(self, *args, **kwargs):
        return get_connection().cursor(*args, **kwargs)

    def commit(self):
        return get_connection().commit()

    def rollback(self):
        return get_connection().rollback()

    def close(self):
        global _connection
        if _connection:
            _connection.close()

    @property
    def closed(self):
        return _connection is None or _connection.closed


connection = _LazyConnection()