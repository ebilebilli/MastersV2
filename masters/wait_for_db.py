import time
import psycopg2
from psycopg2 import OperationalError
import os

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
