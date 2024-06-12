#!/bin/bash
until psql -h localhost -U target_user -d target_db -W target_password -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - executing command"

psql -h localhost -U target_user -d target_db -W target_password <<-EOSQL
    CREATE TABLE IF NOT EXISTS jobs_table_joined (
        id SERIAL PRIMARY KEY,
        job_title VARCHAR(255),
        company_name VARCHAR(255),
        location VARCHAR(255),
        URL VARCHAR(255) UNIQUE,
        summarized_data TEXT
    );
EOSQL