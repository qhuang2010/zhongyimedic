"""
Yuanqi Pulse Method Schema Definition
元气脉法数据结构定义

This module defines the core data structures for the Yuanqi Pulse Method (元气脉法),
a proprietary TCM diagnostic system not previously published in academic literature.

Key Components:
1. Yuanqi Theory (元气理论) - Core theoretical framework
2. Pulse Patterns (脉象模式) - Specific pulse recognition patterns
3. Diagnostic Rules (诊断规则) - Reasoning rules from pulse to syndrome
4. Treatment Protocols (治疗方案) - Treatment approach
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class YuanqiState(Enum):
    """元气状态分类 - Yuanqi State Classification"""
    ABUNDANT = "元气充盛"
    SLIGHTLY_DEFICIENT = "元气稍虚"
    DEFICIENT = "元气虚损"
    SEVERELY_DEFICIENT = "元气大虚"
    DEPLETED = "元气衰竭"
    FLOATING = "元气外浮"
    SINKING = "元气下陷"


class PulseLevel(Enum):
    """脉诊层次 - Pulse Palpation Level"""
    FU = "浮"      # Superficial
    ZHONG = "中"   # Middle
    CHEN = "沉"    # Deep


class PulseQualityYuanqi(Enum):
    """元气脉法脉象特征 - Yuanqi Pulse Qualities"""
    # 力度
    STRONG = "有力"
    MODERATE = "中等"
    WEAK = "弱"
    EMPTY = "空虚"
    ABSENT = "无"
    
    # 特殊描述
    ROOTED = "有根"
    ROOTLESS = "无根"
    FLOATING_UP = "上浮"
    
    # 常规脉象
    WIRY = "弦"
    SLIPPERY = "滑"
    THIN = "细"
    RAPID = "数"
    SLOW = "迟"


@dataclass
class YuanqiTheory:
    """
    元气理论条目
    Yuanqi Theory Entry
    """
    theory_id: str
    category: str                    # 理论类别
    title: str                       # 标题
    content: str                     # 内容
    
    # 关键概念
    key_concepts: List[Dict[str, str]] = field(default_factory=list)
    
    # 与传统理论关系
    relation_to_classical: Dict[str, str] = field(default_factory=dict)
    
    # 临床应用
    clinical_applications: List[str] = field(default_factory=list)
    
    # 来源
    source: Dict[str, str] = field(default_factory=dict)
    
    # 关联理论
    related_theories: List[str] = field(default_factory=list)


@dataclass
class PulsePositionData:
    """
    单个脉位数据
    Single Pulse Position Data
    """
    fu: str = ""      # 浮取
    zhong: str = ""   # 中取
    chen: str = ""    # 沉取
    
    def is_rootless(self) -> bool:
        """判断是否无根"""
        rootless_indicators = ["空", "虚", "无", "弱", "几无", "欲绝"]
        return any(ind in self.chen for ind in rootless_indicators)
    
    def get_strength_gradient(self) -> str:
        """获取浮中沉力度变化趋势"""
        # 简化判断逻辑
        if self.is_rootless():
            return "上实下虚"
        return "正常"


@dataclass 
class YuanqiPulseGrid:
    """
    元气脉法九宫格脉象
    Yuanqi Pulse Method Grid Data
    """
    # 左手
    left_cun: PulsePositionData = field(default_factory=PulsePositionData)
    left_guan: PulsePositionData = field(default_factory=PulsePositionData)
    left_chi: PulsePositionData = field(default_factory=PulsePositionData)
    
    # 右手
    right_cun: PulsePositionData = field(default_factory=PulsePositionData)
    right_guan: PulsePositionData = field(default_factory=PulsePositionData)
    right_chi: PulsePositionData = field(default_factory=PulsePositionData)
    
    # 总体描述
    overall_description: str = ""
    
    def assess_yuanqi_state(self) -> YuanqiState:
        """
        评估元气状态
        Assess overall Yuanqi state based on pulse grid
        """
        # 检查尺部沉取（元气根本）
        left_chi_rootless = self.left_chi.is_rootless()
        right_chi_rootless = self.right_chi.is_rootless()
        
        if left_chi_rootless and right_chi_rootless:
            return YuanqiState.SEVERELY_DEFICIENT
        elif left_chi_rootless or right_chi_rootless:
            return YuanqiState.DEFICIENT
        else:
            return YuanqiState.ABUNDANT
    
    def get_key_findings(self) -> List[str]:
        """获取关键发现"""
        findings = []
        
        if self.left_chi.is_rootless():
            findings.append("左尺沉取无根")
        if self.right_chi.is_rootless():
            findings.append("右尺沉取无根")
            
        return findings


@dataclass
class YuanqiPulsePattern:
    """
    元气脉法脉象模式
    Yuanqi Pulse Pattern
    """
    pattern_id: str
    pattern_name: str                # 脉象名称
    
    # 特征描述
    characteristics: Dict[str, Any] = field(default_factory=dict)
    key_features: List[str] = field(default_factory=list)
    
    # 诊断意义
    diagnostic_meaning: Dict[str, Any] = field(default_factory=dict)
    
    # 鉴别要点
    differentiation: List[Dict[str, str]] = field(default_factory=list)
    
    # 治疗方向
    treatment_direction: Dict[str, Any] = field(default_factory=dict)
    
    # 常见伴随症状
    associated_symptoms: List[str] = field(default_factory=list)
    
    # 来源
    source: Dict[str, str] = field(default_factory=dict)
    
    def matches(self, pulse_grid: YuanqiPulseGrid) -> float:
        """
        计算脉象与此模式的匹配度
        Calculate match score between pulse grid and this pattern
        """
        score = 0.0
        total_checks = len(self.key_features)
        
        if total_checks == 0:
            return 0.0
        
        findings = pulse_grid.get_key_findings()
        overall = pulse_grid.overall_description
        
        for feature in self.key_features:
            if feature in findings or feature in overall:
                score += 1.0
        
        return score / total_checks


@dataclass
class YuanqiDiagnosticRule:
    """
    元气脉法诊断规则
    Yuanqi Diagnostic Rule
    """
    rule_id: str
    rule_name: str
    
    # 触发条件
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # 推理链
    reasoning_chain: List[Dict[str, str]] = field(default_factory=list)
    
    # 结论
    syndrome_conclusion: str = ""
    pathomechanism: str = ""
    
    # 治疗建议
    treatment_principle: str = ""
    recommended_formulas: List[str] = field(default_factory=list)
    
    # 置信度
    confidence: float = 0.8


@dataclass
class YuanqiTreatmentProtocol:
    """
    元气脉法治疗方案
    Yuanqi Treatment Protocol
    """
    protocol_id: str
    protocol_name: str
    
    # 适应证
    indications: Dict[str, Any] = field(default_factory=dict)
    
    # 治则治法
    principles: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    
    # 常用方剂
    formulas: List[Dict[str, Any]] = field(default_factory=list)
    
    # 用药特点
    medication_features: List[str] = field(default_factory=list)
    
    # 禁忌
    contraindications: List[str] = field(default_factory=list)
    
    # 疗效观察
    outcome_indicators: List[str] = field(default_factory=list)


@dataclass
class YuanqiClinicalCase:
    """
    元气脉法临床病例
    Yuanqi Clinical Case
    """
    case_id: str
    record_date: str
    
    # 患者信息
    patient: Dict[str, Any] = field(default_factory=dict)
    
    # 主诉与病史
    chief_complaint: str = ""
    present_illness: str = ""
    
    # 脉象
    pulse_grid: Optional[YuanqiPulseGrid] = None
    
    # 其他四诊
    other_diagnosis: Dict[str, Any] = field(default_factory=dict)
    
    # 元气脉法诊断
    yuanqi_diagnosis: Dict[str, Any] = field(default_factory=dict)
    
    # 治疗
    treatment: Dict[str, Any] = field(default_factory=dict)
    
    # 疗效
    outcome: Dict[str, Any] = field(default_factory=dict)
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 质量标记
    is_validated: bool = False
    validation_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "case_id": self.case_id,
            "record_date": self.record_date,
            "patient": self.patient,
            "chief_complaint": self.chief_complaint,
            "present_illness": self.present_illness,
            "yuanqi_diagnosis": self.yuanqi_diagnosis,
            "treatment": self.treatment,
            "outcome": self.outcome,
            "is_validated": self.is_validated,
            "validation_score": self.validation_score
        }


@dataclass
class YuanqiCorpusMetadata:
    """
    元气脉法语料库元数据
    Yuanqi Corpus Metadata
    """
    corpus_name: str = "Yuanqi-Pulse-Method-Corpus"
    version: str = "1.0.0"
    description: str = "元气脉法诊疗知识库"
    
    # 统计
    theory_count: int = 0
    pulse_pattern_count: int = 0
    diagnostic_rule_count: int = 0
    treatment_protocol_count: int = 0
    clinical_case_count: int = 0
    validated_case_count: int = 0
    
    # 来源
    primary_source: str = "元气脉法授课资料"
    is_proprietary: bool = True
    
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
