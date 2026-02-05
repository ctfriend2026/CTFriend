#!/bin/bash

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd ${SCRIPT_DIR}

echo "-- Starting backup --"

BUCKET_NAME="bucket-sep-25"

mkdir -p backups

BACKUP_FOLDER=tai_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$BACKUP_FOLDER"

mkdir -p $BACKUP_DIR
echo "Created backup directory: $BACKUP_DIR"

# backup timescale db
echo "Creating archive of TimescaleDB..."
docker exec postgres_db pg_dump -U postgres metrics | gzip > $BACKUP_DIR/metrics_db.gz

# backup prometheus data
echo "Creating archive of Prometheus data..."
SNAPSHOT_NAME=$(curl -XPOST http://localhost:9090/api/v1/admin/tsdb/snapshot \
  | jq -r '.data.name')
docker exec prometheus tar -czf - -C /prometheus/snapshots $SNAPSHOT_NAME | \
    cat > $BACKUP_DIR/prometheus_data.tar.gz

# backup grafana data
echo "Creating archive of Grafana data..."
GRAFANA_VOLUME_DIR=$(docker volume inspect ctfriend_grafana_data | jq -r '.[0].Mountpoint')
docker run --rm \
    -v "$GRAFANA_VOLUME_DIR:/data" \
    alpine:latest \
    sh -c "apk add --no-cache sqlite && \
    sqlite3 /data/grafana.db .dump > /data/grafana-dump.sql && \
    sqlite3 /data/grafana.db .schema > /data/grafana-schema.sql"

docker cp grafana:/var/lib/grafana/grafana-dump.sql $BACKUP_DIR/grafana-dump.sql
docker cp grafana:/var/lib/grafana/grafana-schema.sql $BACKUP_DIR/grafana-schema.sql

ARCHIVE_FILE="backups/$BACKUP_FOLDER.tar.gz"
echo "Creating final archive: $ARCHIVE_FILE"
tar -czf $ARCHIVE_FILE -C $BACKUP_DIR .

echo "Uploading backups to Google Cloud Storage..."
gcloud storage cp $ARCHIVE_FILE gs://$BUCKET_NAME

cd -

echo "-- Backup done --"