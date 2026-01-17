import sys
import os
from typing import Dict, Any

from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import uuid4
import uvicorn
from pypinyin import lazy_pinyin, Style

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_preparation.validator import DataValidator
from src.database.connection import engine, Base, get_db
from src.database.models import Patient, MedicalRecord, Practitioner
from uuid import uuid4

# Create tables if they don't exist
# Note: In production, use Alembic for migrations
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to database to create tables. Please ensure PostgreSQL is running. Error: {e}")

app = FastAPI(title="中医脉象九宫格OCR识别系统")

# Mount static files from React build
# Note: Ensure 'npm run build' has been executed in web/frontend
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

# Initialize validator
validator = DataValidator()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Serve the React app
    index_path = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>Frontend build not found. Please run 'npm run build' in web/frontend</h1>", status_code=404)

@app.post("/api/validate")
async def validate_data(data: Dict[str, Any]):
    is_valid, errors = validator.validate_data(data, context="web_input")
    return {"valid": is_valid, "errors": errors}

@app.get("/api/patients/search")
async def search_patients(
    query: str = Query(None, min_length=1),
    db: Session = Depends(get_db)
):
    """
    Search patients by name or phone number
    """
    if not query:
        return []
    
    patients = db.query(Patient).filter(
        or_(
            Patient.name.ilike(f"%{query}%"),
            Patient.phone.ilike(f"%{query}%"),
            Patient.pinyin.ilike(f"%{query}%")
        )
    ).limit(20).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "gender": p.gender,
            "age": p.age,
            "phone": p.phone,
            "last_visit": p.updated_at.strftime("%Y-%m-%d") if p.updated_at else None
        }
        for p in patients
    ]

@app.get("/api/patients/by_date")
async def get_patients_by_date(
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format"),
    date: str = Query(None, description="Single date in YYYY-MM-DD format (deprecated, use start_date/end_date)"),
    db: Session = Depends(get_db)
):
    """
    Get patients who had a medical record within a date range.
    If only one date is provided, it will be used as both start and end.
    If no dates are provided, defaults to today.
    """
    try:
        from sqlalchemy import func
        
        # Handle backwards compatibility and defaults
        if start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        elif date:
            # Legacy single date parameter
            start = datetime.strptime(date, "%Y-%m-%d").date()
            end = start
        elif start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = start
        elif end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            start = end
        else:
            # Default to today
            start = datetime.now().date()
            end = start
        
        # Ensure start <= end
        if start > end:
            start, end = end, start
        
        # Query MedicalRecords within date range, join with Patient
        records = db.query(MedicalRecord).join(Patient).filter(
            func.date(MedicalRecord.visit_date) >= start,
            func.date(MedicalRecord.visit_date) <= end
        ).order_by(MedicalRecord.visit_date.desc()).all()
        
        # Deduplicate patients
        seen_patients = set()
        result_patients = []
        
        for r in records:
            p = r.patient
            if p.id not in seen_patients:
                seen_patients.add(p.id)
                result_patients.append({
                    "id": p.id,
                    "name": p.name,
                    "gender": p.gender,
                    "age": p.age,
                    "phone": p.phone,
                    "last_visit": r.visit_date.strftime("%Y-%m-%d")
                })
                
        return result_patients
        
    except ValueError:
         raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@app.get("/api/patients/{patient_id}/latest_record")
async def get_patient_latest_record(patient_id: int, db: Session = Depends(get_db)):
    """
    Get patient details and their latest medical record
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    latest_record = db.query(MedicalRecord)\
        .filter(MedicalRecord.patient_id == patient_id)\
        .order_by(MedicalRecord.created_at.desc())\
        .first()
        
    response_data = {
        "record_id": latest_record.id if latest_record else None,
        "patient_info": {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone
        },
        "medical_record": {},
        "pulse_grid": {}
    }
    
    if latest_record and latest_record.data:
        record_data = latest_record.data
        if "medical_record" in record_data:
            response_data["medical_record"] = record_data["medical_record"]
        if "pulse_grid" in record_data:
            response_data["pulse_grid"] = record_data["pulse_grid"]
            
    return response_data

@app.get("/api/practitioners")
async def get_practitioners(db: Session = Depends(get_db)):
    """
    Get all practitioners (teachers and doctors)
    """
    practitioners = db.query(Practitioner).all()
    return [{
        "id": p.id,
        "name": p.name,
        "role": p.role
    } for p in practitioners]

@app.get("/api/patients/{patient_id}/history")
async def get_patient_history(patient_id: int, db: Session = Depends(get_db)):
    """
    Get a list of medical records for a patient
    """
    records = db.query(MedicalRecord)\
        .filter(MedicalRecord.patient_id == patient_id)\
        .order_by(MedicalRecord.visit_date.desc())\
        .all()
        
    return [
        {
            "id": r.id,
            "visit_date": r.visit_date.strftime("%Y-%m-%d"),
            "complaint": r.complaint
        }
        for r in records
    ]

@app.get("/api/records/{record_id}")
async def get_record(record_id: int, db: Session = Depends(get_db)):
    """
    Get a specific medical record
    """
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    response_data = {
        "medical_record": {},
        "pulse_grid": {}
    }
    
    if record.data:
        record_data = record.data
        if "medical_record" in record_data:
            response_data["medical_record"] = record_data["medical_record"]
        if "pulse_grid" in record_data:
            response_data["pulse_grid"] = record_data["pulse_grid"]
            
    return response_data

@app.delete("/api/records/{record_id}")
async def delete_record(record_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific medical record
    """
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    db.delete(record)
    db.commit()
    
    return {"status": "success", "message": f"Record {record_id} deleted"}

from datetime import datetime, date

# ... (imports)

@app.post("/api/records/save")
async def save_record(data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Save medical record using Relational Skeleton + JSONB Flesh pattern.
    If a record exists for the same patient on the same day, update it instead of creating new.
    """
    try:
        # Extract Relational Skeleton data
        patient_info = data.get("patient_info", {})
        medical_info = data.get("medical_record", {})
        
        # 1. Handle Patient (Find or Create)
        # For simplicity, we assume name + gender + age is unique enough for this demo
        # In production, use a proper ID or search
        patient_name = patient_info.get("name")
        if not patient_name:
            raise HTTPException(status_code=400, detail="Patient name is required")
            
        # Try to find by name and phone if provided, otherwise fallback to other fields
        patient_query = db.query(Patient).filter(Patient.name == patient_name)
        
        if patient_info.get("phone"):
            patient_query = patient_query.filter(Patient.phone == patient_info.get("phone"))
        else:
            # Fallback to gender and age if no phone
            patient_query = patient_query.filter(
                Patient.gender == patient_info.get("gender"),
                Patient.age == int(patient_info.get("age", 0)) if patient_info.get("age") else None
            )
            
        patient = patient_query.first()
        
        if not patient:
            # Generate pinyin initials
            pinyin_initials = "".join(lazy_pinyin(patient_name, style=Style.FIRST_LETTER))
            
            patient = Patient(
                name=patient_name,
                gender=patient_info.get("gender"),
                age=int(patient_info.get("age", 0)) if patient_info.get("age") else None,
                phone=patient_info.get("phone"),
                pinyin=pinyin_initials,
                info=patient_info  # Store full patient info in JSONB flesh too
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
        else:
            # Update existing patient info if needed (e.g. add phone if missing)
            if patient_info.get("phone") and not patient.phone:
                patient.phone = patient_info.get("phone")
                db.commit()
            
            # Update pinyin if missing (for legacy data)
            if not patient.pinyin:
                 patient.pinyin = "".join(lazy_pinyin(patient.name, style=Style.FIRST_LETTER))
                 db.commit()
            
        # 2. Create or Update Medical Record
        # Check if record exists for today
        from sqlalchemy import func
        today = date.today()
        
        existing_record = db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient.id,
            func.date(MedicalRecord.visit_date) == today
        ).first()
        
        # Relational Skeleton
        complaint = medical_info.get("complaint")
        
        # Practitioner Binding Logic
        mode = data.get("mode", "personal")
        teacher_name = data.get("teacher", "")
        practitioner_id = None
        
        if mode == "personal":
            # Find default doctor
            doc = db.query(Practitioner).filter(Practitioner.role == "doctor").first()
            if doc:
                practitioner_id = doc.id
        elif mode == "shadowing":
             # Find teacher
             if teacher_name:
                 teacher = db.query(Practitioner).filter(Practitioner.name == teacher_name, Practitioner.role == "teacher").first()
                 if teacher:
                     practitioner_id = teacher.id
        
        # JSONB Flesh (Store everything)
        record_data = {
            "medical_record": medical_info,
            "pulse_grid": data.get("pulse_grid", {}),
            "raw_input": data,
            "client_info": { 
                "mode": mode,
                "teacher": teacher_name,
                "practitioner_id": practitioner_id # redundant but useful for debug
            }
        }
        
        if existing_record:
            # Update existing record
            existing_record.complaint = complaint
            existing_record.data = record_data
            existing_record.practitioner_id = practitioner_id # Update practitioner
            existing_record.updated_at = datetime.now()
            record_id = existing_record.id
            message = "Record updated successfully"
        else:
            # Create new record
            new_record = MedicalRecord(
                patient_id=patient.id,
                complaint=complaint,
                data=record_data,
                practitioner_id=practitioner_id # Set practitioner
            )
            db.add(new_record)
            record_id = None # Will be set after commit
            message = "Record saved successfully"
        
        db.commit()
        if not record_id and 'new_record' in locals():
            db.refresh(new_record)
            record_id = new_record.id
        
        return {"status": "success", "message": message, "record_id": record_id}
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_record(data: Dict[str, Any]):
    """
    Advanced Rule-Based Analysis Simulation based on Shanghan Lun and Zheng Qin'an (Fire Spirit School) logic.
    """
    medical_record = data.get("medical_record", {})
    pulse_grid = data.get("pulse_grid", {})
    
    complaint = medical_record.get("complaint", "")
    prescription = medical_record.get("prescription", "")
    
    # 1. Parse Pulse Data
    # Extract key qualities from the grid (Now supporting left/right)
    # Helper to aggregate from both hands
    def get_qualities(pos, level):
        # Check specific left/right keys first, fallback to generic if not found (legacy support)
        vals = []
        for side in ["left", "right"]:
            key = f"{side}-{pos}-{level}"
            val = pulse_grid.get(key, "").strip()
            if val: vals.append(val)
        
        # Also check legacy generic keys
        legacy_key = f"{pos}-{level}"
        legacy_val = pulse_grid.get(legacy_key, "").strip()
        if legacy_val: vals.append(legacy_val)
        
        return vals

    fu_qualities = []
    for p in ["cun", "guan", "chi"]:
        fu_qualities.extend(get_qualities(p, "fu"))
        
    zhong_qualities = []
    for p in ["cun", "guan", "chi"]:
        zhong_qualities.extend(get_qualities(p, "zhong"))
        
    chen_qualities = []
    for p in ["cun", "guan", "chi"]:
        chen_qualities.extend(get_qualities(p, "chen"))
        
    overall_pulse = pulse_grid.get("overall_description", "")
    
    # Helper to check keywords in a list of strings
    def check_keywords(qualities, keywords):
        for q in qualities:
            for k in keywords:
                if k in q:
                    return True
        return False
    
    # Helper for overall description
    def check_overall(keywords):
        for k in keywords:
            if k in overall_pulse:
                return True
        return False

    is_floating_tight = check_keywords(fu_qualities, ["紧", "弦"]) or check_overall(["紧", "弦"])
    is_floating_weak = check_keywords(fu_qualities, ["细", "弱", "微", "无"]) or check_overall(["细", "弱", "虚"])
    is_deep_empty = check_keywords(chen_qualities, ["无", "空", "微", "弱"]) or check_overall(["无根", "空", "豁"])
    is_middle_empty = check_keywords(zhong_qualities, ["空", "无", "弱"])
    
    # 2. Logic Engine (Zheng Qin'an / Shanghan Perspective)
    
    # Diagnosis Pattern Detection
    pattern = "Unknown"
    consistency_comment = ""
    suggestion = ""
    
    # Pattern: Rootless Yang / True Cold False Heat (Zheng Qin'an Focus)
    # Signs: Floating pulse is present (maybe even big/tight), but Deep/Root is Empty/None.
    if is_deep_empty and (check_keywords(fu_qualities, ["大", "浮", "紧", "弦", "细"])):
        pattern = "Rootless Yang"
        consistency_comment = (
            "【郑钦安视角】脉象呈现“寸关尺浮取可见，但沉取无力或空虚”，此乃“阳气外浮，下元虚寒”之象。\\n"
            "虽浮部见紧或细，切不可误认为单纯表实证。沉取无根，说明肾阳虚衰，真阳不能潜藏，反逼虚阳上浮外越。\\n"
            "若主诉有“头晕、面红”等看似热象，实为“真寒假热”。"
        )
        suggestion = (
            "建议：急当扶阳抑阴，引火归元。\\n"
            "切忌使用发散风寒之辛温解表药（如麻黄）或苦寒直折之药，恐耗散仅存之真阳。\\n"
            "推荐方剂：四逆汤、白通汤或潜阳丹加减。"
        )
        
    # Pattern: Taiyang Cold Damage (Shanghan Lun)
    # Signs: Floating and Tight, Deep is relatively normal or tight.
    elif is_floating_tight and not is_deep_empty:
        pattern = "Taiyang Cold"
        consistency_comment = (
            "【伤寒论视角】脉浮而紧，乃太阳伤寒表实证之典型脉象。\\n"
            "“寸口脉浮而紧，浮则为风，紧则为寒”，寒邪束表，卫阳闭郁。\\n"
            "若主诉伴有“恶寒、发热、身痛、无汗”，则脉证高度一致。"
        )
        suggestion = (
            "建议：辛温解表，发汗宣肺。\\n"
            "推荐方剂：麻黄汤加减。\\n"
            "注意：若患者素体汗多或尺脉迟弱，需防过汗伤阳，可考虑桂枝汤或桂枝加葛根汤。"
        )

    # Pattern: Spleen/Stomach Deficiency (Middle Burner)
    elif is_middle_empty:
        pattern = "Middle Deficiency"
        consistency_comment = (
            "【脉象分析】关部（中候）见空/弱，提示中焦脾胃之气虚损。\\n"
            "脾胃为后天之本，中气不足则生化无源。"
        )
        suggestion = (
            "建议：健脾益气，调和中焦。\\n"
            "推荐方剂：理中汤或补中益气汤加减。"
        )
        
    else:
        # Default / Fallback
        consistency_comment = (
            "脉象显示：浮部" + "/".join([q for q in fu_qualities if q]) + 
            "，沉部" + "/".join([q for q in chen_qualities if q]) + "。\\n"
            "需结合“望闻问切”四诊合参。若浮沉皆无力，多属气血两虚；若脉象有力，多属实证。"
        )
        suggestion = "建议结合舌苔及其他临床症状进一步辨证。"

    # 3. Prescription Analysis
    prescription_comment = ""
    if not prescription or len(prescription) < 2:
        prescription_comment = "未提供完整处方，无法进行具体药物对证分析。"
    else:
        # Simple keyword check for warming herbs
        warming_herbs = ["附子", "干姜", "肉桂", "桂枝", "细辛", "吴茱萸"]
        clearing_herbs = ["石膏", "知母", "黄连", "黄芩", "大黄"]
        
        has_warming = check_keywords([prescription], warming_herbs)
        has_clearing = check_keywords([prescription], clearing_herbs)
        
        if pattern == "Rootless Yang":
            if has_warming:
                prescription_comment = "处方中包含扶阳药物，符合“扶阳抑阴”的治疗原则，方向正确。"
            elif has_clearing:
                prescription_comment = "【警示】处方中包含寒凉药物，与“下元虚寒、阳气外越”的病机相悖，恐致“雪上加霜”，请慎重复核！"
            else:
                prescription_comment = "处方似乎未重用温潜之品，对于真阳虚衰之证，力度可能不足。"
        elif pattern == "Taiyang Cold":
            if "麻黄" in prescription or "桂枝" in prescription:
                prescription_comment = "处方包含解表散寒之药，符合太阳病治疗原则。"
            else:
                prescription_comment = "处方未见典型解表药，若确诊为太阳伤寒，需考虑是否用药偏颇。"
        else:
            prescription_comment = "处方需结合具体病机分析。若为虚寒证，宜温补；若为实热证，宜清泄。"

    return {
        "consistency_comment": consistency_comment,
        "prescription_comment": prescription_comment,
        "suggestion": suggestion
    }

@app.post("/api/records/search_similar")
async def search_similar_records(data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Search for similar medical records based on pulse grid data
    Updated: Supports single-hand matching against both hands of candidates
    """
    current_grid = data.get("pulse_grid", {})
    if not current_grid:
        return []
        
    # Get all records to compare (in production, use vector search or more efficient filtering)
    candidates = db.query(MedicalRecord).order_by(MedicalRecord.created_at.desc()).limit(100).all()
    
    results = []
    
    # 1. Analyze Input Structure
    base_positions = [
        "cun-fu", "guan-fu", "chi-fu",
        "cun-zhong", "guan-zhong", "chi-zhong",
        "cun-chen", "guan-chen", "chi-chen"
    ]
    
    has_left = any(current_grid.get(f"left-{p}") for p in base_positions)
    has_right = any(current_grid.get(f"right-{p}") for p in base_positions)
    
    # Determine Matching Strategy
    # Strategy: 
    # - If both hands present: Match Left-Left AND Right-Right (Original logic)
    # - If only one hand (e.g. Left): Match InputLeft-CandLeft AND InputLeft-CandRight, take MAX score
    
    single_hand_mode = (has_left and not has_right) or (has_right and not has_left)
    input_hand_prefix = "left-" if (has_left and not has_right) else "right-" if (has_right and not has_left) else None
    
    for record in candidates:
        if not record.data or "pulse_grid" not in record.data:
            continue
            
        candidate_grid = record.data["pulse_grid"]
        
        # Helper to calculate score between two sets of keys
        def calculate_score(prefix_a, prefix_b):
            sc = 0
            m = []
            for pos in base_positions:
                key_a = f"{prefix_a}{pos}"
                key_b = f"{prefix_b}{pos}"
                
                # Also support legacy keys (no prefix) for candidate
                val_a = current_grid.get(key_a, "").strip()
                
                # Candidate might have prefix or legacy
                val_b = candidate_grid.get(key_b, "").strip()
                if not val_b and not prefix_b: # Try legacy if prefix_b is empty string (meaning generic match intended? No, logic below)
                     pass 

                # Actually, let's normalize candidate fetching
                # If we are comparing to Candidate Left, we check "left-{pos}"
                # If Candidate has no "left-", maybe it has legacy "{pos}"? 
                # Let's assume legacy data is Generic.
                
                real_val_b = val_b
                if not real_val_b:
                    # Fallback to legacy key if prefix_b corresponds to a side but data is legacy generic
                    legacy_key = pos
                    real_val_b = candidate_grid.get(legacy_key, "").strip()

                if val_a and real_val_b:
                    if val_a == real_val_b:
                        sc += 10
                        m.append(f"{key_a}=={key_b if val_b else legacy_key}")
                    elif val_a in real_val_b or real_val_b in val_a:
                        sc += 5
                        m.append(f"{key_a}~={key_b if val_b else legacy_key}")
            return sc, m

        final_score = 0
        final_matches = []

        if single_hand_mode and input_hand_prefix:
            # Single Hand Matching
            # Compare Input vs Candidate Left
            score_l, matches_l = calculate_score(input_hand_prefix, "left-")
            # Compare Input vs Candidate Right
            score_r, matches_r = calculate_score(input_hand_prefix, "right-")
            
            if score_l >= score_r:
                final_score = score_l
                final_matches = matches_l
            else:
                final_score = score_r
                final_matches = matches_r
        else:
            # Dual Hand Matching (Standard)
            score_l, matches_l = calculate_score("left-", "left-")
            score_r, matches_r = calculate_score("right-", "right-")
            
            # Also check Legacy/Generic keys if explicit sides missing in candidate?
            # Existing logic did exact key matching.
            # Let's keep it simple: Add scores up
            final_score = score_l + score_r
            final_matches = matches_l + matches_r
            
            # Legacy generic keys matching (if input has them? Input usually is standardized now)
            # If input has 'cun-fu' (legacy), match with 'cun-fu'
            score_g, matches_g = calculate_score("", "")
            final_score += score_g
            final_matches.extend(matches_g)

        # 2. Compare overall description
        overall1 = current_grid.get("overall_description", "").strip()
        overall2 = candidate_grid.get("overall_description", "").strip()
        if overall1 and overall2:
            set1 = set(overall1)
            set2 = set(overall2)
            overlap = len(set1.intersection(set2))
            if overlap > 0:
                final_score += overlap * 2
                
        if final_score > 0:
            patient = record.patient
            results.append({
                "record_id": record.id,
                "patient_name": patient.name if patient else "Unknown",
                "visit_date": record.visit_date.strftime("%Y-%m-%d"),
                "score": final_score,
                "pulse_grid": candidate_grid,
                "matches": final_matches,
                "complaint": record.complaint
            })
            
    # Sort by score desc
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:5]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
