import sys
import os
import random
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import SessionLocal
from src.database.models import Patient, MedicalRecord

def add_wangfang_record():
    db = SessionLocal()
    try:
        # Find Wang Fang
        # Assuming the phone number from previous seed data: 13900139002
        patient = db.query(Patient).filter(Patient.name == "王芳").first()
        
        if not patient:
            print("Patient Wang Fang not found. Please run seed_data.py first.")
            return

        print(f"Found patient: {patient.name} (ID: {patient.id})")

        # Create a new record (e.g., a follow-up visit 2 weeks later)
        pulse_options = ["浮", "沉", "迟", "数", "滑", "涩", "弦", "紧", "缓", "弱"]
        
        pulse_grid = {
            "cun-fu": "滑",
            "guan-fu": "缓",
            "chi-fu": "弱",
            "cun-zhong": "滑",
            "guan-zhong": "缓",
            "chi-zhong": "弱",
            "cun-chen": "沉",
            "guan-chen": "沉",
            "chi-chen": "沉",
        }
        
        complaint = "复诊：手脚冰凉有所缓解，但仍感疲乏"
        
        record_data = {
            "medical_record": {
                "complaint": complaint,
                "prescription": "当归四逆汤加减",
                "note": "注意保暖，少食生冷"
            },
            "pulse_grid": pulse_grid,
            "raw_input": {}
        }
        
        # Set date to be more recent than the seed data (which was random 0-30 days ago)
        # Let's say this is "today"
        new_record = MedicalRecord(
            patient_id=patient.id,
            visit_date=datetime.now(),
            complaint=complaint,
            diagnosis="阳虚体质",
            data=record_data
        )
        
        db.add(new_record)
        db.commit()
        print("Successfully added new record for Wang Fang.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_wangfang_record()
