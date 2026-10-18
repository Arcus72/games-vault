FROM postgres:17-alpine

# Copy the backup file to /tmp
COPY GamesVault_DB.backup /tmp/GamesVault_DB.backup

# Copy the init script to entrypoint directory
COPY restore.sh /docker-entrypoint-initdb.d/restore.sh

RUN chmod +x /docker-entrypoint-initdb.d/restore.sh