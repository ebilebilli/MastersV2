import time
import psycopg2
from psycopg2 import OperationalError

while True:
    try:
        conn = psycopg2.connect(
            dbname="masters",
            user="postgres",
            password="boceyim123",
            host="db",
            port="5432"
        )
        conn.close()
        break
    except OperationalError:
        time.sleep(2)
