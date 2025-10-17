import os
import psycopg2
from psycopg2.extras import register_uuid
from dotenv import load_dotenv

load_dotenv()
register_uuid()

def get_conn():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL no configurada")
    return psycopg2.connect(url)
