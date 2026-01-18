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
ports = ["5432", "6543"]

for pw in passwords:
    for port in ports:
        print(f"Testing password: {pw} on port: {port}")
        try:
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=pw,
                host=host,
                port=port,
                sslmode='require',
                connect_timeout=10
            )
            print(f"  SUCCESS! Password '{pw}' works on port {port}.")
            conn.close()
            
            encoded_pw = quote_plus(pw)
            url = f"postgresql://{user}:{encoded_pw}@{host}:{port}/{dbname}?sslmode=require"
            print(f"  Final connection string: {url}")
            exit(0)
            
        except Exception as e:
            print(f"  FAILED: {e}")
