"""
TCM Chain-of-Thought Generator
中医思维链生成器

Generates structured reasoning chains from clinical data,
following the classical TCM diagnostic process:
四诊 → 辨证 → 论治 → 方药

This module is the core innovation for JAMIA/BMC publication,
demonstrating explainable AI in Traditional Chinese Medicine.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from .tcm_cot_schema import (
    ChainOfThought, DiagnosticEvidence, DiagnosticMethod,
    PulseGridData, PulseQuality, ReasoningStep,
    SyndromeDifferentiation, SyndromeType,
    TreatmentPrinciple, PrescriptionRationale, HerbEntry
)
from .knowledge_base import knowledge_base


class ChainOfThoughtGenerator:
    """
    中医思维链生成器
    TCM Chain-of-Thought Generator
    
    Generates explainable diagnostic reasoning chains from:
    1. Pulse grid data (脉象九宫格)
    2. Four diagnostic methods observations (四诊信息)
    3. Chief complaints (主诉)
    
    Output: Structured ChainOfThought object with full reasoning trace
    """
    
    def __init__(self):
        self.kb = knowledge_base
        self.step_counter = 0
    
    def generate_cot(
        self,
        pulse_grid_data: Dict[str, Any],
        symptoms: List[str],
        chief_complaint: str,
        patient_info: Optional[Dict] = None
    ) -> ChainOfThought:
        """
        生成完整的思维链
        Generate complete Chain-of-Thought
        
        Args:
            pulse_grid_data: 脉象九宫格数据
            symptoms: 症状列表
            chief_complaint: 主诉
            patient_info: 患者基本信息（可选）
            
        Returns:
            ChainOfThought: 完整的思维链对象
        """
        self.step_counter = 0
        
        # 1. 创建CoT对象
        cot = ChainOfThought(
            cot_id=str(uuid.uuid4()),
            chief_complaint=chief_complaint,
            patient_demographics=patient_info or {}
        )
        
        # 2. 解析脉象数据
        cot.pulse_grid = self._parse_pulse_grid(pulse_grid_data)
        
        # 3. 收集四诊信息
        cot.diagnostic_evidence = self._collect_diagnostic_evidence(
            pulse_grid_data, symptoms
        )
        
        # 4. 生成推理链
        reasoning_steps = []
        
        # Step 1: 四诊合参
        reasoning_steps.append(self._generate_four_methods_synthesis(
            cot.diagnostic_evidence, cot.pulse_grid
        ))
        
        # 5. 六经辨证
        pulse_qualities = self._extract_pulse_qualities(pulse_grid_data)
        six_meridian_result = self.kb.identify_six_meridian_pattern(
            symptoms, pulse_qualities
        )
        
        # Step 2: 六经辨证推理
        syndrome_step, syndrome = self._generate_syndrome_differentiation(
            six_meridian_result, symptoms, pulse_qualities
        )
        reasoning_steps.append(syndrome_step)
        cot.syndrome_differentiation = syndrome
        
        # 6. 确定治则
        # Step 3: 确立治法
        treatment_step, treatment = self._generate_treatment_principle(syndrome)
        reasoning_steps.append(treatment_step)
        cot.treatment_principle = treatment
        
        # 7. 选方用药
        formula_matches = self.kb.match_syndrome_to_formula(
            symptoms, pulse_qualities
        )
        
        # Step 4: 方药选择
        prescription_step, prescription = self._generate_prescription(
            formula_matches, syndrome, treatment
        )
        reasoning_steps.append(prescription_step)
        cot.prescription = prescription
        
        # 8. 设置推理链
        cot.reasoning_steps = reasoning_steps
        
        # 9. 预期疗效
        cot.expected_outcome = self._generate_expected_outcome(syndrome, treatment)
        
        return cot
    
    def _parse_pulse_grid(self, data: Dict[str, Any]) -> PulseGridData:
        """解析脉象九宫格数据"""
        pulse_grid = PulseGridData()
        
        # 解析各宫格数据
        if "positions" in data:
            positions = data["positions"]
            
            # 左手三部
            pulse_grid.left_cun = self._parse_position(positions.get("1", {}))
            pulse_grid.left_guan = self._parse_position(positions.get("2", {}))
            pulse_grid.left_chi = self._parse_position(positions.get("3", {}))
            
            # 右手三部
            pulse_grid.right_cun = self._parse_position(positions.get("4", {}))
            pulse_grid.right_guan = self._parse_position(positions.get("5", {}))
            pulse_grid.right_chi = self._parse_position(positions.get("6", {}))
            
            # 总体评价
            pulse_grid.overall_assessment = positions.get("7", {}).get("value", "")
            
            # 脉象特征
            features_str = positions.get("8", {}).get("value", "")
            pulse_grid.pulse_features = self._parse_pulse_features(features_str)
            
            # 诊断建议
            pulse_grid.diagnostic_suggestion = positions.get("9", {}).get("value", "")
        
        return pulse_grid
    
    def _parse_position(self, pos_data: Dict) -> Dict[str, Any]:
        """解析单个宫格位置数据"""
        return {
            "浮": pos_data.get("levels", {}).get("fu", ""),
            "中": pos_data.get("levels", {}).get("zhong", ""),
            "沉": pos_data.get("levels", {}).get("chen", ""),
            "overall": pos_data.get("value", "")
        }
    
    def _parse_pulse_features(self, features_str: str) -> List[PulseQuality]:
        """解析脉象特征字符串为枚举列表"""
        features = []
        quality_map = {
            "浮": PulseQuality.FLOATING,
            "沉": PulseQuality.SINKING,
            "迟": PulseQuality.SLOW,
            "数": PulseQuality.RAPID,
            "虚": PulseQuality.DEFICIENT,
            "实": PulseQuality.EXCESSIVE,
            "滑": PulseQuality.SLIPPERY,
            "涩": PulseQuality.ROUGH,
            "弦": PulseQuality.WIRY,
            "细": PulseQuality.THIN,
            "洪": PulseQuality.SURGING,
            "微": PulseQuality.FAINT
        }
        
        for char in features_str:
            if char in quality_map:
                features.append(quality_map[char])
        
        return features
    
    def _extract_pulse_qualities(self, data: Dict[str, Any]) -> List[str]:
        """从脉象数据中提取特征"""
        qualities = []
        
        if "positions" in data:
            features_str = data["positions"].get("8", {}).get("value", "")
            for char in features_str:
                if char in ["浮", "沉", "迟", "数", "虚", "实", "滑", "涩", "弦", "细", "洪", "微"]:
                    if char not in qualities:
                        qualities.append(char)
        
        return qualities
    
    def _collect_diagnostic_evidence(
        self,
        pulse_data: Dict,
        symptoms: List[str]
    ) -> List[DiagnosticEvidence]:
        """收集四诊依据"""
        evidence_list = []
        
        # 切诊 - 脉象
        pulse_features = self._extract_pulse_qualities(pulse_data)
        if pulse_features:
            evidence_list.append(DiagnosticEvidence(
                method=DiagnosticMethod.PALPATION,
                observation=f"脉象：{', '.join(pulse_features)}",
                clinical_significance=self._interpret_pulse(pulse_features),
                confidence=0.9
            ))
        
        # 问诊 - 症状
        for symptom in symptoms:
            significance = self._get_symptom_significance(symptom)
            evidence_list.append(DiagnosticEvidence(
                method=DiagnosticMethod.INQUIRY,
                observation=symptom,
                clinical_significance=significance,
                confidence=0.85
            ))
        
        return evidence_list
    
    def _interpret_pulse(self, qualities: List[str]) -> str:
        """解释脉象临床意义"""
        interpretations = {
            "浮": "邪在表、阳气向外",
            "沉": "邪在里、阳气不足",
            "迟": "寒证、阳虚",
            "数": "热证、阴虚",
            "虚": "正气不足",
            "实": "邪气亢盛",
            "弦": "肝胆病、痛证",
            "细": "血虚、阴虚",
            "微": "阳气衰微"
        }
        
        meanings = [interpretations.get(q, "") for q in qualities if q in interpretations]
        return "；".join(filter(None, meanings))
    
    def _get_symptom_significance(self, symptom: str) -> str:
        """获取症状临床意义"""
        symptom_map = {
            "恶寒": "表证、阳虚",
            "发热": "表证、里热",
            "汗出": "表虚、营卫不和",
            "无汗": "表实、寒邪束表",
            "头痛": "表证、肝阳上亢",
            "身痛": "表证、寒湿阻络",
            "口苦": "少阳病、肝胆郁热",
            "口渴": "热证、津液不足",
            "不渴": "寒证、湿证"
        }
        return symptom_map.get(symptom, "待辨析")
    
    def _generate_four_methods_synthesis(
        self,
        evidence: List[DiagnosticEvidence],
        pulse_grid: PulseGridData
    ) -> ReasoningStep:
        """生成四诊合参推理步骤"""
        self.step_counter += 1
        
        # 汇总所有观察
        observations = [e.observation for e in evidence]
        significances = [e.clinical_significance for e in evidence]
        
        premise = f"患者症状体征：{'; '.join(observations)}"
        inference = f"四诊分析：各症状分别提示{'; '.join(filter(None, significances))}"
        conclusion = "综合四诊信息，需进一步进行六经辨证"
        
        return ReasoningStep(
            step_number=self.step_counter,
            reasoning_type="归纳",
            premise=premise,
            inference=inference,
            conclusion=conclusion,
            classical_reference="《伤寒论》：观其脉证，知犯何逆，随证治之",
            confidence=0.85
        )
    
    def _generate_syndrome_differentiation(
        self,
        six_meridian_result: List[Dict],
        symptoms: List[str],
        pulse: List[str]
    ) -> tuple:
        """生成辨证推理步骤"""
        self.step_counter += 1
        
        # 获取最佳匹配
        if six_meridian_result:
            best_match = six_meridian_result[0]
            pattern_name = best_match["pattern"]
            pattern_info = best_match["pattern_info"]
            
            # 确定证型
            syndrome_type = self._map_pattern_to_syndrome(pattern_name)
            
            # 获取经典依据
            classical_refs = self.kb.get_classical_reference(pattern_name)
            classical_clause = classical_refs[0]["original_text"] if classical_refs else None
            classical_source = "《伤寒论》" if classical_refs else None
            
            syndrome = SyndromeDifferentiation(
                primary_syndrome=syndrome_type,
                evidence_summary=f"根据症状{best_match['matched_symptoms']}和脉象{best_match['matched_pulse']}",
                key_symptoms=best_match["matched_symptoms"],
                key_signs=pulse,
                six_meridian_analysis=f"符合{pattern_name}诊断标准",
                pathomechanism=pattern_info.get("treatment_principle", ""),
                classical_clause=classical_clause,
                classical_source=classical_source
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="演绎",
                premise=f"主症：{', '.join(symptoms)}；脉象：{', '.join(pulse)}",
                inference=f"根据《伤寒论》六经辨证，{', '.join(best_match['matched_symptoms'])}为{pattern_name}之主症，{', '.join(best_match['matched_pulse'])}脉为其脉象特征",
                conclusion=f"辨证为{pattern_name}",
                classical_reference=classical_clause,
                confidence=best_match["score"]
            )
        else:
            syndrome = SyndromeDifferentiation(
                primary_syndrome=SyndromeType.EXTERIOR,
                evidence_summary="证据不足，需进一步诊察"
            )
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="推断",
                premise=f"主症：{', '.join(symptoms)}",
                inference="症状信息不足以明确六经归属",
                conclusion="待进一步辨证",
                confidence=0.5
            )
        
        return step, syndrome
    
    def _map_pattern_to_syndrome(self, pattern_name: str) -> SyndromeType:
        """将证型名称映射到枚举"""
        mapping = {
            "太阳病": SyndromeType.TAIYANG,
            "阳明病": SyndromeType.YANGMING,
            "少阳病": SyndromeType.SHAOYANG,
            "太阴病": SyndromeType.TAIYIN,
            "少阴病": SyndromeType.SHAOYIN,
            "厥阴病": SyndromeType.JUEYIN
        }
        return mapping.get(pattern_name, SyndromeType.EXTERIOR)
    
    def _generate_treatment_principle(
        self,
        syndrome: SyndromeDifferentiation
    ) -> tuple:
        """生成治则推理步骤"""
        self.step_counter += 1
        
        # 根据证型确定治则
        treatment_map = {
            SyndromeType.TAIYANG: ("发汗解表", ["调和营卫"]),
            SyndromeType.YANGMING: ("清热泻火", ["通腑泄热"]),
            SyndromeType.SHAOYANG: ("和解少阳", ["疏肝理气"]),
            SyndromeType.TAIYIN: ("温中健脾", ["燥湿运脾"]),
            SyndromeType.SHAOYIN: ("回阳救逆", ["温肾壮阳"]),
            SyndromeType.JUEYIN: ("调和寒热", ["疏肝解郁"])
        }
        
        primary_syndrome = syndrome.primary_syndrome
        primary_principle, secondary = treatment_map.get(
            primary_syndrome, ("扶正祛邪", [])
        )
        
        treatment = TreatmentPrinciple(
            primary_principle=primary_principle,
            secondary_principles=secondary,
            rationale=f"根据{primary_syndrome.value}之病机，当以{primary_principle}为法",
            classical_reference=syndrome.classical_clause
        )
        
        step = ReasoningStep(
            step_number=self.step_counter,
            reasoning_type="演绎",
            premise=f"辨证为{primary_syndrome.value}",
            inference=f"{primary_syndrome.value}的治疗原则为{primary_principle}",
            conclusion=f"确立治法：{primary_principle}",
            classical_reference=f"《伤寒论》治{primary_syndrome.value}之法",
            confidence=0.9
        )
        
        return step, treatment
    
    def _generate_prescription(
        self,
        formula_matches: List[Dict],
        syndrome: SyndromeDifferentiation,
        treatment: TreatmentPrinciple
    ) -> tuple:
        """生成方药推理步骤"""
        self.step_counter += 1
        
        if formula_matches:
            best_formula = formula_matches[0]
            formula_name = best_formula["formula_name"]
            formula_info = best_formula["formula_info"]
            
            # 构建药物列表
            herbs = []
            for herb_data in formula_info.get("composition", []):
                herbs.append(HerbEntry(
                    name=herb_data["herb"],
                    dosage=herb_data["dosage"],
                    role=herb_data["role"],
                    function=f"{herb_data['role']}药",
                    rationale=f"方中{herb_data['role']}药"
                ))
            
            # 检查配伍
            herb_names = [h["herb"] for h in formula_info.get("composition", [])]
            compatibility = self.kb.check_herb_compatibility(herb_names)
            
            prescription = PrescriptionRationale(
                formula_name=formula_name,
                formula_source=formula_info.get("source", "《伤寒论》"),
                formula_analysis=f"本方以{herbs[0].name if herbs else ''}为君药，{', '.join(formula_info.get('functions', []))}",
                herbs=herbs,
                compatibility_analysis="配伍得当" if not compatibility["prohibited"] else "注意配伍禁忌"
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="类比",
                premise=f"治法为{treatment.primary_principle}，证型为{syndrome.primary_syndrome.value}",
                inference=f"《伤寒论》中{formula_name}为治疗{syndrome.primary_syndrome.value}之主方，功效{', '.join(formula_info.get('functions', []))}",
                conclusion=f"选方{formula_name}",
                classical_reference=formula_info.get("classical_clause"),
                confidence=best_formula["match_score"]
            )
        else:
            prescription = PrescriptionRationale(
                formula_name="待定",
                formula_source="",
                formula_analysis="需根据具体情况选方"
            )
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="推断",
                premise=f"治法为{treatment.primary_principle}",
                inference="需要更多信息以确定具体方剂",
                conclusion="方药待定",
                confidence=0.5
            )
        
        return step, prescription
    
    def _generate_expected_outcome(
        self,
        syndrome: SyndromeDifferentiation,
        treatment: TreatmentPrinciple
    ) -> str:
        """生成预期疗效"""
        outcome_map = {
            SyndromeType.TAIYANG: "服药后当汗出热退，恶寒解除",
            SyndromeType.YANGMING: "服药后当热退便通，诸症减轻",
            SyndromeType.SHAOYANG: "服药后寒热往来止，胸胁舒畅",
            SyndromeType.TAIYIN: "服药后腹痛止，食欲增加",
            SyndromeType.SHAOYIN: "服药后四肢转温，精神好转",
            SyndromeType.JUEYIN: "服药后寒热调和，饮食正常"
        }
        return outcome_map.get(syndrome.primary_syndrome, "症状逐步改善")


# 创建单例生成器
cot_generator = ChainOfThoughtGenerator()


def generate_chain_of_thought(
    pulse_grid_data: Dict[str, Any],
    symptoms: List[str],
    chief_complaint: str,
    patient_info: Optional[Dict] = None
) -> ChainOfThought:
    """
    便捷函数：生成思维链
    Convenience function to generate Chain-of-Thought
    """
    return cot_generator.generate_cot(
        pulse_grid_data=pulse_grid_data,
        symptoms=symptoms,
        chief_complaint=chief_complaint,
        patient_info=patient_info
    )
