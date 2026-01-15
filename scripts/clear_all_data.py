import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import SessionLocal
from src.database.models import Patient, MedicalRecord

def clear_data():
    db = SessionLocal()
    try:
        print("Starting data cleanup...")
        
        # Delete medical records first due to foreign key constraint
        num_records = db.query(MedicalRecord).delete()
        print(f"Deleted {num_records} medical records.")
        
        # Delete patients
        num_patients = db.query(Patient).delete()
        print(f"Deleted {num_patients} patients.")
        
        db.commit()
        print("All test data cleared successfully.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_data()
