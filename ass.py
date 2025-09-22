# create_feedback_table.py

from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, func, MetaData, Table
from sqlalchemy_utils import database_exists, create_database

# ---------------- PostgreSQL Credentials ----------------
DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USERNAME = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACЬ"
DB_NAME = "gssp_common"
DB_SESSION_ROLE = "citi_pg_app_owner"

DB_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ---------------- Create Engine ----------------
engine = create_engine(DB_URL)

# ---------------- Ensure Database Exists ----------------
if not database_exists(engine.url):
    create_database(engine.url)
    print(f"Database created: {DB_NAME}")

# ---------------- Metadata ----------------
SCHEMA_NAME = "gssp_common"
TABLE_NAME = "Feedback"
metadata = MetaData(schema=SCHEMA_NAME)

# ---------------- Define Feedback Table ----------------
feedback_table = Table(
    TABLE_NAME,
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("Application_Id", String, nullable=False),
    Column("correlation_id", String, nullable=False),
    Column("content", JSON, nullable=False),
    Column("soeid", String, nullable=False),
    Column("authorization_coin_id", String, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)

# ---------------- Create Schema & Table ----------------
with engine.connect() as conn:
    # Set session role if needed
    conn.execute(f"SET ROLE {DB_SESSION_ROLE};")
    # Create schema if it doesn't exist
    conn.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};")
    print(f"Schema ensured: {SCHEMA_NAME}")

    # Create table
    metadata.create_all(bind=engine)
    print(f"Table created: {SCHEMA_NAME}.{TABLE_NAME}")
    
