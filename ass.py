# create_feedback_table_psycopg2.py

import psycopg2
from psycopg2 import sql

# ---------------- PostgreSQL Credentials ----------------
DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USERNAME = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACЬ"
DB_NAME = "gssp_common"
DB_SESSION_ROLE = "citi_pg_app_owner"
SCHEMA_NAME = "gssp_common"
TABLE_NAME = "Feedback"

# ---------------- SQL Statements ----------------
CREATE_SCHEMA_SQL = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(SCHEMA_NAME))

CREATE_TABLE_SQL = sql.SQL("""
CREATE TABLE IF NOT EXISTS {}.{} (
    id SERIAL PRIMARY KEY,
    Application_Id VARCHAR NOT NULL,
    correlation_id VARCHAR NOT NULL,
    content JSON NOT NULL,
    soeid VARCHAR NOT NULL,
    authorization_coin_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
)
""").format(sql.Identifier(SCHEMA_NAME), sql.Identifier(TABLE_NAME))

# ---------------- Connect and Execute ----------------
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Set session role
    cursor.execute(f"SET ROLE {DB_SESSION_ROLE};")

    # Create schema
    cursor.execute(CREATE_SCHEMA_SQL)
    print(f"Schema ensured: {SCHEMA_NAME}")

    # Create table
    cursor.execute(CREATE_TABLE_SQL)
    print(f"Table created: {SCHEMA_NAME}.{TABLE_NAME}")

except Exception as e:
    print(f"Error creating table: {e}")

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
 
