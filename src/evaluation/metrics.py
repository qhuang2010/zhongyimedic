"""
TCM Clinical Evaluation Metrics
中医临床评估指标

This module implements evaluation metrics for TCM diagnostic systems,
following medical informatics best practices for JAMIA/BMC publication.

Metrics Include:
1. Diagnostic Accuracy (诊断准确率)
2. Syndrome Consistency (辨证一致性) - Cohen's Kappa
3. Clinical Acceptability (临床可接受度)
4. Expert Agreement (专家一致性)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import numpy as np
from collections import Counter
import json


class AcceptabilityLevel(Enum):
    """临床可接受度等级"""
    COMPLETELY_ACCEPTABLE = 5      # 完全可接受
    MOSTLY_ACCEPTABLE = 4          # 大部分可接受
    PARTIALLY_ACCEPTABLE = 3       # 部分可接受
    MOSTLY_UNACCEPTABLE = 2        # 大部分不可接受
    COMPLETELY_UNACCEPTABLE = 1    # 完全不可接受


@dataclass
class EvaluationResult:
    """
    单次评估结果
    Single Evaluation Result
    """
    case_id: str
    predicted_syndrome: str
    actual_syndrome: str
    predicted_formula: str
    actual_formula: str
    acceptability_score: int
    expert_comments: str = ""
    reasoning_quality_score: float = 0.0
    classical_reference_accuracy: float = 0.0


@dataclass
class MetricsReport:
    """
    综合评估报告
    Comprehensive Metrics Report
    """
    # 样本信息
    total_cases: int = 0
    evaluated_cases: int = 0
    
    # 诊断准确率
    syndrome_accuracy: float = 0.0
    formula_accuracy: float = 0.0
    
    # 一致性指标
    syndrome_kappa: float = 0.0
    formula_kappa: float = 0.0
    
    # 临床可接受度
    mean_acceptability: float = 0.0
    acceptability_distribution: Dict[int, int] = field(default_factory=dict)
    
    # 推理质量
    mean_reasoning_quality: float = 0.0
    
    # 经典引用准确率
    mean_reference_accuracy: float = 0.0
    
    # 置信区间
    syndrome_accuracy_ci: Tuple[float, float] = (0.0, 0.0)
    acceptability_ci: Tuple[float, float] = (0.0, 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_info": {
                "total_cases": self.total_cases,
                "evaluated_cases": self.evaluated_cases
            },
            "diagnostic_accuracy": {
                "syndrome_accuracy": round(self.syndrome_accuracy, 4),
                "formula_accuracy": round(self.formula_accuracy, 4)
            },
            "consistency_metrics": {
                "syndrome_kappa": round(self.syndrome_kappa, 4),
                "formula_kappa": round(self.formula_kappa, 4)
            },
            "clinical_acceptability": {
                "mean_score": round(self.mean_acceptability, 2),
                "distribution": self.acceptability_distribution
            },
            "reasoning_quality": {
                "mean_score": round(self.mean_reasoning_quality, 4)
            },
            "classical_reference_accuracy": round(self.mean_reference_accuracy, 4),
            "confidence_intervals": {
                "syndrome_accuracy_95ci": [round(x, 4) for x in self.syndrome_accuracy_ci],
                "acceptability_95ci": [round(x, 4) for x in self.acceptability_ci]
            }
        }


def calculate_accuracy(predictions: List[str], ground_truth: List[str]) -> float:
    """
    计算准确率
    Calculate accuracy
    
    Args:
        predictions: 预测结果列表
        ground_truth: 真实标签列表
        
    Returns:
        accuracy: 准确率 (0-1)
    """
    if len(predictions) != len(ground_truth):
        raise ValueError("Predictions and ground truth must have same length")
    
    if len(predictions) == 0:
        return 0.0
    
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    return correct / len(predictions)


def calculate_cohens_kappa(
    rater1: List[str],
    rater2: List[str],
    categories: Optional[List[str]] = None
) -> float:
    """
    计算Cohen's Kappa系数
    Calculate Cohen's Kappa coefficient
    
    用于评估两个评价者之间的一致性，考虑机会一致性
    Used to assess inter-rater agreement, accounting for chance agreement
    
    Args:
        rater1: 评价者1的标签列表
        rater2: 评价者2的标签列表
        categories: 所有可能的类别（可选）
        
    Returns:
        kappa: Kappa系数 (-1 to 1)
              - 1.0: 完美一致
              - 0.81-1.00: 几乎完美
              - 0.61-0.80: 高度一致
              - 0.41-0.60: 中等一致
              - 0.21-0.40: 一般一致
              - 0.00-0.20: 轻微一致
              - < 0: 低于预期一致性
    """
    if len(rater1) != len(rater2):
        raise ValueError("Both raters must have the same number of ratings")
    
    n = len(rater1)
    if n == 0:
        return 0.0
    
    # 获取所有类别
    if categories is None:
        categories = list(set(rater1) | set(rater2))
    
    # 构建混淆矩阵
    cat_to_idx = {cat: i for i, cat in enumerate(categories)}
    k = len(categories)
    confusion_matrix = np.zeros((k, k))
    
    for r1, r2 in zip(rater1, rater2):
        if r1 in cat_to_idx and r2 in cat_to_idx:
            confusion_matrix[cat_to_idx[r1], cat_to_idx[r2]] += 1
    
    # 观察一致性 Po
    po = np.trace(confusion_matrix) / n
    
    # 预期一致性 Pe
    row_sums = confusion_matrix.sum(axis=1)
    col_sums = confusion_matrix.sum(axis=0)
    pe = np.sum(row_sums * col_sums) / (n * n)
    
    # Cohen's Kappa
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    
    kappa = (po - pe) / (1 - pe)
    return kappa


def calculate_fleiss_kappa(
    ratings_matrix: np.ndarray,
    n_categories: int
) -> float:
    """
    计算Fleiss' Kappa系数
    Calculate Fleiss' Kappa for multiple raters
    
    用于评估多个评价者之间的一致性
    For assessing agreement among multiple raters
    
    Args:
        ratings_matrix: (n_subjects x n_categories) 矩阵
                       每行表示每个类别的评价者数量
        n_categories: 类别数量
        
    Returns:
        kappa: Fleiss' Kappa系数
    """
    n_subjects = ratings_matrix.shape[0]
    n_raters = ratings_matrix.sum(axis=1)[0]  # 假设每个主题评价者数相同
    
    # 计算 P_j (每个类别的比例)
    p_j = ratings_matrix.sum(axis=0) / (n_subjects * n_raters)
    
    # 计算 P_i (每个主题的一致性)
    p_i = (np.sum(ratings_matrix ** 2, axis=1) - n_raters) / (n_raters * (n_raters - 1))
    
    # 平均观察一致性
    p_bar = np.mean(p_i)
    
    # 预期一致性
    p_e = np.sum(p_j ** 2)
    
    # Fleiss' Kappa
    if p_e == 1.0:
        return 1.0 if p_bar == 1.0 else 0.0
    
    kappa = (p_bar - p_e) / (1 - p_e)
    return kappa


def calculate_clinical_acceptability(
    acceptability_scores: List[int],
    threshold: int = 3
) -> Dict[str, Any]:
    """
    计算临床可接受度统计
    Calculate clinical acceptability statistics
    
    Args:
        acceptability_scores: 可接受度评分列表 (1-5)
        threshold: 可接受阈值，>=threshold视为可接受
        
    Returns:
        统计结果字典
    """
    if not acceptability_scores:
        return {
            "mean": 0.0,
            "std": 0.0,
            "acceptable_rate": 0.0,
            "distribution": {}
        }
    
    scores = np.array(acceptability_scores)
    
    # 分布统计
    distribution = Counter(acceptability_scores)
    
    # 可接受比例
    acceptable_count = sum(1 for s in acceptability_scores if s >= threshold)
    acceptable_rate = acceptable_count / len(acceptability_scores)
    
    return {
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
        "median": float(np.median(scores)),
        "acceptable_rate": acceptable_rate,
        "distribution": dict(distribution),
        "n": len(acceptability_scores)
    }


def calculate_confidence_interval(
    data: List[float],
    confidence: float = 0.95
) -> Tuple[float, float]:
    """
    计算置信区间
    Calculate confidence interval
    
    使用正态分布近似
    
    Args:
        data: 数据列表
        confidence: 置信水平 (默认0.95即95%)
        
    Returns:
        (lower, upper): 置信区间
    """
    if len(data) < 2:
        mean = np.mean(data) if data else 0.0
        return (mean, mean)
    
    data = np.array(data)
    n = len(data)
    mean = np.mean(data)
    std_err = np.std(data, ddof=1) / np.sqrt(n)
    
    # Z值 (95%置信度 = 1.96)
    z_values = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z = z_values.get(confidence, 1.96)
    
    margin = z * std_err
    return (mean - margin, mean + margin)


def calculate_sensitivity_specificity(
    predictions: List[bool],
    ground_truth: List[bool]
) -> Dict[str, float]:
    """
    计算敏感性和特异性
    Calculate sensitivity and specificity
    
    Args:
        predictions: 预测结果列表 (True/False)
        ground_truth: 真实标签列表 (True/False)
        
    Returns:
        包含各指标的字典
    """
    tp = sum(1 for p, g in zip(predictions, ground_truth) if p and g)
    tn = sum(1 for p, g in zip(predictions, ground_truth) if not p and not g)
    fp = sum(1 for p, g in zip(predictions, ground_truth) if p and not g)
    fn = sum(1 for p, g in zip(predictions, ground_truth) if not p and g)
    
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1 = 2 * precision * sensitivity / (precision + sensitivity) if (precision + sensitivity) > 0 else 0.0
    
    return {
        "sensitivity": sensitivity,  # 召回率
        "specificity": specificity,
        "precision": precision,      # 精确率
        "f1_score": f1,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn
    }


class MetricsCalculator:
    """
    综合评估指标计算器
    Comprehensive Metrics Calculator
    """
    
    def __init__(self):
        self.results: List[EvaluationResult] = []
    
    def add_result(self, result: EvaluationResult):
        """添加评估结果"""
        self.results.append(result)
    
    def add_results(self, results: List[EvaluationResult]):
        """批量添加评估结果"""
        self.results.extend(results)
    
    def clear(self):
        """清空结果"""
        self.results = []
    
    def calculate_report(self) -> MetricsReport:
        """
        生成综合评估报告
        Generate comprehensive metrics report
        """
        if not self.results:
            return MetricsReport()
        
        report = MetricsReport()
        report.total_cases = len(self.results)
        report.evaluated_cases = len(self.results)
        
        # 提取预测和真实值
        predicted_syndromes = [r.predicted_syndrome for r in self.results]
        actual_syndromes = [r.actual_syndrome for r in self.results]
        predicted_formulas = [r.predicted_formula for r in self.results]
        actual_formulas = [r.actual_formula for r in self.results]
        acceptability_scores = [r.acceptability_score for r in self.results]
        reasoning_scores = [r.reasoning_quality_score for r in self.results]
        reference_scores = [r.classical_reference_accuracy for r in self.results]
        
        # 计算准确率
        report.syndrome_accuracy = calculate_accuracy(predicted_syndromes, actual_syndromes)
        report.formula_accuracy = calculate_accuracy(predicted_formulas, actual_formulas)
        
        # 计算Kappa (预测与真实的一致性)
        report.syndrome_kappa = calculate_cohens_kappa(predicted_syndromes, actual_syndromes)
        report.formula_kappa = calculate_cohens_kappa(predicted_formulas, actual_formulas)
        
        # 计算临床可接受度
        acceptability_stats = calculate_clinical_acceptability(acceptability_scores)
        report.mean_acceptability = acceptability_stats["mean"]
        report.acceptability_distribution = acceptability_stats["distribution"]
        
        # 推理质量
        report.mean_reasoning_quality = np.mean(reasoning_scores) if reasoning_scores else 0.0
        
        # 经典引用准确率
        report.mean_reference_accuracy = np.mean(reference_scores) if reference_scores else 0.0
        
        # 置信区间
        binary_syndrome = [1.0 if p == a else 0.0 for p, a in zip(predicted_syndromes, actual_syndromes)]
        report.syndrome_accuracy_ci = calculate_confidence_interval(binary_syndrome)
        report.acceptability_ci = calculate_confidence_interval([float(s) for s in acceptability_scores])
        
        return report
    
    def export_for_publication(self, report: MetricsReport) -> str:
        """
        导出适合论文发表的格式
        Export in publication-ready format
        """
        output = []
        output.append("=" * 60)
        output.append("Clinical Validation Results")
        output.append("=" * 60)
        output.append("")
        
        output.append(f"Sample Size: N = {report.total_cases}")
        output.append("")
        
        output.append("Diagnostic Accuracy:")
        output.append(f"  - Syndrome Identification: {report.syndrome_accuracy:.1%} "
                     f"(95% CI: {report.syndrome_accuracy_ci[0]:.1%}-{report.syndrome_accuracy_ci[1]:.1%})")
        output.append(f"  - Formula Recommendation: {report.formula_accuracy:.1%}")
        output.append("")
        
        output.append("Inter-rater Agreement (Cohen's Kappa):")
        output.append(f"  - Syndrome: κ = {report.syndrome_kappa:.3f}")
        output.append(f"  - Formula: κ = {report.formula_kappa:.3f}")
        output.append("")
        
        output.append("Clinical Acceptability (1-5 Likert Scale):")
        output.append(f"  - Mean Score: {report.mean_acceptability:.2f} "
                     f"(95% CI: {report.acceptability_ci[0]:.2f}-{report.acceptability_ci[1]:.2f})")
        output.append("")
        
        output.append("Reasoning Quality:")
        output.append(f"  - Mean Score: {report.mean_reasoning_quality:.2f}/5.0")
        output.append(f"  - Classical Reference Accuracy: {report.mean_reference_accuracy:.1%}")
        output.append("")
        
        output.append("=" * 60)
        
        return "\n".join(output)


# 创建单例计算器
metrics_calculator = MetricsCalculator()
