import psycopg2
import os
from urllib.parse import quote_plus

# Test combinations
passwords = [
    "Ucn?ch3PCVcF*Wg",
    "[Ucn?ch3PCVcF*Wg]"
]

host = "db.lddtpexxziuvqkhejukr.supabase.co"
user = "postgres"
dbname = "postgres"
port = "5432"

for pw in passwords:
    print(f"Testing password: {pw}")
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=pw,
            host=host,
            port=port,
            sslmode='require'
        )
        print(f"  SUCCESS! Password '{pw}' works.")
        conn.close()
        
        # If success, construct the URL
        encoded_pw = quote_plus(pw)
        url = f"postgresql://{user}:{encoded_pw}@{host}:{port}/{dbname}"
        print(f"  Recommended URL: {url}")
        
    except Exception as e:
        print(f"  FAILED: {e}")

