import sys
import os
import requests

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import SessionLocal
from src.database.models import Patient, MedicalRecord
from datetime import datetime

def test_matching_logic():
    db = SessionLocal()
    try:
        print("Starting matching logic verification...")
        
        # 1. Clear existing records for clean test
        db.query(MedicalRecord).delete()
        db.query(Patient).delete()
        db.commit()
        
        # 2. Create a dummy patient
        p = Patient(name="TestPatient", gender="男", age=30)
        db.add(p)
        db.commit()
        db.refresh(p)
        
        # 3. Create a record with Symmetric Pulse (Big everywhere)
        # But let's make it distinct: Left=Floating, Right=Deep
        # To test cross-matching
        
        # Case A: Left=Floating, Right=Deep
        grid_A = {
            "left-cun-fu": "Floating",
            "right-cun-chen": "Deep",
            "overall_description": "Mixed Pulse"
        }
        rec_A = MedicalRecord(
            patient_id=p.id,
            data={"pulse_grid": grid_A, "medical_record": {}, "raw_input": {}}
        )
        db.add(rec_A)
        db.commit()
        
        # 4. Test Single Hand Match
        # Input: Left="Deep"
        # Since RecA has Right="Deep", Input(Left) should match RecA(Right) if logic works.
        
        print("\nTest Case 1: Input Left='Deep' vs Record(Left='Floating', Right='Deep')")
        # Should match effectively because Input(L) ~= Record(R)
        
        # We need to test via API function directly or mock it? 
        # Ideally via API endpoint but server is running. 
        # Let's verify via direct function call logic simulation or request to localhost:8000
        
        try:
            url = "http://localhost:8000/api/records/search_similar"
            payload = {
                "pulse_grid": {
                    "left-cun-chen": "Deep"  # Input Left matches Record Right's feature
                }
            }
            
            # Using requests to hit the running server
            resp = requests.post(url, json=payload)
            if resp.status_code == 200:
                results = resp.json()
                if len(results) > 0:
                    print(f"✓ Match Found! Score: {results[0]['score']}")
                    print(f"  Matches: {results[0]['matches']}")
                    # Expect match on right-cun-che (from input left-cun-che)
                    # Input key: left-cun-che. Candidate key matched: right-cun-che?
                    # My logic: calculate_score(prefix_a="left-", prefix_b="right-")
                    # key_a = left-cun-che (Deep), key_b = right-cun-che (Deep) -> Match!
                    
                    found_cross_match = any("right" in m for m in results[0]['matches'])
                    if found_cross_match:
                         print("✓ Successfully matched Input(Left) against Candidate(Right)!")
                    else:
                         print("? Match found but maybe not cross-hand? Check matches list.")
                else:
                    print("✗ No matches found. Logic might be wrong.")
            else:
                print(f"✗ API Error: {resp.status_code} {resp.text}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")

    except Exception as e:
        print(f"Error during test: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_matching_logic()
