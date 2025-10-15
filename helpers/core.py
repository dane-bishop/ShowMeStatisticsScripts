import psycopg2
from psycopg2.extras import RealDictCursor

BASE = "https://mutigers.com"





def get_db_connection():
    return psycopg2.connect(host="localhost", database="capstone_db", user="danebishop",password="Bayloreagles20")