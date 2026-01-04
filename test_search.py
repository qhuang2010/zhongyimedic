import requests
import time

BASE_URL = "http://localhost:8000"

def test_workflow():
    # 1. Save a patient record
    payload = {
        "patient_info": {
            "name": "张三",
            "gender": "男",
            "age": 30,
            "phone": "13800138000"
        },
        "medical_record": {
            "complaint": "Test complaint"
        },
        "pulse_grid": {}
    }
    
    print("Saving record...")
    resp = requests.post(f"{BASE_URL}/api/records/save", json=payload)
    print("Save response:", resp.json())
    assert resp.status_code == 200

    # 2. Search by Chinese name
    print("Searching '张'...")
    resp = requests.get(f"{BASE_URL}/api/patients/search", params={"query": "张"})
    data = resp.json()
    print("Search '张' result:", len(data))
    assert len(data) >= 1
    assert data[0]["name"] == "张三"

    # 3. Search by Pinyin initials ('zs')
    print("Searching 'zs'...")
    resp = requests.get(f"{BASE_URL}/api/patients/search", params={"query": "zs"})
    data = resp.json()
    print("Search 'zs' result:", len(data))
    assert len(data) >= 1
    assert data[0]["name"] == "张三"
    
    # 4. Search by phone
    print("Searching '138'...")
    resp = requests.get(f"{BASE_URL}/api/patients/search", params={"query": "138"})
    data = resp.json()
    print("Search '138' result:", len(data))
    assert len(data) >= 1

    print("All tests passed!")

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print("Test failed:", e)
