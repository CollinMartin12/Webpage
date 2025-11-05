#!/bin/bash

echo "Waiting for MariaDB to be ready..."

# Wait for MariaDB to be available
while ! python -c "
import pymysql
import os
import sys
try:
    connection = pymysql.connect(
        host=os.getenv('DB_HOST', 'mariadb'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'microblog_user'),
        password=os.getenv('DB_PASSWORD', 'microblog_password'),
        database=os.getenv('DB_NAME', 'microblog_db')
    )
    connection.close()
    print('Database is ready!')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"; do
    echo "Waiting for database..."
    sleep 2
done

echo "Database is ready! Creating tables..."

# Create tables
python create_tables.py

echo "Starting Flask application..."
exec "$@"
