import psycopg
import os

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("DB_NAME", "poker"),
        user=os.getenv("DB_USER", "app"),
        password=os.getenv("DB_PASSWORD", "app_pw"),
        port=os.getenv("DB_PORT", "5432"),
    )
