
CREATE TABLE IF NOT EXISTS public.json_storage (
    id SERIAL PRIMARY KEY,
    application_id TEXT,
    consumer_id TEXT,
    full_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
