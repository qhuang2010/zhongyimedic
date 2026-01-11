"""
TCM Classical Knowledge Base
中医经典知识库

This module contains structured knowledge from classical TCM texts,
particularly focusing on Shanghan Lun (伤寒论) for syndrome-formula mapping.

Key Features:
1. Six Meridian Syndrome Patterns (六经病证)
2. Classical Clauses (经典条文)
3. Formula-Syndrome Correspondence (方证对应)
4. Herb Compatibility Rules (药物配伍)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


# ============================================================
# 《伤寒论》条文索引 - Shanghan Lun Clause Index
# ============================================================

SHANGHAN_LUN_CLAUSES = {
    # 太阳病篇
    "TAIYANG_001": {
        "clause_number": 1,
        "original_text": "太阳之为病，脉浮，头项强痛而恶寒。",
        "translation": "Taiyang disease manifests with floating pulse, headache, stiff neck, and aversion to cold.",
        "syndrome": "太阳病提纲",
        "key_symptoms": ["脉浮", "头项强痛", "恶寒"],
        "clinical_significance": "太阳病诊断要点：脉浮为邪在表，头项强痛为太阳经循行所过，恶寒为卫阳被郁"
    },
    "TAIYANG_002": {
        "clause_number": 2,
        "original_text": "太阳病，发热，汗出，恶风，脉缓者，名为中风。",
        "translation": "Taiyang disease with fever, sweating, aversion to wind, and moderate pulse is called wind-strike.",
        "syndrome": "太阳中风证",
        "key_symptoms": ["发热", "汗出", "恶风", "脉缓"],
        "formula": "桂枝汤",
        "clinical_significance": "太阳中风为表虚证，营卫不和，当用桂枝汤调和营卫"
    },
    "TAIYANG_003": {
        "clause_number": 3,
        "original_text": "太阳病，或已发热，或未发热，必恶寒，体痛，呕逆，脉阴阳俱紧者，名为伤寒。",
        "translation": "Taiyang disease with or without fever, but definitely aversion to cold, body pain, vomiting, and tight pulse on both positions is called cold damage.",
        "syndrome": "太阳伤寒证",
        "key_symptoms": ["恶寒", "体痛", "呕逆", "脉紧"],
        "formula": "麻黄汤",
        "clinical_significance": "太阳伤寒为表实证，寒邪束表，当用麻黄汤发汗解表"
    },
    "TAIYANG_012": {
        "clause_number": 12,
        "original_text": "太阳中风，阳浮而阴弱，阳浮者，热自发；阴弱者，汗自出。啬啬恶寒，淅淅恶风，翕翕发热，鼻鸣干呕者，桂枝汤主之。",
        "translation": "In Taiyang wind-strike, the yang is floating and yin is weak...",
        "syndrome": "太阳中风证",
        "key_symptoms": ["恶寒", "恶风", "发热", "汗出", "鼻鸣", "干呕"],
        "formula": "桂枝汤",
        "clinical_significance": "桂枝汤证完整描述，为营卫不和之典型表现"
    },
    "TAIYANG_035": {
        "clause_number": 35,
        "original_text": "太阳病，头痛发热，身疼腰痛，骨节疼痛，恶风无汗而喘者，麻黄汤主之。",
        "translation": "Taiyang disease with headache, fever, body pain, low back pain, joint pain, aversion to wind, no sweating and wheezing, Mahuang Tang is the master formula.",
        "syndrome": "太阳伤寒证",
        "key_symptoms": ["头痛", "发热", "身疼", "腰痛", "骨节疼痛", "恶风", "无汗", "喘"],
        "formula": "麻黄汤",
        "clinical_significance": "麻黄汤证完整描述，为寒邪束表之典型表现"
    },
    
    # 少阴病篇
    "SHAOYIN_281": {
        "clause_number": 281,
        "original_text": "少阴之为病，脉微细，但欲寐也。",
        "translation": "Shaoyin disease manifests with faint and thin pulse, with only desire to sleep.",
        "syndrome": "少阴病提纲",
        "key_symptoms": ["脉微细", "但欲寐"],
        "clinical_significance": "少阴病诊断要点：心肾阳虚，脉道不充则脉微细，神失所养则但欲寐"
    },
    "SHAOYIN_323": {
        "clause_number": 323,
        "original_text": "少阴病，脉沉者，急温之，宜四逆汤。",
        "translation": "Shaoyin disease with sunken pulse should be urgently warmed, Sini Tang is appropriate.",
        "syndrome": "少阴寒化证",
        "key_symptoms": ["脉沉"],
        "formula": "四逆汤",
        "clinical_significance": "少阴寒化证的急救方，回阳救逆"
    }
}


# ============================================================
# 方证对应关系 - Formula-Syndrome Correspondence
# ============================================================

FORMULA_SYNDROME_MAP = {
    "桂枝汤": {
        "pinyin": "Guizhi Tang",
        "english": "Cinnamon Twig Decoction",
        "source": "《伤寒论》",
        "composition": [
            {"herb": "桂枝", "dosage": "9g", "role": "君"},
            {"herb": "芍药", "dosage": "9g", "role": "臣"},
            {"herb": "甘草", "dosage": "6g", "role": "佐使"},
            {"herb": "生姜", "dosage": "9g", "role": "佐"},
            {"herb": "大枣", "dosage": "3枚", "role": "佐"}
        ],
        "functions": ["解肌发表", "调和营卫"],
        "indications": {
            "syndrome": "太阳中风证",
            "symptoms": ["发热", "汗出", "恶风", "脉浮缓"],
            "pathomechanism": "风寒袭表，营卫不和"
        },
        "contraindications": ["表实无汗者", "温病初起者"],
        "classical_clause": "TAIYANG_012"
    },
    "麻黄汤": {
        "pinyin": "Mahuang Tang",
        "english": "Ephedra Decoction",
        "source": "《伤寒论》",
        "composition": [
            {"herb": "麻黄", "dosage": "9g", "role": "君"},
            {"herb": "桂枝", "dosage": "6g", "role": "臣"},
            {"herb": "杏仁", "dosage": "9g", "role": "佐"},
            {"herb": "甘草", "dosage": "3g", "role": "使"}
        ],
        "functions": ["发汗解表", "宣肺平喘"],
        "indications": {
            "syndrome": "太阳伤寒证",
            "symptoms": ["恶寒", "发热", "头身疼痛", "无汗", "喘", "脉浮紧"],
            "pathomechanism": "风寒束表，肺气不宣"
        },
        "contraindications": ["表虚自汗者", "阳虚体弱者", "孕妇慎用"],
        "classical_clause": "TAIYANG_035"
    },
    "四逆汤": {
        "pinyin": "Sini Tang",
        "english": "Frigid Extremities Decoction",
        "source": "《伤寒论》",
        "composition": [
            {"herb": "附子", "dosage": "15g", "role": "君"},
            {"herb": "干姜", "dosage": "9g", "role": "臣"},
            {"herb": "甘草", "dosage": "6g", "role": "佐使"}
        ],
        "functions": ["回阳救逆", "温中祛寒"],
        "indications": {
            "syndrome": "少阴寒化证",
            "symptoms": ["四肢厥逆", "恶寒蜷卧", "呕吐不渴", "腹痛下利", "神衰欲寐", "脉微细"],
            "pathomechanism": "心肾阳衰，阴寒内盛"
        },
        "contraindications": ["阴虚火旺者", "热证厥逆者"],
        "classical_clause": "SHAOYIN_323"
    },
    "小柴胡汤": {
        "pinyin": "Xiao Chaihu Tang",
        "english": "Minor Bupleurum Decoction",
        "source": "《伤寒论》",
        "composition": [
            {"herb": "柴胡", "dosage": "24g", "role": "君"},
            {"herb": "黄芩", "dosage": "9g", "role": "臣"},
            {"herb": "人参", "dosage": "9g", "role": "佐"},
            {"herb": "半夏", "dosage": "9g", "role": "佐"},
            {"herb": "甘草", "dosage": "6g", "role": "使"},
            {"herb": "生姜", "dosage": "9g", "role": "佐"},
            {"herb": "大枣", "dosage": "4枚", "role": "佐"}
        ],
        "functions": ["和解少阳", "疏肝理气"],
        "indications": {
            "syndrome": "少阳病",
            "symptoms": ["寒热往来", "胸胁苦满", "默默不欲饮食", "心烦喜呕", "口苦", "咽干", "目眩", "脉弦"],
            "pathomechanism": "邪犯少阳，枢机不利"
        },
        "contraindications": ["阴虚血少者"],
        "classical_clause": "SHAOYANG_096"
    }
}


# ============================================================
# 药物配伍规则 - Herb Compatibility Rules
# ============================================================

HERB_COMPATIBILITY = {
    # 相须 - Mutual Enhancement
    "mutual_enhancement": [
        {"herbs": ["附子", "干姜"], "effect": "增强回阳救逆之功"},
        {"herbs": ["麻黄", "桂枝"], "effect": "增强发汗解表之力"},
        {"herbs": ["黄芪", "党参"], "effect": "增强补气之效"},
    ],
    
    # 相使 - Mutual Assistance
    "mutual_assistance": [
        {"herbs": ["黄芪", "防风"], "effect": "黄芪益气固表，防风祛风"},
        {"herbs": ["茯苓", "白术"], "effect": "健脾利水"},
    ],
    
    # 相畏/相杀 - Neutralization
    "neutralization": [
        {"herbs": ["半夏", "生姜"], "effect": "生姜制半夏之毒"},
        {"herbs": ["附子", "甘草"], "effect": "甘草缓附子之峻"},
    ],
    
    # 相恶 - Incompatibility (reduce effect)
    "incompatibility": [
        {"herbs": ["人参", "莱菔子"], "effect": "莱菔子消减人参补气之功"},
    ],
    
    # 相反 - Prohibited Combinations (十八反)
    "prohibited": [
        {"herbs": ["甘草", "甘遂"], "reason": "十八反"},
        {"herbs": ["甘草", "大戟"], "reason": "十八反"},
        {"herbs": ["甘草", "海藻"], "reason": "十八反"},
        {"herbs": ["甘草", "芫花"], "reason": "十八反"},
        {"herbs": ["乌头", "贝母"], "reason": "十八反"},
        {"herbs": ["乌头", "瓜蒌"], "reason": "十八反"},
        {"herbs": ["乌头", "半夏"], "reason": "十八反"},
        {"herbs": ["乌头", "白蔹"], "reason": "十八反"},
        {"herbs": ["乌头", "白及"], "reason": "十八反"},
        {"herbs": ["藜芦", "人参"], "reason": "十八反"},
        {"herbs": ["藜芦", "沙参"], "reason": "十八反"},
        {"herbs": ["藜芦", "丹参"], "reason": "十八反"},
        {"herbs": ["藜芦", "玄参"], "reason": "十八反"},
        {"herbs": ["藜芦", "细辛"], "reason": "十八反"},
        {"herbs": ["藜芦", "芍药"], "reason": "十八反"},
    ]
}


# ============================================================
# 六经辨证规则 - Six Meridian Differentiation Rules
# ============================================================

SIX_MERIDIAN_PATTERNS = {
    "太阳病": {
        "nature": "表证",
        "location": "体表、肌肤",
        "pulse": ["浮"],
        "key_symptoms": ["恶寒", "发热", "头项强痛"],
        "subtypes": {
            "中风": {
                "symptoms": ["发热", "汗出", "恶风", "脉浮缓"],
                "formula": "桂枝汤"
            },
            "伤寒": {
                "symptoms": ["恶寒", "发热", "无汗", "身痛", "脉浮紧"],
                "formula": "麻黄汤"
            }
        },
        "treatment_principle": "发汗解表"
    },
    "阳明病": {
        "nature": "里热证",
        "location": "胃肠",
        "pulse": ["大", "洪"],
        "key_symptoms": ["身热", "汗出", "不恶寒反恶热"],
        "subtypes": {
            "经证": {
                "symptoms": ["大热", "大汗", "大渴", "脉洪大"],
                "formula": "白虎汤"
            },
            "腑证": {
                "symptoms": ["潮热", "谵语", "腹满痛", "大便秘结"],
                "formula": "承气汤类"
            }
        },
        "treatment_principle": "清热"
    },
    "少阳病": {
        "nature": "半表半里证",
        "location": "胸胁",
        "pulse": ["弦"],
        "key_symptoms": ["寒热往来", "胸胁苦满", "口苦", "咽干", "目眩"],
        "subtypes": {},
        "treatment_principle": "和解少阳",
        "formula": "小柴胡汤"
    },
    "太阴病": {
        "nature": "里虚寒证",
        "location": "脾胃",
        "pulse": ["缓", "弱"],
        "key_symptoms": ["腹满而吐", "食不下", "自利", "时腹自痛"],
        "subtypes": {},
        "treatment_principle": "温中健脾",
        "formula": "理中汤"
    },
    "少阴病": {
        "nature": "里虚寒证（心肾）",
        "location": "心肾",
        "pulse": ["微", "细"],
        "key_symptoms": ["脉微细", "但欲寐"],
        "subtypes": {
            "寒化": {
                "symptoms": ["四肢厥逆", "下利清谷", "脉微欲绝"],
                "formula": "四逆汤"
            },
            "热化": {
                "symptoms": ["心烦不得眠", "口燥咽干"],
                "formula": "黄连阿胶汤"
            }
        },
        "treatment_principle": "回阳救逆或滋阴降火"
    },
    "厥阴病": {
        "nature": "寒热错杂证",
        "location": "肝",
        "pulse": ["弦", "细"],
        "key_symptoms": ["消渴", "气上撞心", "心中疼热", "饥而不欲食", "食则吐蛔"],
        "subtypes": {},
        "treatment_principle": "调和寒热",
        "formula": "乌梅丸"
    }
}


class KnowledgeBase:
    """
    中医经典知识库类
    TCM Classical Knowledge Base Class
    """
    
    def __init__(self):
        self.clauses = SHANGHAN_LUN_CLAUSES
        self.formulas = FORMULA_SYNDROME_MAP
        self.herb_rules = HERB_COMPATIBILITY
        self.six_meridian = SIX_MERIDIAN_PATTERNS
    
    def get_clause(self, clause_id: str) -> Optional[Dict]:
        """获取条文"""
        return self.clauses.get(clause_id)
    
    def get_formula(self, formula_name: str) -> Optional[Dict]:
        """获取方剂信息"""
        return self.formulas.get(formula_name)
    
    def match_syndrome_to_formula(self, symptoms: List[str], pulse: List[str]) -> List[Dict]:
        """
        根据症状和脉象匹配方剂
        Match formulas based on symptoms and pulse
        """
        matches = []
        
        for formula_name, formula_info in self.formulas.items():
            indications = formula_info.get("indications", {})
            formula_symptoms = indications.get("symptoms", [])
            
            # 计算症状匹配度
            symptom_match_count = sum(1 for s in symptoms if s in formula_symptoms)
            total_symptoms = len(formula_symptoms)
            
            if total_symptoms > 0:
                match_score = symptom_match_count / total_symptoms
                
                if match_score >= 0.3:  # 至少30%症状匹配
                    matches.append({
                        "formula_name": formula_name,
                        "match_score": match_score,
                        "matched_symptoms": [s for s in symptoms if s in formula_symptoms],
                        "formula_info": formula_info
                    })
        
        # 按匹配度排序
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches
    
    def check_herb_compatibility(self, herbs: List[str]) -> Dict[str, List]:
        """
        检查药物配伍
        Check herb compatibility
        """
        result = {
            "enhancements": [],
            "warnings": [],
            "prohibited": []
        }
        
        # 检查禁忌配伍
        for rule in self.herb_rules["prohibited"]:
            if all(h in herbs for h in rule["herbs"]):
                result["prohibited"].append({
                    "herbs": rule["herbs"],
                    "reason": rule["reason"]
                })
        
        # 检查相恶配伍
        for rule in self.herb_rules["incompatibility"]:
            if all(h in herbs for h in rule["herbs"]):
                result["warnings"].append({
                    "herbs": rule["herbs"],
                    "effect": rule["effect"]
                })
        
        # 检查增强配伍
        for rule in self.herb_rules["mutual_enhancement"]:
            if all(h in herbs for h in rule["herbs"]):
                result["enhancements"].append({
                    "herbs": rule["herbs"],
                    "effect": rule["effect"]
                })
        
        return result
    
    def identify_six_meridian_pattern(self, symptoms: List[str], pulse: List[str]) -> List[Dict]:
        """
        六经辨证
        Identify Six Meridian Pattern
        """
        matches = []
        
        for pattern_name, pattern_info in self.six_meridian.items():
            pattern_symptoms = pattern_info.get("key_symptoms", [])
            pattern_pulse = pattern_info.get("pulse", [])
            
            # 症状匹配
            symptom_matches = [s for s in symptoms if s in pattern_symptoms]
            # 脉象匹配
            pulse_matches = [p for p in pulse if p in pattern_pulse]
            
            if symptom_matches or pulse_matches:
                score = (len(symptom_matches) * 2 + len(pulse_matches)) / \
                        (len(pattern_symptoms) * 2 + len(pattern_pulse))
                
                matches.append({
                    "pattern": pattern_name,
                    "score": score,
                    "matched_symptoms": symptom_matches,
                    "matched_pulse": pulse_matches,
                    "pattern_info": pattern_info
                })
        
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches
    
    def get_classical_reference(self, syndrome: str) -> List[Dict]:
        """
        获取证型的经典依据
        Get classical references for a syndrome
        """
        references = []
        
        for clause_id, clause_info in self.clauses.items():
            if syndrome in clause_info.get("syndrome", ""):
                references.append({
                    "clause_id": clause_id,
                    "clause_number": clause_info.get("clause_number"),
                    "original_text": clause_info.get("original_text"),
                    "clinical_significance": clause_info.get("clinical_significance")
                })
        
        return references


# 单例实例
knowledge_base = KnowledgeBase()
