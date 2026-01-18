import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_db_storage():
    print("Testing cloud database storage...")
    
    # 1. Create a test patient and record
    test_data = {
        "patient_info": {
            "name": "云测试1号",
            "gender": "男",
            "age": 30,
            "phone": "13800001234"
        },
        "medical_record": {
            "complaint": "端到端云连接测试",
            "prescription": "测试方剂"
        },
        "pulse_grid": {
            "left-cun-fu": "浮",
            "left-guan-fu": "弦",
            "right-cun-fu": "细"
        },
        "mode": "personal"
    }
    
    try:
        # Give the server a moment to start just in case
        time.sleep(2)
        
        print(f"Sending request to {BASE_URL}/api/records/save...")
        response = requests.post(f"{BASE_URL}/api/records/save", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Record saved! ID: {result.get('record_id')}")
            
            # 2. Verify we can search for it
            print("Verifying searchability...")
            search_resp = requests.get(f"{BASE_URL}/api/patients/search?query=云测试")
            if search_resp.status_code == 200:
                patients = search_resp.json()
                if any(p['name'] == "云测试1号" for p in patients):
                    print("SUCCESS: Patient found in cloud database!")
                else:
                    print("FAILURE: Patient not found in search results.")
            else:
                print(f"FAILURE: Search api failed with status {search_resp.status_code}")
                
        else:
            print(f"FAILURE: Server returned error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"ERROR: Could not connect to server: {e}")

if __name__ == "__main__":
    test_db_storage()
