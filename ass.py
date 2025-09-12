

import json
import psycopg2

# PostgreSQL credentials
DB_HOST = "sd-ram-k"
DB_PORT = 1524
DB_USERNAME = "Post"
DB_PASSWORD = "ppdv"
DB_NAME = "ge"
DB_SESSION_ROLE = "Pq_APP_owner"

# Path to your JSON file
JSON_FILE = "data.json"

def insert_single_json():
    try:
        # Load JSON file
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract fields
        application_id = data.get("x-application-id")
        consumer_id = data.get("x-soeid") or data.get("x-correlation-id")

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )

        with conn.cursor() as cursor:
            cursor.execute(f"SET ROLE {DB_SESSION_ROLE};")

            # Ensure table exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS json_storage (
                    id SERIAL PRIMARY KEY,
                    application_id TEXT,
                    consumer_id TEXT,
                    full_json JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Insert into DB
            cursor.execute(
                """
                INSERT INTO json_storage (application_id, consumer_id, full_json)
                VALUES (%s, %s, %s);
                """,
                (application_id, consumer_id, json.dumps(data))
            )

        conn.commit()
        conn.close()
        print("✅ JSON inserted successfully into PostgreSQL")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    insert_single_json()

