# utility.py

import json
import psycopg2
import configparser
from psycopg2 import sql, OperationalError
from constants import (
    APP_ID_KEY,
    CONSUMER_ID_KEY,
    SUCCESS_MSG,
    MISSING_FIELDS_MSG,
    CONFIG_FILE,
)
from setup_log import setup_logger

# -------------------- Logger --------------------
try:
    logger = setup_logger()
except Exception:
    logger = None

# -------------------- Load Config --------------------
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

DB_HOST = "sd-ram1-kmat.nam.nsroot.net"
DB_PORT = 1524
DB_USER = "postgres_dev_179442"
DB_PASSWORD = "ppdVEB9ACЬ"
DB_NAME = "gssp_common"
DB_SESSION_ROLE = "citi_pg_app_owner"
TABLE_NAME = '"Feedback"'   # quoted for Postgres case-sensitive table name


# -------------------- Database Connection --------------------
def get_connection():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
        )
        if logger:
            logger.info("Database connection established successfully.")
        return connection
    except OperationalError as e:
        if logger:
            logger.error(f"Failed to connect to the database: {e}")
        raise


# -------------------- Insert JSON --------------------
def insert_json(data: dict, authorization_coin_id: str) -> dict:
    """
    Insert JSON into PostgreSQL.
    - application_id and consumer_id come from the uploaded JSON.
    - authorization_coin_id comes from the request header.
    """
    application_id = data.get(APP_ID_KEY)
    consumer_id = data.get(CONSUMER_ID_KEY)

    # Validate
    if not application_id or not consumer_id or not authorization_coin_id:
        if logger:
            logger.error(MISSING_FIELDS_MSG)
        return {
            "success": False,
            "message": MISSING_FIELDS_MSG,
            "details": None,
        }

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # Set session role
            cursor.execute(sql.SQL("SET ROLE {};").format(sql.Identifier(DB_SESSION_ROLE)))

            # Ensure table exists
            cursor.execute(sql.SQL(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id SERIAL PRIMARY KEY,
                    application_id TEXT,
                    consumer_id TEXT,
                    authorization_coin_id TEXT,
                    feedback_json JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))

            # Insert row
            cursor.execute(
                sql.SQL(f"""
                    INSERT INTO {TABLE_NAME}
                    (application_id, consumer_id, authorization_coin_id, feedback_json)
                    VALUES (%s, %s, %s, %s);
                """),
                (application_id, consumer_id, authorization_coin_id, json.dumps(data)),
            )

            conn.commit()
            return {
                "success": True,
                "details": {
                    "message": SUCCESS_MSG,
                    "table": TABLE_NAME.strip('"'),
                    "application_id": application_id,
                    "consumer_id": consumer_id,
                    "authorization_coin_id": authorization_coin_id,
                },
            }

    except Exception as e:
        if logger:
            logger.error(f"Database operation failed: {e}")
        return {
            "success": False,
            "message": "Database operation failed.",
            "error": str(e),
        }

    finally:
        if conn:
            conn.close()
            if logger:
                logger.info("Database connection closed.")



# main.py
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from utility import insert_json
from constants import SUCCESS_MSG, INVALID_JSON_MSG
from setup_log import setup_logger
import uvicorn

# -------------------- Initialize logger --------------------
try:
    logger = setup_logger()
except Exception:
    logger = None

# -------------------- Initialize FastAPI application --------------------
app = FastAPI()


@app.post("/upload-json/")
async def upload_json(
    file: UploadFile = File(...),
    authorization_coin_id: str = Header(None, alias="Authorization-Coin-Id")
):
    """
    Upload a JSON file and insert its contents into the database.
    `authorization_coin_id` must come from request headers, not from the JSON.
    """
    if not authorization_coin_id:
        raise HTTPException(status_code=400, detail="Missing Authorization-Coin-Id header")

    try:
        # Read file
        contents = await file.read()

        # Parse JSON
        try:
            data = json.loads(contents.decode("utf-8"))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail=INVALID_JSON_MSG)

        # Insert into DB
        message = insert_json(data, authorization_coin_id)
        return {"message": message or SUCCESS_MSG}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# -------------------- Run Application --------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=9000,
        log_level="info",
        workers=4
    )

