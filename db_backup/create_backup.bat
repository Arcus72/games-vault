@echo off
cd /d "%~dp0.."
docker compose exec -T db pg_dump -U postgres -d gamesvault -F c > db_backup\db_backup.backup
