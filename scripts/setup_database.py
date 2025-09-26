import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def create_database():
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        host="localhost",
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "password")
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
    cursor = conn.cursor()
    
    # Create database
    try:
        cursor.execute("CREATE DATABASE climate_policy")
        print("Database 'climate_policy' created successfully")
    except psycopg2.errors.DuplicateDatabase:
        print("Database already exists")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_database()