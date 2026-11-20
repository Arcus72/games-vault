@echo off
cd /d "%~dp0.."
docker compose exec -T db pg_restore -U postgres -d gamesvault --clean < db_backup\db_backup.backup
