import requests
import os
from urllib.parse import quote_plus

def get_real_ip(hostname):
    print(f"Resolving real IP for {hostname} via Cloudflare DoH...")
    try:
        # Use Cloudflare's DNS-over-HTTPS
        url = f"https://cloudflare-dns.com/query?name={hostname}&type=A"
        headers = {"accept": "application/dns-json"}
        response = requests.get(url, headers=headers)
        data = response.json()
        if "Answer" in data:
            real_ip = data["Answer"][0]["data"]
            print(f"Real IP found: {real_ip}")
            return real_ip
        else:
            print("Could not resolve via DoH.")
            return None
    except Exception as e:
        print(f"DoH Resolution failed: {e}")
        return None

def update_env_with_ip():
    hostname = "db.lddtpexxziuvqkhejukr.supabase.co"
    real_ip = get_real_ip(hostname)
    
    if real_ip:
        # Construct the URL with IP and SNI/SSL requirements
        # Note: PostgreSQL with SSL usually needs the hostname for certificate verification.
        # However, we can try to use the IP and see if it connects.
        user = "postgres"
        password = "Ucn?ch3PCVcF*Wg"
        port = "5432"
        dbname = "postgres"
        
        encoded_pw = quote_plus(password)
        # We keep the host as the real IP to bypass the local DNS hijacking
        new_url = f"postgresql://{user}:{encoded_pw}@{real_ip}:{port}/{dbname}?sslmode=require"
        
        env_path = os.path.join(os.getcwd(), ".env")
        with open(env_path, "w") as f:
            f.write(f"DATABASE_URL={new_url}\n")
        
        print("\nUpdated .env with REAL IP.")
        print("NOTE: Connecting via IP might cause SSL certificate hostname mismatch warnings,")
        print("but it should bypass the Clash Fake-IP timeout.")
        return True
    return False

if __name__ == "__main__":
    if update_env_with_ip():
        print("\nNow try running the test again.")
    else:
        print("\nCould not resolve the real IP. Please ensure your internet is working or check Clash settings.")
