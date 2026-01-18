import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")

print(f"Testing connection to: {url.split('@')[-1]}") # Hide password in logs
try:
    conn = psycopg2.connect(url, connect_timeout=10)
    print("SUCCESS! Connected to Supabase.")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"DB Version: {cur.fetchone()}")
    
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
