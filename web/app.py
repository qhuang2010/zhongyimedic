import sys
import os
from typing import Dict, Any

from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uvicorn
from pypinyin import lazy_pinyin, Style

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_preparation.validator import DataValidator
from src.database.connection import engine, Base, get_db
from src.database.models import Patient, MedicalRecord

# Chain-of-Thought and Evaluation modules
try:
    from src.corpus.cot_generator import generate_chain_of_thought
    from src.corpus.knowledge_base import knowledge_base
    from src.evaluation.metrics import MetricsCalculator, EvaluationResult
    from src.evaluation.validation_framework import validation_framework
    
    # Yuanqi Pulse Method modules
    from src.corpus.yuanqi_cot_generator import generate_yuanqi_chain_of_thought
    from src.corpus.yuanqi_knowledge_base import yuanqi_knowledge_base
    COT_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: CoT modules not fully available: {e}")
    COT_MODULES_AVAILABLE = False

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
        
        # JSONB Flesh (Store everything)
        record_data = {
            "medical_record": medical_info,
            "pulse_grid": data.get("pulse_grid", {}),
            "raw_input": data
        }
        
        if existing_record:
            # Update existing record
            existing_record.complaint = complaint
            existing_record.data = record_data
            existing_record.updated_at = datetime.now()
            record_id = existing_record.id
            message = "Record updated successfully"
        else:
            # Create new record
            new_record = MedicalRecord(
                patient_id=patient.id,
                complaint=complaint,
                data=record_data
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
    AI智能评价 - 整合元气脉法思维链
    Advanced AI Analysis integrating Yuanqi Pulse Method Chain-of-Thought reasoning.
    """
    medical_record = data.get("medical_record", {})
    pulse_grid = data.get("pulse_grid", {})
    
    complaint = medical_record.get("complaint", "")
    prescription = medical_record.get("prescription", "")
    symptoms = medical_record.get("symptoms", [])
    
    # 如果症状是字符串，尝试解析
    if isinstance(symptoms, str):
        symptoms = [s.strip() for s in symptoms.split("，") if s.strip()]
    
    # ========================================
    # 1. 生成元气脉法思维链（核心创新）
    # ========================================
    cot_result = None
    yuanqi_analysis = ""
    medication_analysis = ""
    
    if COT_MODULES_AVAILABLE:
        try:
            # 转换脉象数据格式
            pulse_positions = {}
            
            # 解析左右手脉象
            for side in ["left", "right"]:
                for i, pos in enumerate(["cun", "guan", "chi"]):
                    pos_key = str(i + 1) if side == "left" else str(i + 4)
                    levels = {}
                    for level in ["fu", "zhong", "chen"]:
                        key = f"{side}-{pos}-{level}"
                        val = pulse_grid.get(key, "")
                        if val:
                            levels[level] = val
                    if levels:
                        pulse_positions[pos_key] = {"levels": levels}
            
            # 添加总体描述
            overall = pulse_grid.get("overall_description", "")
            if overall:
                pulse_positions["7"] = {"value": overall}
            
            # 生成元气脉法思维链
            cot = generate_yuanqi_chain_of_thought(
                pulse_grid_data={"positions": pulse_positions},
                symptoms=symptoms if symptoms else [complaint],
                chief_complaint=complaint,
                patient_info={}
            )
            cot_result = cot.to_dict()
            
            # 提取关键分析内容
            reasoning_steps = cot_result.get("reasoning_steps", [])
            
            yuanqi_analysis = "【元气脉法思维链分析】\n\n"
            for step in reasoning_steps:
                step_num = step.get("step_number", 0)
                step_type = step.get("reasoning_type", "")
                premise = step.get("premise", "")
                conclusion = step.get("conclusion", "")
                inference = step.get("inference", "")
                
                yuanqi_analysis += f"步骤{step_num}（{step_type}）：\n"
                yuanqi_analysis += f"  前提：{premise}\n"
                if inference:
                    yuanqi_analysis += f"  推理：{inference[:150]}{'...' if len(inference) > 150 else ''}\n"
                yuanqi_analysis += f"  结论：{conclusion}\n\n"
            
            # 处方分析
            prescription_data = cot_result.get("prescription", {})
            if prescription_data:
                medication_analysis = "【元气脉法用药分析】\n\n"
                medication_analysis += f"推荐方剂：{prescription_data.get('formula_name', '待定')}\n"
                medication_analysis += f"方剂解析：{prescription_data.get('formula_analysis', '')}\n\n"
                
                compat = prescription_data.get("compatibility_analysis", "")
                if compat:
                    medication_analysis += f"{compat}\n"
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            yuanqi_analysis = f"思维链生成异常：{str(e)}"
    
    # ========================================
    # 2. 传统规则分析（保留作为补充）
    # ========================================
    
    def get_qualities(pos, level):
        vals = []
        for side in ["left", "right"]:
            key = f"{side}-{pos}-{level}"
            val = pulse_grid.get(key, "").strip()
            if val: vals.append(val)
        legacy_key = f"{pos}-{level}"
        legacy_val = pulse_grid.get(legacy_key, "").strip()
        if legacy_val: vals.append(legacy_val)
        return vals

    chen_qualities = []
    for p in ["cun", "guan", "chi"]:
        chen_qualities.extend(get_qualities(p, "chen"))
    
    def check_keywords(qualities, keywords):
        for q in qualities:
            for k in keywords:
                if k in q:
                    return True
        return False
    
    is_deep_empty = check_keywords(chen_qualities, ["无", "空", "微", "弱", "虚"])
    
    # 元气状态判断
    yuanqi_state = "待评估"
    if is_deep_empty:
        yuanqi_state = "元气虚损（沉取无根）"
    else:
        yuanqi_state = "元气尚可（沉取有力）"
    
    # ========================================
    # 3. 处方一致性分析
    # ========================================
    prescription_comment = ""
    if not prescription or len(prescription) < 2:
        prescription_comment = "未提供完整处方，无法进行具体药物对证分析。"
    else:
        warming_herbs = ["附子", "干姜", "肉桂", "桂枝", "细辛", "吴茱萸", "附片", "仙灵脾"]
        nourishing_herbs = ["麦冬", "党参", "山药", "熟地", "枸杞"]
        
        has_warming = any(h in prescription for h in warming_herbs)
        has_nourishing = any(h in prescription for h in nourishing_herbs)
        
        if is_deep_empty:
            if has_warming:
                prescription_comment = "✅ 处方包含温阳药物，符合元气脉法'沉取无根需温补元阳'原则，方向正确。"
            elif has_nourishing:
                prescription_comment = "⚠️ 处方以养阴为主，需评估脉空程度。若脉空>5分宜养阴；若为虚阳外越则需温阳。"
            else:
                prescription_comment = "⚠️ 处方未见明显温阳或养阴之品，对于元气虚损证，力度可能不足。"
        else:
            prescription_comment = "脉象沉取有力，元气尚可。处方需结合具体病证综合分析。"

    # ========================================
    # 4. 构建返回结果
    # ========================================
    
    result = {
        "yuanqi_state": yuanqi_state,
        "consistency_comment": yuanqi_analysis if yuanqi_analysis else "元气脉法模块未加载",
        "prescription_comment": prescription_comment,
        "medication_analysis": medication_analysis,
        "suggestion": cot_result.get("expected_outcome", "请结合临床综合判断") if cot_result else "请结合四诊合参",
    }
    
    # 如果有完整思维链，添加详细数据
    if cot_result:
        result["chain_of_thought"] = cot_result
        
        # 提取关键诊断信息
        syndrome = cot_result.get("syndrome_differentiation", {})
        if syndrome:
            result["syndrome"] = syndrome.get("evidence_summary", "")
            
        treatment = cot_result.get("treatment_principle", {})
        if treatment:
            result["treatment_principle"] = treatment.get("primary_principle", "")
    
    return result

@app.post("/api/records/search_similar")
async def search_similar_records(data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Search for similar medical records based on pulse grid data
    """
    current_grid = data.get("pulse_grid", {})
    if not current_grid:
        return []
        
    # Get all records to compare (in production, use vector search or more efficient filtering)
    # For now, we fetch latest 100 records to compare
    candidates = db.query(MedicalRecord).order_by(MedicalRecord.created_at.desc()).limit(100).all()
    
    results = []
    # Expanded grid keys for 18 positions (plus legacy support)
    base_positions = [
        "cun-fu", "guan-fu", "chi-fu",
        "cun-zhong", "guan-zhong", "chi-zhong",
        "cun-chen", "guan-chen", "chi-chen"
    ]
    
    grid_keys = []
    # Add left/right versions
    for pos in base_positions:
        grid_keys.append(f"left-{pos}")
        grid_keys.append(f"right-{pos}")
        # Add legacy version just in case
        grid_keys.append(pos)
    
    for record in candidates:
        if not record.data or "pulse_grid" not in record.data:
            continue
            
        candidate_grid = record.data["pulse_grid"]
        score = 0
        matches = []
        
        # 1. Compare 9-grid keys
        for key in grid_keys:
            val1 = current_grid.get(key, "").strip()
            val2 = candidate_grid.get(key, "").strip()
            
            if val1 and val2:
                if val1 == val2:
                    score += 10 # Exact match
                    matches.append(key)
                elif val1 in val2 or val2 in val1:
                    score += 5 # Partial match
                    matches.append(key)
        
        # 2. Compare overall description
        overall1 = current_grid.get("overall_description", "").strip()
        overall2 = candidate_grid.get("overall_description", "").strip()
        if overall1 and overall2:
            # Simple keyword overlap (Jaccard-ish)
            set1 = set(overall1)
            set2 = set(overall2)
            overlap = len(set1.intersection(set2))
            if overlap > 0:
                score += overlap * 2
                
        if score > 0:
            patient = record.patient
            results.append({
                "record_id": record.id,
                "patient_name": patient.name if patient else "Unknown",
                "visit_date": record.visit_date.strftime("%Y-%m-%d"),
                "score": score,
                "pulse_grid": candidate_grid,
                "matches": matches,
                "complaint": record.complaint
            })
            
    # Sort by score desc
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:5] # Return top 5


# ============================================================
# Chain-of-Thought API Endpoints (Medical Informatics Journal)
# ============================================================

@app.post("/api/generate-cot")
async def generate_cot_endpoint(data: Dict[str, Any]):
    """
    Generate Chain-of-Thought reasoning from clinical data.
    
    This is the core innovation endpoint for JAMIA/BMC publication.
    Generates structured, explainable diagnostic reasoning with classical references.
    """
    if not COT_MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Chain-of-Thought modules not available"
        )
    
    try:
        pulse_grid = data.get("pulse_grid", {})
        symptoms = data.get("symptoms", [])
        chief_complaint = data.get("chief_complaint", "")
        patient_info = data.get("patient_info", {})
        
        if not chief_complaint:
            raise HTTPException(status_code=400, detail="Chief complaint is required")
        
        # Generate Chain-of-Thought
        cot = generate_chain_of_thought(
            pulse_grid_data=pulse_grid,
            symptoms=symptoms,
            chief_complaint=chief_complaint,
            patient_info=patient_info
        )
        
        return {
            "status": "success",
            "chain_of_thought": cot.to_dict()
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate")
async def evaluate_diagnosis_endpoint(data: Dict[str, Any]):
    """
    Evaluate AI diagnosis against expert ground truth.
    
    Used for clinical validation studies.
    Returns accuracy metrics and consistency scores.
    """
    if not COT_MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Evaluation modules not available"
        )
    
    try:
        ai_syndrome = data.get("ai_syndrome", "")
        expert_syndrome = data.get("expert_syndrome", "")
        ai_formula = data.get("ai_formula", "")
        expert_formula = data.get("expert_formula", "")
        acceptability_score = data.get("acceptability_score", 3)
        
        # Create evaluation result
        result = EvaluationResult(
            case_id=data.get("case_id", "unknown"),
            predicted_syndrome=ai_syndrome,
            actual_syndrome=expert_syndrome,
            predicted_formula=ai_formula,
            actual_formula=expert_formula,
            acceptability_score=acceptability_score
        )
        
        # Calculate metrics
        syndrome_match = ai_syndrome == expert_syndrome
        formula_match = ai_formula == expert_formula
        
        return {
            "status": "success",
            "evaluation": {
                "syndrome_correct": syndrome_match,
                "formula_correct": formula_match,
                "acceptability_score": acceptability_score,
                "overall_assessment": "acceptable" if acceptability_score >= 3 else "unacceptable"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/corpus/stats")
async def get_corpus_stats():
    """
    Get statistics about the TCM Chain-of-Thought corpus.
    
    Returns counts of syndromes, formulas, and classical references.
    """
    if not COT_MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Corpus modules not available"
        )
    
    try:
        stats = {
            "corpus_name": "TCM-CoT-Corpus",
            "version": "1.0.0",
            "knowledge_base": {
                "classical_clauses": len(knowledge_base.clauses),
                "formulas": len(knowledge_base.formulas),
                "six_meridian_patterns": len(knowledge_base.six_meridian),
                "herb_compatibility_rules": sum(
                    len(rules) for rules in knowledge_base.herb_rules.values()
                )
            },
            "available_syndromes": [
                "太阳病", "阳明病", "少阳病", 
                "太阴病", "少阴病", "厥阴病"
            ],
            "sample_formulas": list(knowledge_base.formulas.keys())[:5]
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge/formula/{formula_name}")
async def get_formula_details(formula_name: str):
    """
    Get detailed information about a specific formula.
    """
    if not COT_MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Knowledge base modules not available"
        )
    
    formula = knowledge_base.get_formula(formula_name)
    if not formula:
        raise HTTPException(status_code=404, detail=f"Formula '{formula_name}' not found")
    
    return formula


@app.get("/api/knowledge/clause/{clause_id}")
async def get_clause_details(clause_id: str):
    """
    Get a specific classical clause from Shanghan Lun.
    """
    if not COT_MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Knowledge base modules not available"
        )
    
    clause = knowledge_base.get_clause(clause_id)
    if not clause:
        raise HTTPException(status_code=404, detail=f"Clause '{clause_id}' not found")
    
    return clause


# ============================================================
# Yuanqi Pulse Method API Endpoints (元气脉法)
# ============================================================

@app.post("/api/yuanqi/generate-cot")
async def generate_yuanqi_cot_endpoint(data: Dict[str, Any]):
    """
    Generate Chain-of-Thought reasoning using Yuanqi Pulse Method (元气脉法).
    
    This is the core innovation endpoint - generates explainable diagnostic
    reasoning based on proprietary Yuanqi Pulse Method theory.
    """
    if not COT_MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Yuanqi modules not available"
        )
    
    try:
        pulse_grid = data.get("pulse_grid", {})
        symptoms = data.get("symptoms", [])
        chief_complaint = data.get("chief_complaint", "")
        patient_info = data.get("patient_info", {})
        
        if not chief_complaint:
            raise HTTPException(status_code=400, detail="Chief complaint is required")
        
        # Generate Yuanqi Chain-of-Thought
        cot = generate_yuanqi_chain_of_thought(
            pulse_grid_data=pulse_grid,
            symptoms=symptoms,
            chief_complaint=chief_complaint,
            patient_info=patient_info
        )
        
        return {
            "status": "success",
            "method": "yuanqi_pulse_method",
            "chain_of_thought": cot.to_dict()
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/yuanqi/stats")
async def get_yuanqi_stats():
    """
    Get statistics about the Yuanqi Pulse Method knowledge base.
    """
    if not COT_MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Yuanqi modules not available"
        )
    
    try:
        stats = yuanqi_knowledge_base.get_corpus_stats()
        
        return {
            "corpus_name": "Yuanqi-Pulse-Method-Corpus",
            "version": "1.0.0",
            "description": "元气脉法诊疗知识库",
            "is_proprietary": True,
            "knowledge_base": stats,
            "pulse_patterns": [
                p.pattern_name for p in yuanqi_knowledge_base.pulse_patterns.values()
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/yuanqi/pattern/{pattern_name}")
async def get_yuanqi_pattern(pattern_name: str):
    """
    Get details of a specific Yuanqi pulse pattern.
    """
    if not COT_MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Yuanqi modules not available"
        )
    
    pattern = yuanqi_knowledge_base.get_pattern_by_name(pattern_name)
    if not pattern:
        raise HTTPException(
            status_code=404, 
            detail=f"Pattern '{pattern_name}' not found"
        )
    
    return {
        "pattern_id": pattern.pattern_id,
        "pattern_name": pattern.pattern_name,
        "key_features": pattern.key_features,
        "diagnostic_meaning": {
            "yuanqi_state": pattern.diagnostic_meaning.get("yuanqi_state", "").value 
                if hasattr(pattern.diagnostic_meaning.get("yuanqi_state", ""), "value") 
                else str(pattern.diagnostic_meaning.get("yuanqi_state", "")),
            "pathomechanism": pattern.diagnostic_meaning.get("pathomechanism", "")
        },
        "treatment_direction": pattern.treatment_direction,
        "associated_symptoms": pattern.associated_symptoms
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
