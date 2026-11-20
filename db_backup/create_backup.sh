#!/bin/bash
set -e

cd "$(dirname "$0")/.."
docker compose exec -T db pg_dump -U postgres -d gamesvault -F c > db_backup/db_backup.backup
