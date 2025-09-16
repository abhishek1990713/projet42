from fastapi import FastAPI, UploadFile, File, HTTPException
import json
import uvicorn

from db import insert_feedback_to_db
from setup_log import logger

app = FastAPI(title="Feedback API", version="1.0")


@app.post("/upload-json")
async def upload_json(file: UploadFile = File(...)):
    """
    API endpoint to upload a JSON file and insert its content into PostgreSQL.

    Args:
        file (UploadFile): JSON file uploaded by the user.

    Returns:
        dict: A success message on successful insert.

    Raises:
        HTTPException: If file is not JSON or database insert fails.
    """
    try:
        if not file.filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Only JSON files are allowed")

        # Read file content
        content = await file.read()
        data = json.loads(content)

        # Extract required fields
        application_id = data.get("x-application-id")
        consumer_id = data.get("x-correlation-id")

        if not application_id or not consumer_id:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: x-application-id or x-correlation-id"
            )

        # Insert into DB
        insert_feedback_to_db(application_id, consumer_id, data)

        return {"message": "Feedback JSON inserted successfully"}

    except json.JSONDecodeError:
        logger.error("Invalid JSON file uploaded")
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        logger.error(f"Error inserting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    """
    Entry point for running the FastAPI app directly with Python.
    Runs Uvicorn server on host 0.0.0.0 and port 9000.
    """
    uvicorn.run("fast:app", host="0.0.0.0", port=9000, reload=True)


import os
import psycopg2
import json
from dotenv import load_dotenv
from setup_log import logger

# Load environment variables from .env file
load_dotenv()


def get_connection():
    """
    Establish a PostgreSQL connection using environment variables.

    Returns:
        psycopg2.extensions.connection: A PostgreSQL connection object.

    Raises:
        Exception: If connection to the database fails.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME"),
        )
        logger.info("Database connection established successfully")

        # Set DB session role
        role = os.getenv("DB_SESSION_ROLE")
        if role:
            with conn.cursor() as cursor:
                cursor.execute(f"SET ROLE {role};")
            logger.info(f"Database role set to {role}")

        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise


def insert_feedback_to_db(application_id: str, consumer_id: str, feedback_json: dict):
    """
    Insert feedback JSON into the feedback_json table in PostgreSQL.
    If the table does not exist, create it first.

    Args:
        application_id (str): The application ID from feedback.
        consumer_id (str): The consumer ID from feedback.
        feedback_json (dict): The full feedback JSON.

    Raises:
        Exception: If insert fails.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gssp_common.feedback_json (
                id SERIAL PRIMARY KEY,
                application_id TEXT,
                consumer_id TEXT,
                full_json JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(
            """
            INSERT INTO gssp_common.feedback_json 
            (application_id, consumer_id, full_json)
            VALUES (%s, %s, %s);
            """,
            (
                application_id,
                consumer_id,
                json.dumps(feedback_json),
            )
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("Feedback JSON inserted successfully")

    except Exception as e:
        logger.error(f"Error inserting feedback: {str(e)}")
        raise



from pydantic import BaseModel, Field
from typing import Dict, Any


class Feedback(BaseModel):
    """
    Pydantic model for validating feedback JSON structure.
    - application_id: Application ID string
    - consumer_id: Consumer ID string
    - feedback: Full JSON payload (dict)
    """
    application_id: str = Field(..., description="Unique application identifier")
    consumer_id: str = Field(..., description="Unique consumer identifier")
    feedback: Dict[str, Any] = Field(..., description="Full JSON feedback payload")

