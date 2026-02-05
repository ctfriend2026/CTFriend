#!/bin/bash

if [[ -n "$1" ]]; then
  echo "Restoring using the archive file: $1"
else
  echo "Usage: $0 <archive-file.tar.gz>"
  exit 1
fi

SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"

cd ${SCRIPT_DIR}

echo "-- Starting restore --"

BUCKET_NAME="bucket-sep-25"

mkdir -p restore
rm -rf restore/*

# read the object archive from the bucket
ARCHIVE_FILE="restore/$1"

# download the archive from Google Cloud Storage
echo "Downloading archive from Google Cloud Storage: gs://$BUCKET_NAME/$1"
gcloud storage cp gs://$BUCKET_NAME/$1 $ARCHIVE_FILE

# extract the archive
echo "Extracting archive: $ARCHIVE_FILE"
tar -xzf $ARCHIVE_FILE -C restore/

# shut down containers
docker compose down -v
sleep 5

# restore prometheus data
docker compose up -d --build prometheus
docker compose down prometheus # to ensure a new volume is created
sleep 5

echo "Restore archive of Prometheus data..."
PROMETHEUS_DATA_DIR=$(tar -tzf restore/prometheus_data.tar.gz | head -1)
tar -xzf restore/prometheus_data.tar.gz -C restore/
PROMETHEUS_VOLUME_DIR=$(docker volume inspect ctfriend_prometheus_data | jq -r '.[0].Mountpoint')

sudo cp -r restore/${PROMETHEUS_DATA_DIR}* ${PROMETHEUS_VOLUME_DIR}
sudo chown -R 65534:65534 ${PROMETHEUS_VOLUME_DIR}

# restore grafana data
docker compose up -d --build grafana
docker compose down grafana # to ensure a new volume is created
sleep 10

echo "Restoring archive of Grafana data..."
# GRAFANA_DATA_DIR=$(tar -tzf restore/grafana_data.tar.gz | head -1)
# tar -xzf restore/grafana_data.tar.gz -C restore/
GRAFANA_VOLUME_DIR=$(docker volume inspect ctfriend_grafana_data | jq -r '.[0].Mountpoint')

# grep -v -f restore/grafana-schema.sql restore/grafana-dump.sql > restore/grafana-data.sql
grep '^INSERT INTO' restore/grafana-dump.sql > restore/grafana-data.sql
sudo rm ${GRAFANA_VOLUME_DIR}/grafana.db
sudo sqlite3 ${GRAFANA_VOLUME_DIR}/grafana.db < restore/grafana-schema.sql 
sudo sqlite3 ${GRAFANA_VOLUME_DIR}/grafana.db < restore/grafana-data.sql 
sudo chown -R 472:root ${GRAFANA_VOLUME_DIR}/grafana.db

# restore timescale db
echo "Restoring archive of TimescaleDB..."

docker compose up -d --build db

# Use pg_isready to check the status in a loop
until pg_isready -h "localhost" -p "5432" -U "prometheus" -q; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 2
done
gunzip -c restore/metrics_db.gz | docker exec -i postgres_db psql -U postgres -d metrics

docker compose up -d --build

cd -

echo "-- Restore done --"