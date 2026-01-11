"""
TCM Chain-of-Thought Schema Definition
中医思维链语料库数据结构定义

This module defines the core data structures for the TCM Chain-of-Thought corpus,
which structures the Traditional Chinese Medicine diagnostic reasoning process
into a traceable chain of thought.

Key Components:
1. Four Diagnostic Methods (四诊) - Inspection, Listening, Inquiry, Palpation
2. Syndrome Differentiation (辨证) - Pattern identification
3. Treatment Principles (治则) - Therapeutic approach
4. Prescription Rationale (方药) - Formula and herb selection reasoning
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import json


class DiagnosticMethod(Enum):
    """四诊方法 - Four Diagnostic Methods"""
    INSPECTION = "望诊"      # Visual inspection
    LISTENING = "闻诊"       # Listening and smelling
    INQUIRY = "问诊"         # Inquiry
    PALPATION = "切诊"       # Pulse diagnosis and palpation


class SyndromeType(Enum):
    """证型分类 - Syndrome Classification"""
    # 六经辨证 - Six Meridian Differentiation
    TAIYANG = "太阳病"
    YANGMING = "阳明病"
    SHAOYANG = "少阳病"
    TAIYIN = "太阴病"
    SHAOYIN = "少阴病"
    JUEYIN = "厥阴病"
    
    # 八纲辨证 - Eight Principle Differentiation
    YIN = "阴证"
    YANG = "阳证"
    EXTERIOR = "表证"
    INTERIOR = "里证"
    COLD = "寒证"
    HEAT = "热证"
    DEFICIENCY = "虚证"
    EXCESS = "实证"


class PulseQuality(Enum):
    """脉象特征 - Pulse Qualities"""
    FLOATING = "浮"
    SINKING = "沉"
    SLOW = "迟"
    RAPID = "数"
    DEFICIENT = "虚"
    EXCESSIVE = "实"
    SLIPPERY = "滑"
    ROUGH = "涩"
    WIRY = "弦"
    THIN = "细"
    SURGING = "洪"
    FAINT = "微"


@dataclass
class DiagnosticEvidence:
    """
    诊断依据 - Single piece of diagnostic evidence
    Represents one observation from the four diagnostic methods
    """
    method: DiagnosticMethod
    observation: str                    # 观察内容
    clinical_significance: str          # 临床意义
    confidence: float = 1.0             # 置信度 0-1
    source_reference: Optional[str] = None  # 经典出处


@dataclass
class PulseGridData:
    """
    脉象九宫格数据 - Pulse Grid Data
    Represents the 3x3 pulse diagnosis grid data
    """
    # 左手三部
    left_cun: Dict[str, Any] = field(default_factory=dict)   # 左寸-心
    left_guan: Dict[str, Any] = field(default_factory=dict)  # 左关-肝
    left_chi: Dict[str, Any] = field(default_factory=dict)   # 左尺-肾
    
    # 右手三部
    right_cun: Dict[str, Any] = field(default_factory=dict)  # 右寸-肺
    right_guan: Dict[str, Any] = field(default_factory=dict) # 右关-脾
    right_chi: Dict[str, Any] = field(default_factory=dict)  # 右尺-肾
    
    # 总体评价
    overall_assessment: str = ""
    pulse_features: List[PulseQuality] = field(default_factory=list)
    diagnostic_suggestion: str = ""


@dataclass
class ReasoningStep:
    """
    推理步骤 - Single reasoning step in the chain
    """
    step_number: int
    reasoning_type: str           # 推理类型: 归纳、演绎、类比
    premise: str                  # 前提
    inference: str                # 推理过程
    conclusion: str               # 结论
    classical_reference: Optional[str] = None  # 经典依据
    confidence: float = 1.0


@dataclass
class SyndromeDifferentiation:
    """
    辨证分型 - Syndrome Differentiation Result
    The core of TCM diagnosis - identifying the pattern
    """
    primary_syndrome: SyndromeType
    secondary_syndromes: List[SyndromeType] = field(default_factory=list)
    
    # 辨证依据
    evidence_summary: str = ""
    key_symptoms: List[str] = field(default_factory=list)
    key_signs: List[str] = field(default_factory=list)
    
    # 六经辨证特征
    six_meridian_analysis: Optional[str] = None
    
    # 病机分析
    pathomechanism: str = ""
    
    # 经典条文对应
    classical_clause: Optional[str] = None
    classical_source: Optional[str] = None


@dataclass  
class TreatmentPrinciple:
    """
    治则治法 - Treatment Principles
    """
    primary_principle: str          # 主治法
    secondary_principles: List[str] = field(default_factory=list)
    
    # 治则依据
    rationale: str = ""
    
    # 禁忌
    contraindications: List[str] = field(default_factory=list)
    
    # 经典依据
    classical_reference: Optional[str] = None


@dataclass
class HerbEntry:
    """
    单味药物 - Single Herb Entry
    """
    name: str                       # 药名
    dosage: str                     # 剂量
    role: str                       # 君臣佐使
    function: str                   # 功效
    rationale: str = ""             # 选药理由


@dataclass
class PrescriptionRationale:
    """
    方药分析 - Prescription and Herb Selection Rationale
    """
    formula_name: str               # 方名
    formula_source: str             # 方剂出处
    
    # 方解
    formula_analysis: str = ""
    
    # 药物组成
    herbs: List[HerbEntry] = field(default_factory=list)
    
    # 配伍分析
    compatibility_analysis: str = ""
    
    # 加减化裁
    modifications: List[str] = field(default_factory=list)
    modification_rationale: str = ""


@dataclass
class ChainOfThought:
    """
    中医思维链 - TCM Chain-of-Thought
    The complete reasoning chain from symptoms to treatment
    """
    # 元数据
    cot_id: str
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    
    # 患者基本信息（脱敏）
    patient_demographics: Dict[str, Any] = field(default_factory=dict)
    chief_complaint: str = ""
    
    # 四诊信息
    diagnostic_evidence: List[DiagnosticEvidence] = field(default_factory=list)
    pulse_grid: Optional[PulseGridData] = None
    
    # 推理链
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    
    # 辨证结果
    syndrome_differentiation: Optional[SyndromeDifferentiation] = None
    
    # 治则
    treatment_principle: Optional[TreatmentPrinciple] = None
    
    # 方药
    prescription: Optional[PrescriptionRationale] = None
    
    # 预期疗效
    expected_outcome: str = ""
    follow_up_plan: str = ""
    
    # 质量标注
    expert_validated: bool = False
    validation_score: Optional[float] = None
    validator_comments: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "cot_id": self.cot_id,
            "created_at": self.created_at.isoformat(),
            "version": self.version,
            "patient_demographics": self.patient_demographics,
            "chief_complaint": self.chief_complaint,
            "diagnostic_evidence": [
                {
                    "method": e.method.value,
                    "observation": e.observation,
                    "clinical_significance": e.clinical_significance,
                    "confidence": e.confidence,
                    "source_reference": e.source_reference
                } for e in self.diagnostic_evidence
            ],
            "pulse_grid": {
                "left_cun": self.pulse_grid.left_cun,
                "left_guan": self.pulse_grid.left_guan,
                "left_chi": self.pulse_grid.left_chi,
                "right_cun": self.pulse_grid.right_cun,
                "right_guan": self.pulse_grid.right_guan,
                "right_chi": self.pulse_grid.right_chi,
                "overall_assessment": self.pulse_grid.overall_assessment,
                "pulse_features": [p.value for p in self.pulse_grid.pulse_features],
                "diagnostic_suggestion": self.pulse_grid.diagnostic_suggestion
            } if self.pulse_grid else None,
            "reasoning_steps": [
                {
                    "step_number": s.step_number,
                    "reasoning_type": s.reasoning_type,
                    "premise": s.premise,
                    "inference": s.inference,
                    "conclusion": s.conclusion,
                    "classical_reference": s.classical_reference,
                    "confidence": s.confidence
                } for s in self.reasoning_steps
            ],
            "syndrome_differentiation": {
                "primary_syndrome": self.syndrome_differentiation.primary_syndrome.value,
                "secondary_syndromes": [s.value for s in self.syndrome_differentiation.secondary_syndromes],
                "evidence_summary": self.syndrome_differentiation.evidence_summary,
                "key_symptoms": self.syndrome_differentiation.key_symptoms,
                "key_signs": self.syndrome_differentiation.key_signs,
                "pathomechanism": self.syndrome_differentiation.pathomechanism,
                "classical_clause": self.syndrome_differentiation.classical_clause,
                "classical_source": self.syndrome_differentiation.classical_source
            } if self.syndrome_differentiation else None,
            "treatment_principle": {
                "primary_principle": self.treatment_principle.primary_principle,
                "secondary_principles": self.treatment_principle.secondary_principles,
                "rationale": self.treatment_principle.rationale,
                "contraindications": self.treatment_principle.contraindications,
                "classical_reference": self.treatment_principle.classical_reference
            } if self.treatment_principle else None,
            "prescription": {
                "formula_name": self.prescription.formula_name,
                "formula_source": self.prescription.formula_source,
                "formula_analysis": self.prescription.formula_analysis,
                "herbs": [
                    {
                        "name": h.name,
                        "dosage": h.dosage,
                        "role": h.role,
                        "function": h.function,
                        "rationale": h.rationale
                    } for h in self.prescription.herbs
                ],
                "compatibility_analysis": self.prescription.compatibility_analysis,
                "modifications": self.prescription.modifications,
                "modification_rationale": self.prescription.modification_rationale
            } if self.prescription else None,
            "expected_outcome": self.expected_outcome,
            "follow_up_plan": self.follow_up_plan,
            "expert_validated": self.expert_validated,
            "validation_score": self.validation_score,
            "validator_comments": self.validator_comments
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChainOfThought":
        """Create from dictionary"""
        # Implementation for deserialization
        cot = cls(cot_id=data["cot_id"])
        cot.version = data.get("version", "1.0")
        cot.chief_complaint = data.get("chief_complaint", "")
        # ... additional field population
        return cot


@dataclass
class CorpusMetadata:
    """
    语料库元数据 - Corpus Metadata
    Statistics and information about the entire corpus
    """
    corpus_name: str = "TCM-CoT-Corpus"
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # 统计信息
    total_entries: int = 0
    validated_entries: int = 0
    
    # 分布统计
    syndrome_distribution: Dict[str, int] = field(default_factory=dict)
    formula_distribution: Dict[str, int] = field(default_factory=dict)
    
    # 质量指标
    average_validation_score: float = 0.0
    expert_agreement_kappa: float = 0.0
    
    # 数据来源
    data_sources: List[str] = field(default_factory=list)
    classical_references: List[str] = field(default_factory=list)
