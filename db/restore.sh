#!/bin/bash
set -e

pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists /tmp/GamesVault_DB.backup || true