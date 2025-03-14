#!/bin/bash
set -e

# Run the default entrypoint script
docker-entrypoint.sh postgres &

# Wait for PostgreSQL to start
until pg_isready -h localhost -p 5432 -U "$POSTGRES_USER"; do
    echo "Waiting for PostgreSQL to start..."
    sleep 2
done

# Run your SQL script
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init.sql

# Wait for PostgreSQL foreground process
wait
