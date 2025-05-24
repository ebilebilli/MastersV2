import time
import psycopg2
from psycopg2 import OperationalError
import os

while True:
    try:
        conn = psycopg2.connect(
            NAME = os.getenv('POSTGRES_DB'),
            USER = os.getenv('POSTGRES_USER'),
            PASSWORD = os.getenv('POSTGRES_PASSWORD'),
            HOST = os.getenv('POSTGRES_HOST'),
            PORT = os.getenv('POSTGRES_PORT'),
        )
        conn.close()
        break
    except OperationalError:
        time.sleep(2)
