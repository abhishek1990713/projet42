@app.on_event("startup")
def create_db_and_tables():
    try:
        # Optional: Create DB if it does not exist
        if not database_exists(engine.url):
            create_database(engine.url)
            logger.info(DB_CREATED.format(DB_NAME))

        # Create schema if it does not exist
        with engine.connect() as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS gssp_common;")

        models.Base.metadata.create_all(bind=engine)
        logger.info(DB_TABLES_CREATED)

    except Exception as e:
        logger.error(DB_INIT_FAILURE.format(e))
        raise RuntimeError(DB_INIT_FAILURE_RUNTIME) from e
 
