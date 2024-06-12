#!/bin/bash
until psql -h target_db -U target_user -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - executing command"
psql -h target_db -U target_user -c "CREATE DATABASE IF NOT EXISTS target_db;"