#!/bin/bash
set -e

# DB configurations
DB_NAME=$(cat /run/secrets/db_name)
DB_USER=$(cat /run/secrets/db_user)
DB_PASSWORD=$(cat /run/secrets/db_password)

# Telegram configurations
TELEGRAM_BOT_TOKEN="$TG_AUTOBOT_TOKEN"
TELEGRAM_CHAT_ID="$TG_CHAT_ID"

# general configurations
BACKUP_DIR="/backups"
RETENTION_DAYS=30
SLEEP_INTERVAL=604800  # 1 week (in seconds)

# function for sending tg-messages
send_telegram_report() {
  local message="$1"
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${TELEGRAM_CHAT_ID}" \
      -d text="${message}" \
      -d parse_mode="Markdown"
}

# creating a backup
mkdir -p "$BACKUP_DIR"

while true; do
  TIMESTAMP=$(date +%F_%H-%M-%S)
  BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

  echo "[INFO] Starting backup: $BACKUP_FILE"
  PGPASSWORD=$DB_PASSWORD pg_dump -U "$DB_USER" -h db "$DB_NAME" | gzip > "$BACKUP_FILE"

  if [ $? -eq 0 ]; then
    echo "[INFO] Backup successful created: $BACKUP_FILE"

    echo "[INFO] Uploading backup to Google Drive..."
    python3 /usr/local/bin/upload_to_drive.py "$BACKUP_FILE"

    send_telegram_report "✅ *Backup Complete!* The database *${DB_NAME}* is successfully saved at \`$(date)\`."

  else
    echo "[ERROR] Backup failed!"
    rm -f "$BACKUP_FILE"
    send_telegram_report "🚨 *Backup Failed!* Could not back up database *${DB_NAME}* at \`$(date)\`."
  fi

  echo "[INFO] Removing backups older than $RETENTION_DAYS days..."
  find "$BACKUP_DIR" -type f -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -exec rm {} \;

  echo "[INFO] Backup cycle complete. Sleeping for $((SLEEP_INTERVAL / 3600 / 24)) days..."
  sleep $SLEEP_INTERVAL
done
