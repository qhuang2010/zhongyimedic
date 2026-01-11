"""
Yuanqi Pulse Method Knowledge Base
元气脉法知识库

This module contains the structured knowledge from Yuanqi Pulse Method (元气脉法),
a proprietary TCM diagnostic system. The knowledge is derived from teaching materials
and clinical practice.

Key Features:
1. Yuanqi-centric pulse diagnosis
2. Root assessment (元气根本评估)
3. Treatment focused on strengthening Yuanqi
"""

from typing import List, Dict, Optional, Any
from .yuanqi_pulse_schema import (
    YuanqiTheory, YuanqiPulsePattern, YuanqiDiagnosticRule,
    YuanqiTreatmentProtocol, YuanqiState, YuanqiPulseGrid
)


# ============================================================
# 元气脉法核心理论 - Core Theories
# ============================================================

YUANQI_THEORIES = {
    "YQ_THEORY_001": YuanqiTheory(
        theory_id="YQ_THEORY_001",
        category="元气本体论",
        title="元气的概念与临床识别",
        content="""
        元气是人体生命活动的根本动力，藏于肾，布于三焦。
        在脉诊中，元气的充盛与否主要通过沉取层次的脉象判断：
        - 沉取有力有神：元气充盛
        - 沉取无力空虚：元气虚损
        - 沉取欲绝：元气衰竭
        
        元气脉法的核心在于"察根"——通过沉取脉象评估元气根本。
        """,
        key_concepts=[
            {
                "concept_name": "元气",
                "definition": "先天之精所化生的生命原动力，藏于肾命门",
                "clinical_significance": "元气充足则脉象沉取有力有神，不足则沉取无力或空虚"
            },
            {
                "concept_name": "察根",
                "definition": "通过沉取脉象评估元气根本状态的诊断方法",
                "clinical_significance": "是元气脉法的核心诊断技术"
            }
        ],
        clinical_applications=[
            "通过脉诊判断元气盛衰",
            "指导扶元固本治疗",
            "评估疾病预后"
        ],
        source={"lecture_name": "元气脉法基础课程", "chapter": "第一讲"}
    ),
    
    "YQ_THEORY_002": YuanqiTheory(
        theory_id="YQ_THEORY_002",
        category="脉象诊断论",
        title="浮中沉三层诊法",
        content="""
        元气脉法强调脉诊的三层结构：浮、中、沉。
        - 浮取：反映表分、卫气状态
        - 中取：反映中焦、气血运行
        - 沉取：反映里分、元气根本
        
        重点在于浮中沉三层的对比关系：
        - 浮中可取、沉取无力：元气根虚，下元不固
        - 浮取亢盛、沉取空虚：虚阳外越，真寒假热
        - 三层均可：元气平和
        """,
        key_concepts=[
            {
                "concept_name": "浮中沉三层",
                "definition": "脉诊按压力度的三个层次，分别对应不同的病理层次",
                "clinical_significance": "通过三层对比判断虚实真假"
            }
        ],
        clinical_applications=[
            "辨别真寒假热",
            "判断病位深浅",
            "评估元气状态"
        ],
        source={"lecture_name": "元气脉法核心课程", "chapter": "第二讲"}
    )
}


# ============================================================
# 元气脉法脉象模式 - Pulse Patterns
# ============================================================

YUANQI_PULSE_PATTERNS = {
    "YQ_PULSE_001": YuanqiPulsePattern(
        pattern_id="YQ_PULSE_001",
        pattern_name="元气根虚脉",
        characteristics={
            "overall": "浮中可取，沉取无力，尤以两尺沉取空虚为著",
            "key_positions": {
                "left_chi_chen": "空虚无根",
                "right_chi_chen": "空虚无根"
            }
        },
        key_features=[
            "尺部沉取无根",
            "浮中尚可、沉取空",
            "重按欲绝"
        ],
        diagnostic_meaning={
            "yuanqi_state": YuanqiState.DEFICIENT,
            "pathomechanism": "先天真阳亏虚，命门火衰，元气不能充养脉道",
            "organ_affected": ["肾", "命门"]
        },
        differentiation=[
            {"compare_with": "普通虚脉", "key_difference": "虚脉全部无力，元气根虚脉浮中尚可、独沉取无根"},
            {"compare_with": "芤脉", "key_difference": "芤脉中空如葱管，元气根虚脉是沉取无根但中层不空"}
        ],
        treatment_direction={
            "principle": "培补元气，固护根本",
            "methods": ["温补肾阳", "填精益髓", "引火归元"]
        },
        associated_symptoms=["腰膝酸软", "畏寒肢冷", "精神萎靡", "夜尿频多"],
        source={"lecture_name": "元气脉法核心课程", "chapter": "脉象识别篇"}
    ),
    
    "YQ_PULSE_002": YuanqiPulsePattern(
        pattern_id="YQ_PULSE_002",
        pattern_name="虚阳外越脉",
        characteristics={
            "overall": "浮取亢盛有力，甚至浮大，但沉取空虚无根",
            "key_positions": {
                "fu_level": "亢盛有力",
                "chen_level": "空虚无根"
            }
        },
        key_features=[
            "浮大亢盛",
            "沉取空虚",
            "浮沉反差大"
        ],
        diagnostic_meaning={
            "yuanqi_state": YuanqiState.FLOATING,
            "pathomechanism": "元气虚衰，阴不敛阳，虚阳外越上浮",
            "organ_affected": ["肾", "心"]
        },
        differentiation=[
            {"compare_with": "洪脉", "key_difference": "洪脉浮沉皆大有力，虚阳外越脉沉取无力"},
            {"compare_with": "实热证脉", "key_difference": "实热脉三层皆有力，虚阳外越独浮取亢"}
        ],
        treatment_direction={
            "principle": "潜阳归元，引火归原",
            "methods": ["温潜", "引火归元", "交通心肾"],
            "caution": "切忌苦寒直折"
        },
        associated_symptoms=["面红如妆", "烦躁不安", "但下肢厥冷", "口干不欲饮"],
        source={"lecture_name": "元气脉法核心课程", "chapter": "脉象识别篇"}
    ),
    
    "YQ_PULSE_003": YuanqiPulsePattern(
        pattern_id="YQ_PULSE_003",
        pattern_name="元气充实脉",
        characteristics={
            "overall": "浮中沉三取均有力有神，沉取尤其稳健有根",
            "key_positions": {
                "all_levels": "均衡有力",
                "chen_level": "稳健有根"
            }
        },
        key_features=[
            "三层均有力",
            "沉取稳健",
            "脉来从容"
        ],
        diagnostic_meaning={
            "yuanqi_state": YuanqiState.ABUNDANT,
            "pathomechanism": "元气充盛，正气内守",
            "organ_affected": []
        },
        treatment_direction={
            "principle": "无需特殊治疗",
            "methods": ["调养为主"]
        },
        associated_symptoms=[],
        source={"lecture_name": "元气脉法核心课程", "chapter": "脉象识别篇"}
    )
}


# ============================================================
# 元气脉法诊断规则 - Diagnostic Rules
# ============================================================

YUANQI_DIAGNOSTIC_RULES = {
    "YQ_RULE_001": YuanqiDiagnosticRule(
        rule_id="YQ_RULE_001",
        rule_name="元气虚损诊断规则",
        trigger_conditions={
            "pulse_patterns": ["元气根虚脉"],
            "symptoms": ["腰膝酸软", "畏寒肢冷", "精神萎靡"]
        },
        reasoning_chain=[
            {
                "step": 1,
                "premise": "两尺沉取空虚无根",
                "inference": "尺部候肾，沉取候元气根本，空虚示元气亏虚",
                "conclusion": "元气虚损确立"
            },
            {
                "step": 2,
                "premise": "元气虚损 + 畏寒肢冷",
                "inference": "元气虚则阳气不能温煦四末",
                "conclusion": "阳虚证确立"
            },
            {
                "step": 3,
                "premise": "元气虚损 + 阳虚证",
                "inference": "病位在下焦，病性属虚寒",
                "conclusion": "肾阳虚证"
            }
        ],
        syndrome_conclusion="肾阳虚证（元气虚损型）",
        pathomechanism="先天真阳亏虚，命门火衰，温煦失职",
        treatment_principle="温补元阳，培固根本",
        recommended_formulas=["附子理中汤", "金匮肾气丸", "右归丸"],
        confidence=0.9
    ),
    
    "YQ_RULE_002": YuanqiDiagnosticRule(
        rule_id="YQ_RULE_002",
        rule_name="虚阳外越诊断规则",
        trigger_conditions={
            "pulse_patterns": ["虚阳外越脉"],
            "symptoms": ["面红", "烦躁", "下肢厥冷"]
        },
        reasoning_chain=[
            {
                "step": 1,
                "premise": "浮取亢盛、沉取空虚",
                "inference": "浮沉反差示阳气不能潜藏，虚阳外越",
                "conclusion": "虚阳外越确立"
            },
            {
                "step": 2,
                "premise": "面红烦躁（热象）+ 下肢厥冷（寒象）",
                "inference": "上热下寒，寒热错杂假象",
                "conclusion": "真寒假热证"
            },
            {
                "step": 3,
                "premise": "虚阳外越 + 真寒假热",
                "inference": "此为阳虚至极，阴不敛阳",
                "conclusion": "戴阳证/格阳证"
            }
        ],
        syndrome_conclusion="戴阳证（虚阳外越型）",
        pathomechanism="元气虚衰，阴不敛阳，虚阳外越",
        treatment_principle="急当回阳救逆，引火归元",
        recommended_formulas=["四逆汤", "白通汤", "潜阳丹"],
        confidence=0.85
    )
}


# ============================================================
# 元气脉法治疗方案 - Treatment Protocols
# ============================================================

YUANQI_TREATMENT_PROTOCOLS = {
    "YQ_TREAT_001": YuanqiTreatmentProtocol(
        protocol_id="YQ_TREAT_001",
        protocol_name="温补元阳法",
        indications={
            "yuanqi_state": [YuanqiState.DEFICIENT, YuanqiState.SLIGHTLY_DEFICIENT],
            "syndromes": ["肾阳虚证", "命门火衰"]
        },
        principles=["温补元阳", "培固根本"],
        methods=["温肾壮阳", "填精益髓"],
        formulas=[
            {
                "name": "附子理中汤",
                "composition": [
                    {"herb": "制附子", "dosage": "15g", "note": "先煎"},
                    {"herb": "干姜", "dosage": "10g"},
                    {"herb": "党参", "dosage": "15g"},
                    {"herb": "白术", "dosage": "15g"},
                    {"herb": "炙甘草", "dosage": "6g"}
                ],
                "indication": "脾肾阳虚，中下焦虚寒"
            },
            {
                "name": "金匮肾气丸",
                "indication": "肾阳不足，命门火衰"
            }
        ],
        medication_features=[
            "必用温阳药（附子、肉桂、干姜）",
            "配合补肾填精药",
            "中病即止，不宜过剂"
        ],
        contraindications=["阴虚火旺者禁用", "实热证禁用"],
        outcome_indicators=["两尺沉取有力", "畏寒改善", "精神好转"]
    ),
    
    "YQ_TREAT_002": YuanqiTreatmentProtocol(
        protocol_id="YQ_TREAT_002",
        protocol_name="回阳救逆法",
        indications={
            "yuanqi_state": [YuanqiState.SEVERELY_DEFICIENT, YuanqiState.DEPLETED],
            "syndromes": ["戴阳证", "格阳证", "亡阳证"]
        },
        principles=["回阳救逆", "引火归元"],
        methods=["大剂温阳", "潜阳归根"],
        formulas=[
            {
                "name": "四逆汤",
                "composition": [
                    {"herb": "制附子", "dosage": "15-30g", "note": "先煎1小时"},
                    {"herb": "干姜", "dosage": "10-15g"},
                    {"herb": "炙甘草", "dosage": "6g"}
                ],
                "indication": "少阴寒化，四肢厥逆"
            },
            {
                "name": "白通汤",
                "indication": "虚阳上越，戴阳证"
            },
            {
                "name": "潜阳丹",
                "indication": "引火归元"
            }
        ],
        medication_features=[
            "附子为主，大剂量温阳",
            "急证急治，不拘常规剂量",
            "随时观察脉象变化"
        ],
        contraindications=["真热假寒者禁用", "阴虚阳亢者禁用"],
        outcome_indicators=["四肢转温", "脉象有根", "精神好转"]
    )
}


class YuanqiKnowledgeBase:
    """
    元气脉法知识库类
    Yuanqi Pulse Method Knowledge Base Class
    """
    
    def __init__(self):
        self.theories = YUANQI_THEORIES
        self.pulse_patterns = YUANQI_PULSE_PATTERNS
        self.diagnostic_rules = YUANQI_DIAGNOSTIC_RULES
        self.treatment_protocols = YUANQI_TREATMENT_PROTOCOLS
    
    def get_theory(self, theory_id: str) -> Optional[YuanqiTheory]:
        """获取理论条目"""
        return self.theories.get(theory_id)
    
    def get_pulse_pattern(self, pattern_id: str) -> Optional[YuanqiPulsePattern]:
        """获取脉象模式"""
        return self.pulse_patterns.get(pattern_id)
    
    def get_pattern_by_name(self, pattern_name: str) -> Optional[YuanqiPulsePattern]:
        """通过名称获取脉象模式"""
        for pattern in self.pulse_patterns.values():
            if pattern.pattern_name == pattern_name:
                return pattern
        return None
    
    def match_pulse_to_patterns(self, pulse_grid: YuanqiPulseGrid) -> List[Dict[str, Any]]:
        """
        将脉象匹配到模式
        Match pulse grid to known patterns
        """
        matches = []
        
        for pattern_id, pattern in self.pulse_patterns.items():
            score = pattern.matches(pulse_grid)
            if score > 0:
                matches.append({
                    "pattern_id": pattern_id,
                    "pattern_name": pattern.pattern_name,
                    "match_score": score,
                    "pattern": pattern
                })
        
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches
    
    def assess_yuanqi(self, pulse_grid: YuanqiPulseGrid) -> Dict[str, Any]:
        """
        评估元气状态
        Assess Yuanqi state from pulse grid
        """
        state = pulse_grid.assess_yuanqi_state()
        findings = pulse_grid.get_key_findings()
        
        return {
            "yuanqi_state": state,
            "state_description": state.value,
            "key_findings": findings,
            "matched_patterns": self.match_pulse_to_patterns(pulse_grid)
        }
    
    def get_applicable_rules(
        self, 
        pulse_patterns: List[str], 
        symptoms: List[str]
    ) -> List[YuanqiDiagnosticRule]:
        """
        获取适用的诊断规则
        Get applicable diagnostic rules
        """
        applicable = []
        
        for rule in self.diagnostic_rules.values():
            trigger_patterns = rule.trigger_conditions.get("pulse_patterns", [])
            trigger_symptoms = rule.trigger_conditions.get("symptoms", [])
            
            # 检查脉象模式匹配
            pattern_match = any(p in pulse_patterns for p in trigger_patterns)
            
            # 检查症状匹配
            symptom_match = sum(1 for s in symptoms if s in trigger_symptoms)
            
            if pattern_match and symptom_match >= 1:
                applicable.append(rule)
        
        return applicable
    
    def get_treatment_protocol(
        self, 
        yuanqi_state: YuanqiState, 
        syndrome: str
    ) -> Optional[YuanqiTreatmentProtocol]:
        """
        获取治疗方案
        Get treatment protocol for given state and syndrome
        """
        for protocol in self.treatment_protocols.values():
            states = protocol.indications.get("yuanqi_state", [])
            syndromes = protocol.indications.get("syndromes", [])
            
            if yuanqi_state in states or syndrome in syndromes:
                return protocol
        
        return None
    
    def get_corpus_stats(self) -> Dict[str, int]:
        """获取语料库统计"""
        return {
            "theories": len(self.theories),
            "pulse_patterns": len(self.pulse_patterns),
            "diagnostic_rules": len(self.diagnostic_rules),
            "treatment_protocols": len(self.treatment_protocols)
        }


# 创建单例实例
yuanqi_knowledge_base = YuanqiKnowledgeBase()
