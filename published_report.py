import json
from sqlalchemy import text

try:
    from .database import get_engine
except ImportError:
    from database import get_engine

DDL = """CREATE TABLE IF NOT EXISTS dashboard_publication (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    published_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    payload JSONB NOT NULL
)"""


def initialize():
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(text(DDL))
    finally:
        engine.dispose()


def publish(data, analysis, report):
    payload = json.dumps({
        "sales": json.loads(data.to_json(orient="records", date_format="iso")),
        "analysis": analysis, "report": report,
    }, allow_nan=False)
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(text(DDL))
            conn.execute(text("""INSERT INTO dashboard_publication (id, payload)
                VALUES (1, CAST(:payload AS JSONB)) ON CONFLICT (id)
                DO UPDATE SET payload = EXCLUDED.payload, published_at = clock_timestamp()"""),
                {"payload": payload})
    finally:
        engine.dispose()


def read(database_url=None, version_only=False):
    engine = get_engine(database_url)
    try:
        with engine.connect() as conn:
            columns = "published_at" if version_only else "published_at, payload"
            row = conn.execute(text(f"SELECT {columns} FROM dashboard_publication WHERE id = 1")).mappings().first()
            return dict(row) if row else None
    finally:
        engine.dispose()
