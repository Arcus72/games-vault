# Postgres 18 (backup was dumped with 18.6) with pgvector preinstalled
FROM pgvector/pgvector:pg18

# Copy the backup file to /tmp
COPY GamesVault_DB.backup /tmp/GamesVault_DB.backup

# Copy the init script to entrypoint directory
COPY restore.sh /docker-entrypoint-initdb.d/restore.sh

RUN chmod +x /docker-entrypoint-initdb.d/restore.sh