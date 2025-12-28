#!/bin/sh
set -euo pipefail

echo "==> Waiting for MinIO to be ready..."
for i in $(seq 1 30); do
  if curl -fsS "http://minio:9000/minio/health/ready" >/dev/null 2>&1; then
    break
  fi
  echo "MinIO not ready yet ($i/30), sleeping 2s..."
  sleep 2
done

echo "==> Configure mc alias"
mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc alias list

echo "==> Create buckets if not exist"
mc mb --ignore-existing "local/$MINIO_BUCKET_AVATARS"

echo "==> Set anonymous read for avatars/products"
mc anonymous set download "local/$MINIO_BUCKET_AVATARS"
mc anonymous get "local/$MINIO_BUCKET_AVATARS"

echo "==> MinIO init done."