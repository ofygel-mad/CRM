#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"

FILE="$BACKUP_DIR/crm_$TIMESTAMP.sql.gz"

echo "==> Backup started: $FILE"
docker compose exec -T postgres pg_dump -U crm crm | gzip > "$FILE"
echo "==> Done: $(du -sh "$FILE" | cut -f1)"

# Загрузка в S3/MinIO (если задан BACKUP_S3_BUCKET)
if [ -n "${BACKUP_S3_BUCKET:-}" ]; then
  aws s3 cp "$FILE" "s3://$BACKUP_S3_BUCKET/$(basename "$FILE")"
  echo "==> Uploaded to S3: $BACKUP_S3_BUCKET"
fi

# Удалить бэкапы старше 30 дней
find "$BACKUP_DIR" -name "crm_*.sql.gz" -mtime +30 -delete
