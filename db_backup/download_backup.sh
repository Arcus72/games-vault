#!/bin/bash
set -e

cd "$(dirname "$0")"
curl -f -o db_backup.backup "https://gamesvaultstorage.blob.core.windows.net/backup/gamesvault?sp=r&st=2026-11-19T12:35:16Z&se=2027-01-29T20:50:16Z&spr=https&sv=2026-02-06&sr=b&sig=gQo%2F0Nfml2UxwZFMJ%2FMtqfyVNufOR%2BGy2wJc0OIV4%2BU%3D"
