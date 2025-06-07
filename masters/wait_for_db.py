import time
import psycopg2
from psycopg2 import OperationalError
import os

"""
This script waits for the PostgreSQL database service to become available.

It attempts to connect to the database in a loop, retrying every 2 seconds
until the connection is successful. This is commonly used in Docker environments
where the database container might take some time to start accepting connections,
preventing errors like psycopg2.OperationalError on initial connection attempts.

Database connection parameters are provided via environment variables:
    - POSTGRES_DB
    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_HOST
    - POSTGRES_PORT
"""

while True:
    try:
        conn = psycopg2.connect(
            dbname = os.getenv('POSTGRES_DB'),
            user = os.getenv('POSTGRES_USER'),
            password = os.getenv('POSTGRES_PASSWORD'),
            host = os.getenv('POSTGRES_HOST'),
            port = os.getenv('POSTGRES_PORT'),
        )
        conn.close()
        break
    except OperationalError:
        time.sleep(2)
