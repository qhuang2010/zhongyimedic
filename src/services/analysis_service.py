from typing import Dict, Any

def analyze_pulse_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Advanced Rule-Based Analysis Simulation based on Shanghan Lun and Zheng Qin'an (Fire Spirit School) logic.
    This is the core business logic for pulse analysis.
    """
    medical_record = data.get("medical_record", {})
    pulse_grid = data.get("pulse_grid", {})
    
    complaint = medical_record.get("complaint", "")
    prescription = medical_record.get("prescription", "")
    
    # 1. Parse Pulse Data
    # Helper to aggregate from both hands
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
    
    def check_keywords(qualities, keywords):
        for q in qualities:
            for k in keywords:
                if k in q:
                    return True
        return False
    
    def check_overall(keywords):
        for k in keywords:
            if k in overall_pulse:
                return True
        return False

    is_floating_tight = check_keywords(fu_qualities, ["紧", "弦"]) or check_overall(["紧", "弦"])
    is_floating_weak = check_keywords(fu_qualities, ["细", "弱", "微", "无"]) or check_overall(["细", "弱", "虚"])
    is_deep_empty = check_keywords(chen_qualities, ["无", "空", "微", "弱"]) or check_overall(["无根", "空", "豁"])
    is_middle_empty = check_keywords(zhong_qualities, ["空", "无", "弱"])
    
    # 2. Logic Engine
    pattern = "Unknown"
    consistency_comment = ""
    suggestion = ""
    
    if is_deep_empty and (check_keywords(fu_qualities, ["大", "浮", "紧", "弦", "细"])):
        pattern = "Rootless Yang"
        consistency_comment = (
            "【郑钦安视角】脉象呈现“寸关尺浮取可见，但沉取无力或空虚”，此乃“阳气外浮，下元虚寒”之象。\n"
            "虽浮部见紧或细，切不可误认为单纯表实证。沉取无根，说明肾阳虚衰，真阳不能潜藏，反逼虚阳上浮外越。\n"
            "若主诉有“头晕、面红”等看似热象，实为“真寒假热”。"
        )
        suggestion = (
            "建议：急当扶阳抑阴，引火归元。\n"
            "切忌使用发散风寒之辛温解表药（如麻黄）或苦寒直折之药，恐耗散仅存之真阳。\n"
            "推荐方剂：四逆汤、白通汤或潜阳丹加减。"
        )
    elif is_floating_tight and not is_deep_empty:
        pattern = "Taiyang Cold"
        consistency_comment = (
            "【伤寒论视角】脉浮而紧，乃太阳伤寒表实证之典型脉象。\n"
            "“寸口脉浮而紧，浮则为风，紧则为寒”，寒邪束表，卫阳闭郁。\n"
            "若主诉伴有“恶寒、发热、身痛、无汗”，则脉证高度一致。"
        )
        suggestion = (
            "建议：辛温解表，发汗宣肺。\n"
            "推荐方剂：麻黄汤加减。\n"
            "注意：若患者素体汗多或尺脉迟弱，需防过汗伤阳，可考虑桂枝汤或桂枝加葛根汤。"
        )
    elif is_middle_empty:
        pattern = "Middle Deficiency"
        consistency_comment = (
            "【脉象分析】关部（中候）见空/弱，提示中焦脾胃之气虚损。\n"
            "脾胃为后天之本，中气不足则生化无源。"
        )
        suggestion = (
            "建议：健脾益气，调和中焦。\n"
            "推荐方剂：理中汤或补中益气汤加减。"
        )
    else:
        consistency_comment = (
            "脉象显示：浮部" + "/".join([q for q in fu_qualities if q]) + 
            "，沉部" + "/".join([q for q in chen_qualities if q]) + "。\n"
            "需结合“望闻问切”四诊合参。若浮沉皆无力，多属气血两虚；若脉象有力，多属实证。"
        )
        suggestion = "建议结合舌苔及其他临床症状进一步辨证。"

    # 3. Prescription Analysis
    prescription_comment = ""
    if not prescription or len(prescription) < 2:
        prescription_comment = "未提供完整处方，无法进行具体药物对证分析。"
    else:
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
