"""
TCM Clinical Validation Framework
中医临床验证框架

This module implements the validation framework for clinical studies,
following CONSORT/STROBE guidelines for medical research.

Components:
1. Retrospective Case Validation (回顾性病例验证)
2. Prospective Study Design (前瞻性研究设计)
3. Blinded Evaluation Process (盲法评估流程)
4. Expert Panel Review (专家组评审)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import json
import uuid
import random

from .metrics import (
    EvaluationResult, MetricsReport, MetricsCalculator,
    calculate_cohens_kappa, calculate_clinical_acceptability
)


class StudyPhase(Enum):
    """研究阶段"""
    DESIGN = "设计阶段"
    ENROLLMENT = "入组阶段"
    EVALUATION = "评估阶段"
    ANALYSIS = "分析阶段"
    COMPLETED = "已完成"


class BlindingLevel(Enum):
    """盲法级别"""
    OPEN = "开放标签"
    SINGLE_BLIND = "单盲"
    DOUBLE_BLIND = "双盲"


@dataclass
class StudyCase:
    """
    研究病例
    Study Case
    """
    case_id: str
    patient_id: str  # 脱敏ID
    
    # 临床数据
    chief_complaint: str = ""
    symptoms: List[str] = field(default_factory=list)
    pulse_data: Dict[str, Any] = field(default_factory=dict)
    
    # AI诊断结果
    ai_syndrome: str = ""
    ai_formula: str = ""
    ai_reasoning_chain: Dict[str, Any] = field(default_factory=dict)
    
    # 专家诊断（金标准）
    expert_syndrome: str = ""
    expert_formula: str = ""
    expert_rationale: str = ""
    
    # 评估结果
    evaluation_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    is_evaluated: bool = False


@dataclass
class ExpertEvaluator:
    """
    专家评审者
    Expert Evaluator
    """
    evaluator_id: str
    name: str
    title: str                    # 职称
    institution: str              # 机构
    years_of_experience: int      # 从业年限
    specialty: str = "中医内科"    # 专业方向
    is_blinded: bool = True       # 是否盲法


@dataclass
class EvaluationTask:
    """
    评估任务
    Evaluation Task
    """
    task_id: str
    case: StudyCase
    evaluator: ExpertEvaluator
    
    # 评估内容
    show_ai_result: bool = False  # 是否展示AI结果（用于对照）
    
    # 评估结果
    syndrome_assessment: str = ""
    formula_assessment: str = ""
    acceptability_score: int = 0
    reasoning_quality_score: int = 0
    classical_reference_score: int = 0
    comments: str = ""
    
    # 状态
    is_completed: bool = False
    completed_at: Optional[datetime] = None


@dataclass
class ValidationStudy:
    """
    验证研究
    Validation Study
    """
    study_id: str
    study_name: str
    study_type: str                  # 回顾性/前瞻性
    
    # 研究设计
    blinding_level: BlindingLevel = BlindingLevel.SINGLE_BLIND
    target_sample_size: int = 100
    
    # 入排标准
    inclusion_criteria: List[str] = field(default_factory=list)
    exclusion_criteria: List[str] = field(default_factory=list)
    
    # 参与者
    cases: List[StudyCase] = field(default_factory=list)
    evaluators: List[ExpertEvaluator] = field(default_factory=list)
    
    # 评估任务
    evaluation_tasks: List[EvaluationTask] = field(default_factory=list)
    
    # 状态
    phase: StudyPhase = StudyPhase.DESIGN
    created_at: datetime = field(default_factory=datetime.now)
    
    # 结果
    metrics_report: Optional[MetricsReport] = None


class ValidationFramework:
    """
    临床验证框架
    Clinical Validation Framework
    
    Manages the entire validation study lifecycle
    """
    
    def __init__(self):
        self.studies: Dict[str, ValidationStudy] = {}
        self.metrics_calculator = MetricsCalculator()
    
    def create_retrospective_study(
        self,
        study_name: str,
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
        target_sample_size: int = 100
    ) -> ValidationStudy:
        """
        创建回顾性验证研究
        Create retrospective validation study
        """
        study = ValidationStudy(
            study_id=str(uuid.uuid4()),
            study_name=study_name,
            study_type="回顾性研究",
            blinding_level=BlindingLevel.SINGLE_BLIND,
            target_sample_size=target_sample_size,
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria
        )
        
        self.studies[study.study_id] = study
        return study
    
    def create_prospective_study(
        self,
        study_name: str,
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
        target_sample_size: int = 200,
        blinding_level: BlindingLevel = BlindingLevel.DOUBLE_BLIND
    ) -> ValidationStudy:
        """
        创建前瞻性验证研究
        Create prospective validation study
        """
        study = ValidationStudy(
            study_id=str(uuid.uuid4()),
            study_name=study_name,
            study_type="前瞻性研究",
            blinding_level=blinding_level,
            target_sample_size=target_sample_size,
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria
        )
        
        self.studies[study.study_id] = study
        return study
    
    def add_case(
        self,
        study_id: str,
        patient_id: str,
        chief_complaint: str,
        symptoms: List[str],
        pulse_data: Dict[str, Any],
        expert_syndrome: str,
        expert_formula: str,
        ai_syndrome: str = "",
        ai_formula: str = "",
        ai_reasoning_chain: Dict[str, Any] = None
    ) -> StudyCase:
        """
        添加研究病例
        Add study case
        """
        study = self.studies.get(study_id)
        if not study:
            raise ValueError(f"Study {study_id} not found")
        
        case = StudyCase(
            case_id=str(uuid.uuid4()),
            patient_id=patient_id,
            chief_complaint=chief_complaint,
            symptoms=symptoms,
            pulse_data=pulse_data,
            expert_syndrome=expert_syndrome,
            expert_formula=expert_formula,
            ai_syndrome=ai_syndrome,
            ai_formula=ai_formula,
            ai_reasoning_chain=ai_reasoning_chain or {}
        )
        
        study.cases.append(case)
        return case
    
    def add_evaluator(
        self,
        study_id: str,
        name: str,
        title: str,
        institution: str,
        years_of_experience: int,
        specialty: str = "中医内科"
    ) -> ExpertEvaluator:
        """
        添加专家评审者
        Add expert evaluator
        """
        study = self.studies.get(study_id)
        if not study:
            raise ValueError(f"Study {study_id} not found")
        
        evaluator = ExpertEvaluator(
            evaluator_id=str(uuid.uuid4()),
            name=name,
            title=title,
            institution=institution,
            years_of_experience=years_of_experience,
            specialty=specialty,
            is_blinded=study.blinding_level != BlindingLevel.OPEN
        )
        
        study.evaluators.append(evaluator)
        return evaluator
    
    def generate_evaluation_tasks(
        self,
        study_id: str,
        cases_per_evaluator: int = 30,
        evaluators_per_case: int = 2
    ) -> List[EvaluationTask]:
        """
        生成评估任务分配
        Generate evaluation task assignments
        
        确保每个病例由指定数量的专家评估，
        且任务分配随机化以减少偏倚
        """
        study = self.studies.get(study_id)
        if not study:
            raise ValueError(f"Study {study_id} not found")
        
        tasks = []
        
        for case in study.cases:
            # 随机选择评估者
            selected_evaluators = random.sample(
                study.evaluators,
                min(evaluators_per_case, len(study.evaluators))
            )
            
            for evaluator in selected_evaluators:
                task = EvaluationTask(
                    task_id=str(uuid.uuid4()),
                    case=case,
                    evaluator=evaluator,
                    show_ai_result=study.blinding_level == BlindingLevel.OPEN
                )
                tasks.append(task)
        
        study.evaluation_tasks = tasks
        study.phase = StudyPhase.EVALUATION
        
        return tasks
    
    def submit_evaluation(
        self,
        study_id: str,
        task_id: str,
        syndrome_assessment: str,
        formula_assessment: str,
        acceptability_score: int,
        reasoning_quality_score: int,
        classical_reference_score: int,
        comments: str = ""
    ) -> EvaluationTask:
        """
        提交评估结果
        Submit evaluation result
        """
        study = self.studies.get(study_id)
        if not study:
            raise ValueError(f"Study {study_id} not found")
        
        task = next(
            (t for t in study.evaluation_tasks if t.task_id == task_id),
            None
        )
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.syndrome_assessment = syndrome_assessment
        task.formula_assessment = formula_assessment
        task.acceptability_score = acceptability_score
        task.reasoning_quality_score = reasoning_quality_score
        task.classical_reference_score = classical_reference_score
        task.comments = comments
        task.is_completed = True
        task.completed_at = datetime.now()
        
        return task
    
    def calculate_study_metrics(self, study_id: str) -> MetricsReport:
        """
        计算研究指标
        Calculate study metrics
        """
        study = self.studies.get(study_id)
        if not study:
            raise ValueError(f"Study {study_id} not found")
        
        self.metrics_calculator.clear()
        
        # 将评估任务转换为评估结果
        for task in study.evaluation_tasks:
            if task.is_completed:
                result = EvaluationResult(
                    case_id=task.case.case_id,
                    predicted_syndrome=task.case.ai_syndrome,
                    actual_syndrome=task.case.expert_syndrome,
                    predicted_formula=task.case.ai_formula,
                    actual_formula=task.case.expert_formula,
                    acceptability_score=task.acceptability_score,
                    expert_comments=task.comments,
                    reasoning_quality_score=task.reasoning_quality_score / 5.0,
                    classical_reference_accuracy=task.classical_reference_score / 5.0
                )
                self.metrics_calculator.add_result(result)
        
        report = self.metrics_calculator.calculate_report()
        study.metrics_report = report
        study.phase = StudyPhase.ANALYSIS
        
        return report
    
    def calculate_inter_rater_agreement(self, study_id: str) -> Dict[str, float]:
        """
        计算评估者间一致性
        Calculate inter-rater agreement
        """
        study = self.studies.get(study_id)
        if not study:
            raise ValueError(f"Study {study_id} not found")
        
        # 按病例分组评估结果
        case_evaluations: Dict[str, List[EvaluationTask]] = {}
        for task in study.evaluation_tasks:
            if task.is_completed:
                case_id = task.case.case_id
                if case_id not in case_evaluations:
                    case_evaluations[case_id] = []
                case_evaluations[case_id].append(task)
        
        # 提取配对评估
        rater1_syndromes = []
        rater2_syndromes = []
        rater1_formulas = []
        rater2_formulas = []
        
        for case_id, evals in case_evaluations.items():
            if len(evals) >= 2:
                rater1_syndromes.append(evals[0].syndrome_assessment)
                rater2_syndromes.append(evals[1].syndrome_assessment)
                rater1_formulas.append(evals[0].formula_assessment)
                rater2_formulas.append(evals[1].formula_assessment)
        
        syndrome_kappa = calculate_cohens_kappa(rater1_syndromes, rater2_syndromes)
        formula_kappa = calculate_cohens_kappa(rater1_formulas, rater2_formulas)
        
        return {
            "syndrome_inter_rater_kappa": syndrome_kappa,
            "formula_inter_rater_kappa": formula_kappa,
            "paired_cases": len(rater1_syndromes)
        }
    
    def export_study_report(
        self,
        study_id: str,
        format: str = "json"
    ) -> str:
        """
        导出研究报告
        Export study report
        """
        study = self.studies.get(study_id)
        if not study:
            raise ValueError(f"Study {study_id} not found")
        
        report_data = {
            "study_info": {
                "study_id": study.study_id,
                "study_name": study.study_name,
                "study_type": study.study_type,
                "blinding_level": study.blinding_level.value,
                "phase": study.phase.value
            },
            "sample_info": {
                "target_sample_size": study.target_sample_size,
                "enrolled_cases": len(study.cases),
                "evaluated_cases": sum(1 for t in study.evaluation_tasks if t.is_completed),
                "evaluators": len(study.evaluators)
            },
            "inclusion_criteria": study.inclusion_criteria,
            "exclusion_criteria": study.exclusion_criteria,
            "metrics": study.metrics_report.to_dict() if study.metrics_report else None
        }
        
        if format == "json":
            return json.dumps(report_data, ensure_ascii=False, indent=2)
        else:
            # 文本格式
            lines = []
            lines.append(f"研究报告: {study.study_name}")
            lines.append("=" * 50)
            lines.append(f"研究类型: {study.study_type}")
            lines.append(f"盲法级别: {study.blinding_level.value}")
            lines.append(f"样本量: {len(study.cases)}/{study.target_sample_size}")
            lines.append("")
            
            if study.metrics_report:
                lines.append("主要结果:")
                lines.append(f"  辨证准确率: {study.metrics_report.syndrome_accuracy:.1%}")
                lines.append(f"  方剂准确率: {study.metrics_report.formula_accuracy:.1%}")
                lines.append(f"  Cohen's Kappa: {study.metrics_report.syndrome_kappa:.3f}")
                lines.append(f"  临床可接受度: {study.metrics_report.mean_acceptability:.2f}/5")
            
            return "\n".join(lines)


# 预定义研究模板
STUDY_TEMPLATES = {
    "retrospective_pulse_validation": {
        "name": "中医脉象智能诊断系统回顾性验证研究",
        "type": "回顾性研究",
        "inclusion_criteria": [
            "年龄18-80岁",
            "有完整的脉象九宫格记录",
            "有明确的中医辨证诊断",
            "诊断医生为副主任医师及以上职称"
        ],
        "exclusion_criteria": [
            "病历资料不完整者",
            "脉象图像质量不合格者",
            "存在多系统复杂疾病者"
        ],
        "target_sample_size": 150
    },
    "prospective_clinical_trial": {
        "name": "中医智能辅助诊断系统前瞻性临床验证",
        "type": "前瞻性研究",
        "inclusion_criteria": [
            "年龄18-70岁",
            "初诊内科患者",
            "知情同意参与研究"
        ],
        "exclusion_criteria": [
            "危急重症患者",
            "精神疾病患者",
            "拒绝参与研究者"
        ],
        "target_sample_size": 300
    }
}


# 创建单例框架
validation_framework = ValidationFramework()
