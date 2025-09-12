

import os
import json
import psycopg2

# PostgreSQL credentials
DB_HOST = "sd-ram-k"
DB_PORT = 1524
DB_USERNAME = "Post"
DB_PASSWORD = "ppdv"
DB_NAME = "ge"
DB_SESSION_ROLE = "Pq_APP_owner"

# Folder where JSON files are stored
JSON_FOLDER = "json_files"

def insert_json_to_postgres():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )

        with conn.cursor() as cursor:
            cursor.execute(f"SET ROLE {DB_SESSION_ROLE};")

            # Create table with 3 columns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS json_storage (
                    id SERIAL PRIMARY KEY,
                    application_id TEXT,
                    consumer_id TEXT,
                    full_json JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Loop through JSON files in folder
            for file_name in os.listdir(JSON_FOLDER):
                if file_name.endswith(".json"):
                    file_path = os.path.join(JSON_FOLDER, file_name)

                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Extract required fields
                    application_id = data.get("x-application-id")
                    consumer_id = data.get("x-soeid") or data.get("x-correlation-id")

                    # Insert into DB
                    cursor.execute(
                        """
                        INSERT INTO json_storage (application_id, consumer_id, full_json)
                        VALUES (%s, %s, %s);
                        """,
                        (application_id, consumer_id, json.dumps(data))
                    )

                    print(f"✅ Inserted {file_name} into DB")

        conn.commit()
        conn.close()
        print("🎉 All JSON files inserted successfully.")

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    insert_json_to_postgres()
