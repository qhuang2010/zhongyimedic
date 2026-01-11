"""
Yuanqi Pulse Method Chain-of-Thought Generator
元气脉法思维链生成器

Generates structured reasoning chains following Yuanqi Pulse Method principles.
This is the core algorithm for explainable TCM AI diagnosis.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

from .yuanqi_pulse_schema import (
    YuanqiPulseGrid, PulsePositionData, YuanqiState,
    YuanqiClinicalCase
)
from .yuanqi_knowledge_base import yuanqi_knowledge_base
from .tcm_cot_schema import (
    ChainOfThought, DiagnosticEvidence, DiagnosticMethod,
    ReasoningStep, SyndromeDifferentiation, SyndromeType,
    TreatmentPrinciple, PrescriptionRationale, HerbEntry
)


class YuanqiCoTGenerator:
    """
    元气脉法思维链生成器
    Yuanqi Pulse Method Chain-of-Thought Generator
    
    Generates explainable diagnostic reasoning chains based on
    Yuanqi Pulse Method principles.
    """
    
    def __init__(self):
        self.kb = yuanqi_knowledge_base
        self.step_counter = 0
    
    def generate_cot(
        self,
        pulse_grid_data: Dict[str, Any],
        symptoms: List[str],
        chief_complaint: str,
        patient_info: Optional[Dict] = None
    ) -> ChainOfThought:
        """
        生成元气脉法思维链
        Generate Chain-of-Thought using Yuanqi method
        """
        self.step_counter = 0
        
        # 1. 创建CoT对象
        cot = ChainOfThought(
            cot_id=str(uuid.uuid4()),
            chief_complaint=chief_complaint,
            patient_demographics=patient_info or {}
        )
        
        # 2. 解析脉象为YuanqiPulseGrid
        yuanqi_grid = self._parse_to_yuanqi_grid(pulse_grid_data)
        
        # 3. 收集诊断依据
        cot.diagnostic_evidence = self._collect_evidence(
            pulse_grid_data, symptoms, yuanqi_grid
        )
        
        # 4. 生成推理链
        reasoning_steps = []
        
        # Step 1: 元气脉法脉诊分析
        step1 = self._generate_yuanqi_pulse_analysis(yuanqi_grid)
        reasoning_steps.append(step1)
        
        # 5. 评估元气状态
        yuanqi_assessment = self.kb.assess_yuanqi(yuanqi_grid)
        yuanqi_state = yuanqi_assessment["yuanqi_state"]
        matched_patterns = yuanqi_assessment["matched_patterns"]
        
        # Step 2: 元气状态判断
        step2 = self._generate_yuanqi_state_step(
            yuanqi_state, 
            yuanqi_assessment["key_findings"],
            matched_patterns
        )
        reasoning_steps.append(step2)
        
        # 6. 匹配诊断规则
        pattern_names = [p["pattern_name"] for p in matched_patterns]
        applicable_rules = self.kb.get_applicable_rules(pattern_names, symptoms)
        
        # Step 3: 辨证推理
        step3, syndrome = self._generate_syndrome_step(
            applicable_rules, yuanqi_state, symptoms
        )
        reasoning_steps.append(step3)
        cot.syndrome_differentiation = syndrome
        
        # 7. 确定治则
        step4, treatment = self._generate_treatment_step(
            yuanqi_state, syndrome, applicable_rules
        )
        reasoning_steps.append(step4)
        cot.treatment_principle = treatment
        
        # 8. 选方用药
        step5, prescription = self._generate_prescription_step(
            yuanqi_state, syndrome, treatment
        )
        reasoning_steps.append(step5)
        cot.prescription = prescription
        
        cot.reasoning_steps = reasoning_steps
        cot.expected_outcome = self._generate_outcome(yuanqi_state)
        
        return cot
    
    def _parse_to_yuanqi_grid(self, data: Dict[str, Any]) -> YuanqiPulseGrid:
        """解析为元气脉法脉象格式"""
        grid = YuanqiPulseGrid()
        
        if "positions" in data:
            positions = data["positions"]
            
            # 左手
            grid.left_cun = self._parse_position(positions.get("1", {}))
            grid.left_guan = self._parse_position(positions.get("2", {}))
            grid.left_chi = self._parse_position(positions.get("3", {}))
            
            # 右手
            grid.right_cun = self._parse_position(positions.get("4", {}))
            grid.right_guan = self._parse_position(positions.get("5", {}))
            grid.right_chi = self._parse_position(positions.get("6", {}))
            
            # 总体描述
            grid.overall_description = positions.get("7", {}).get("value", "")
        
        return grid
    
    def _parse_position(self, pos_data: Dict) -> PulsePositionData:
        """解析单个脉位"""
        levels = pos_data.get("levels", {})
        return PulsePositionData(
            fu=levels.get("fu", ""),
            zhong=levels.get("zhong", ""),
            chen=levels.get("chen", "")
        )
    
    def _collect_evidence(
        self,
        pulse_data: Dict,
        symptoms: List[str],
        yuanqi_grid: YuanqiPulseGrid
    ) -> List[DiagnosticEvidence]:
        """收集诊断依据"""
        evidence_list = []
        
        # 元气脉法特色：强调沉取层次
        key_findings = yuanqi_grid.get_key_findings()
        if key_findings:
            evidence_list.append(DiagnosticEvidence(
                method=DiagnosticMethod.PALPATION,
                observation=f"元气脉法脉诊：{'; '.join(key_findings)}",
                clinical_significance="元气根本状态评估",
                confidence=0.95,
                source_reference="元气脉法核心课程"
            ))
        
        # 总体脉象
        if yuanqi_grid.overall_description:
            evidence_list.append(DiagnosticEvidence(
                method=DiagnosticMethod.PALPATION,
                observation=f"脉象总评：{yuanqi_grid.overall_description}",
                clinical_significance="综合脉象特征",
                confidence=0.9
            ))
        
        # 症状
        for symptom in symptoms:
            evidence_list.append(DiagnosticEvidence(
                method=DiagnosticMethod.INQUIRY,
                observation=symptom,
                clinical_significance=self._get_symptom_yuanqi_meaning(symptom),
                confidence=0.85
            ))
        
        return evidence_list
    
    def _get_symptom_yuanqi_meaning(self, symptom: str) -> str:
        """获取症状的元气脉法意义"""
        meanings = {
            "腰膝酸软": "肾虚不固，元气亏虚",
            "畏寒肢冷": "阳虚失温，元气不能温煦四末",
            "精神萎靡": "元气不足，神失所养",
            "夜尿频多": "肾阳虚衰，固摄无权",
            "面红如妆": "虚阳上越，非实热",
            "下肢厥冷": "阳气不达，下元虚寒",
            "大便溏薄": "脾肾阳虚，运化失职"
        }
        return meanings.get(symptom, "待元气脉法辨析")
    
    def _generate_yuanqi_pulse_analysis(
        self, 
        yuanqi_grid: YuanqiPulseGrid
    ) -> ReasoningStep:
        """生成元气脉法脉诊分析步骤"""
        self.step_counter += 1
        
        findings = yuanqi_grid.get_key_findings()
        
        premise = f"元气脉法脉诊：浮中沉三层分析"
        
        if findings:
            inference = f"关键发现：{'; '.join(findings)}。" \
                       "元气脉法重在'察根'，通过沉取层次评估元气根本状态。"
        else:
            inference = "脉象浮中沉三层均衡，无明显无根表现。"
        
        conclusion = "完成元气脉法脉诊分析，进行元气状态判断"
        
        return ReasoningStep(
            step_number=self.step_counter,
            reasoning_type="归纳",
            premise=premise,
            inference=inference,
            conclusion=conclusion,
            classical_reference="元气脉法核心理论：察根为本",
            confidence=0.9
        )
    
    def _generate_yuanqi_state_step(
        self,
        state: YuanqiState,
        findings: List[str],
        matched_patterns: List[Dict]
    ) -> ReasoningStep:
        """生成元气状态判断步骤"""
        self.step_counter += 1
        
        premise = f"脉诊关键发现：{'; '.join(findings) if findings else '无明显异常'}"
        
        if matched_patterns:
            top_pattern = matched_patterns[0]
            inference = f"符合元气脉法'{top_pattern['pattern_name']}'脉象特征，" \
                       f"元气状态判断为：{state.value}"
        else:
            inference = f"元气状态判断为：{state.value}"
        
        conclusion = f"元气状态：{state.value}"
        
        return ReasoningStep(
            step_number=self.step_counter,
            reasoning_type="演绎",
            premise=premise,
            inference=inference,
            conclusion=conclusion,
            classical_reference="元气脉法脉象模式识别",
            confidence=0.85
        )
    
    def _generate_syndrome_step(
        self,
        rules: List,
        state: YuanqiState,
        symptoms: List[str]
    ) -> tuple:
        """生成辨证推理步骤"""
        self.step_counter += 1
        
        if rules:
            rule = rules[0]
            
            # 构建推理链描述
            reasoning_desc = ""
            for step in rule.reasoning_chain:
                reasoning_desc += f"{step['premise']} → {step['conclusion']}; "
            
            syndrome = SyndromeDifferentiation(
                primary_syndrome=self._map_to_syndrome_type(rule.syndrome_conclusion),
                evidence_summary=rule.pathomechanism,
                key_symptoms=symptoms[:3],
                key_signs=["脉象无根" if state in [YuanqiState.DEFICIENT, YuanqiState.SEVERELY_DEFICIENT] else "脉象有根"],
                pathomechanism=rule.pathomechanism
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="演绎",
                premise=f"元气状态：{state.value}；症状：{', '.join(symptoms[:3])}",
                inference=reasoning_desc,
                conclusion=rule.syndrome_conclusion,
                classical_reference="元气脉法诊断规则",
                confidence=rule.confidence
            )
        else:
            syndrome = SyndromeDifferentiation(
                primary_syndrome=SyndromeType.DEFICIENCY,
                evidence_summary="根据元气脉法理论辨证",
                key_symptoms=symptoms
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="推断",
                premise=f"元气状态：{state.value}",
                inference="需进一步结合症状辨证",
                conclusion="证型待定",
                confidence=0.5
            )
        
        return step, syndrome
    
    def _map_to_syndrome_type(self, syndrome_name: str) -> SyndromeType:
        """映射证型名称到枚举"""
        if "肾阳虚" in syndrome_name or "元气虚" in syndrome_name:
            return SyndromeType.SHAOYIN
        elif "戴阳" in syndrome_name or "格阳" in syndrome_name:
            return SyndromeType.SHAOYIN
        else:
            return SyndromeType.DEFICIENCY
    
    def _generate_treatment_step(
        self,
        state: YuanqiState,
        syndrome: SyndromeDifferentiation,
        rules: List
    ) -> tuple:
        """生成治则推理步骤"""
        self.step_counter += 1
        
        # 获取治疗方案
        protocol = self.kb.get_treatment_protocol(
            state, 
            syndrome.evidence_summary if syndrome else ""
        )
        
        if protocol:
            treatment = TreatmentPrinciple(
                primary_principle=protocol.principles[0] if protocol.principles else "培补元气",
                secondary_principles=protocol.methods,
                rationale=f"根据元气脉法'{protocol.protocol_name}'治疗方案",
                contraindications=protocol.contraindications
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="演绎",
                premise=f"元气状态：{state.value}",
                inference=f"适用元气脉法'{protocol.protocol_name}'",
                conclusion=f"治法：{', '.join(protocol.principles)}",
                classical_reference="元气脉法治疗方案",
                confidence=0.9
            )
        elif rules:
            rule = rules[0]
            treatment = TreatmentPrinciple(
                primary_principle=rule.treatment_principle,
                rationale="根据元气脉法诊断规则"
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="演绎",
                premise=f"辨证：{rule.syndrome_conclusion}",
                inference=f"依据元气脉法治则",
                conclusion=f"治法：{rule.treatment_principle}",
                confidence=0.85
            )
        else:
            treatment = TreatmentPrinciple(
                primary_principle="培补元气",
                rationale="元气脉法基本原则"
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="推断",
                premise=f"元气状态：{state.value}",
                conclusion="治法：培补元气",
                inference="依据元气脉法基本原则",
                confidence=0.7
            )
        
        return step, treatment
    
    def _generate_prescription_step(
        self,
        state: YuanqiState,
        syndrome: SyndromeDifferentiation,
        treatment: TreatmentPrinciple
    ) -> tuple:
        """生成方药推理步骤 - 增强版，包含元气脉法用药选择逻辑"""
        self.step_counter += 1
        
        # 获取治疗方案
        protocol = self.kb.get_treatment_protocol(state, "")
        
        # 元气脉法核心用药规则：根据脉空程度选择主药
        medication_rules = self._get_medication_selection_rules(state)
        
        if protocol and protocol.formulas:
            formula_info = protocol.formulas[0]
            
            herbs = []
            if "composition" in formula_info:
                for herb_data in formula_info["composition"]:
                    herbs.append(HerbEntry(
                        name=herb_data["herb"],
                        dosage=herb_data["dosage"],
                        role="君" if herb_data["herb"] in ["附子", "制附子"] else "臣佐",
                        function="温阳" if "附" in herb_data["herb"] or "姜" in herb_data["herb"] else "配伍",
                        rationale=herb_data.get("note", "")
                    ))
            
            # 构建详细的用药分析
            herb_analysis = self._build_herb_analysis(medication_rules, herbs)
            
            prescription = PrescriptionRationale(
                formula_name=formula_info["name"],
                formula_source="元气脉法常用方",
                formula_analysis=f"元气脉法治疗{state.value}之主方",
                herbs=herbs,
                compatibility_analysis=herb_analysis
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="类比",
                premise=f"治法：{treatment.primary_principle}",
                inference=f"元气脉法常用{formula_info['name']}治疗此类证型。\n{medication_rules['reasoning']}",
                conclusion=f"选方：{formula_info['name']}\n用药要点：{medication_rules['key_points']}",
                classical_reference="元气脉法用药原则",
                confidence=0.9
            )
        else:
            # 使用元气脉法默认用药逻辑
            herbs = self._generate_default_herbs(state)
            herb_analysis = self._build_herb_analysis(medication_rules, herbs)
            
            prescription = PrescriptionRationale(
                formula_name="元气脉法基础方",
                formula_source="元气脉法临床经验",
                formula_analysis=f"根据脉空程度选药：{medication_rules['main_herb']}",
                herbs=herbs,
                compatibility_analysis=herb_analysis
            )
            
            step = ReasoningStep(
                step_number=self.step_counter,
                reasoning_type="推断",
                premise=f"治法：{treatment.primary_principle}",
                inference=medication_rules['reasoning'],
                conclusion=f"选方：元气脉法基础方\n{medication_rules['key_points']}",
                classical_reference="元气脉法用药原则",
                confidence=0.85
            )
        
        return step, prescription
    
    def _get_medication_selection_rules(self, state: YuanqiState) -> Dict[str, str]:
        """
        获取元气脉法用药选择规则
        核心原则：根据脉空程度（分数）选择不同的补阴/温阳药物
        """
        rules = {
            YuanqiState.ABUNDANT: {
                "main_herb": "无需用药",
                "reasoning": "脉象有根，元气充盛，调养即可",
                "key_points": "以调养为主，无需药物干预",
                "pulse_score": "0分"
            },
            YuanqiState.SLIGHTLY_DEFICIENT: {
                "main_herb": "山药1-1.5g",
                "reasoning": "脉空约2-3分时，山药养中补阴。山药性平，适合轻度元气虚损。",
                "key_points": "脉空约3分用山药；佩兰引气至表；白芍敛阴固表",
                "pulse_score": "2-3分"
            },
            YuanqiState.DEFICIENT: {
                "main_herb": "党参1.5g或山药1.5g",
                "reasoning": "脉空4-5分时，党参补阴力量更强。党参补中益气，兼能生津。",
                "key_points": "脉空4-5分党参补阴；佩兰引阴化表；甘草缓释温阳；白芍固表",
                "pulse_score": "4-5分"
            },
            YuanqiState.SEVERELY_DEFICIENT: {
                "main_herb": "麦冬1.5g",
                "reasoning": "脉空>5分时，麦冬养阴力量最强。麦冬滋阴润肺，清心除烦。",
                "key_points": "脉空>5分用麦冬养阴；佩兰化部分新生之阴并引气于表以固卫；炙甘草护中缓势",
                "pulse_score": ">5分"
            },
            YuanqiState.FLOATING: {
                "main_herb": "附片1g + 仙灵脾1g",
                "reasoning": "虚阳外越时，需温阳潜镇。附片温肾阳，仙灵脾温肾壮阳。",
                "key_points": "附片温阳；仙灵脾温肾阳；白芍敛阴；需引火归元",
                "pulse_score": "虚浮"
            }
        }
        
        return rules.get(state, {
            "main_herb": "山药1.5g",
            "reasoning": "元气脉法基础用药",
            "key_points": "健脾运中、扶卫引气",
            "pulse_score": "待定"
        })
    
    def _generate_default_herbs(self, state: YuanqiState) -> List[HerbEntry]:
        """生成元气脉法默认处方"""
        base_herbs = [
            HerbEntry(name="炙甘草", dosage="1g", role="使", function="护中缓势", 
                     rationale="调和诸药，保护中焦"),
            HerbEntry(name="佩兰", dosage="2.5g", role="臣", function="引气至表", 
                     rationale="化部分新生之阴并引气于表以固卫"),
            HerbEntry(name="白芍", dosage="1g", role="臣", function="敛阴固表", 
                     rationale="收敛佩兰之阳以护卫表之门")
        ]
        
        # 根据元气状态选择主药
        if state == YuanqiState.SEVERELY_DEFICIENT:
            base_herbs.insert(0, HerbEntry(
                name="麦冬", dosage="1.5g", role="君", function="养阴",
                rationale="脉空>5分用麦冬养阴"
            ))
        elif state == YuanqiState.DEFICIENT:
            base_herbs.insert(0, HerbEntry(
                name="党参", dosage="1.5g", role="君", function="补阴益气",
                rationale="脉空4-5分党参补阴"
            ))
        elif state == YuanqiState.FLOATING:
            base_herbs.insert(0, HerbEntry(
                name="附片", dosage="1g", role="君", function="温阳",
                rationale="虚阳外越，附片温阳潜镇"
            ))
            base_herbs.insert(1, HerbEntry(
                name="仙灵脾", dosage="1g", role="臣", function="温肾阳",
                rationale="温肾阳以引火归元"
            ))
        else:
            base_herbs.insert(0, HerbEntry(
                name="山药", dosage="1.5g", role="君", function="养中补阴",
                rationale="脉空约3分用山药养中"
            ))
        
        return base_herbs
    
    def _build_herb_analysis(self, rules: Dict, herbs: List[HerbEntry]) -> str:
        """构建用药分析说明"""
        analysis_parts = [
            f"【元气脉法用药原则】",
            f"- 脉空程度：{rules.get('pulse_score', '待定')}",
            f"- 主药选择：{rules.get('main_herb', '山药')}",
            f"- 选药理由：{rules.get('reasoning', '')}",
            f"",
            f"【具体用药】"
        ]
        
        for herb in herbs:
            if herb.rationale:
                analysis_parts.append(f"- {herb.name} {herb.dosage}：{herb.rationale}")
            else:
                analysis_parts.append(f"- {herb.name} {herb.dosage}：{herb.function}")
        
        analysis_parts.extend([
            "",
            f"【用法】每日800ml水，泡半小时，煎半小时，小口多次服用"
        ])
        
        return "\n".join(analysis_parts)
    
    def _generate_outcome(self, state: YuanqiState) -> str:
        """生成预期疗效"""
        outcomes = {
            YuanqiState.DEFICIENT: "服药后两尺沉取应渐有力，精神好转，畏寒减轻",
            YuanqiState.SEVERELY_DEFICIENT: "服药后四肢渐温，脉象有根，精神好转",
            YuanqiState.FLOATING: "服药后虚阳渐潜，面红减退，下肢转温",
            YuanqiState.ABUNDANT: "调养为主，保持元气充盛"
        }
        return outcomes.get(state, "辨证施治，随证加减")


# 创建单例生成器
yuanqi_cot_generator = YuanqiCoTGenerator()


def generate_yuanqi_chain_of_thought(
    pulse_grid_data: Dict[str, Any],
    symptoms: List[str],
    chief_complaint: str,
    patient_info: Optional[Dict] = None
) -> ChainOfThought:
    """
    便捷函数：生成元气脉法思维链
    Convenience function to generate Yuanqi method Chain-of-Thought
    """
    return yuanqi_cot_generator.generate_cot(
        pulse_grid_data=pulse_grid_data,
        symptoms=symptoms,
        chief_complaint=chief_complaint,
        patient_info=patient_info
    )
