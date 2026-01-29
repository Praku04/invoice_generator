#!/usr/bin/env python3
import time
import psycopg2
import sys
import os

def wait_for_db():
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:invoicedb123@db:5432/invoicedb')
    
    print("Waiting for database...")
    while True:
        try:
            psycopg2.connect(database_url)
            print("Database is ready!")
            break
        except psycopg2.OperationalError:
            print("Database not ready, waiting...")
            time.sleep(1)
        except Exception as e:
            print(f"Error connecting to database: {e}")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_db()