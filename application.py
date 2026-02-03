# ---------------------------------------------------
# Storage Backend Configuration
# ---------------------------------------------------
storageBackend: "mongo"   # Options: "mongo" or "postgres"

# ---------------------------------------------------
# PostgreSQL Configuration
# Used only when storageBackend is set to "postgres"
# ---------------------------------------------------
postgres:
  enabled: false

  # Inline connection string (optional)
  connectionString: ""

  # Connection pool settings
  poolSize: 5
  maxOverflow: 10

  # Reference an existing Kubernetes Secret (recommended for UAT/PROD)
  existingSecret: ""
  secretKey: "POSTGRES_CONNECTION_STRING"
