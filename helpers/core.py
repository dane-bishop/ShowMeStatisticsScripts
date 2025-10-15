import psycopg2
from psycopg2.extras import RealDictCursor
import re

BASE = "https://mutigers.com"
HDRS = {"User-Agent": "Mozilla/5.0 (+data-ingest)"}

COACH_WORDS = re.compile(r"coach|director|ops|operations|trainer|analyst|staff", re.I)





def get_db_connection():
    return psycopg2.connect(host="localhost", database="capstone_db", user="danebishop",password="Bayloreagles20")