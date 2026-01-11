"""
Statistical Analysis Tools for TCM Clinical Studies
中医临床研究统计分析工具

Implements statistical methods commonly required for
medical informatics publications (JAMIA, BMC).

Methods Include:
1. Descriptive Statistics
2. Hypothesis Testing
3. Subgroup Analysis
4. Sample Size Calculation
5. Power Analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from scipy import stats
import json


@dataclass
class DescriptiveStats:
    """描述性统计结果"""
    n: int
    mean: float
    std: float
    median: float
    q1: float  # 25th percentile
    q3: float  # 75th percentile
    min_val: float
    max_val: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "n": self.n,
            "mean": round(self.mean, 4),
            "std": round(self.std, 4),
            "median": round(self.median, 4),
            "IQR": f"{round(self.q1, 2)}-{round(self.q3, 2)}",
            "range": f"{round(self.min_val, 2)}-{round(self.max_val, 2)}"
        }
    
    def to_publication_string(self, format: str = "mean_std") -> str:
        """生成适合论文发表的格式字符串"""
        if format == "mean_std":
            return f"{self.mean:.2f} ± {self.std:.2f}"
        elif format == "median_iqr":
            return f"{self.median:.2f} ({self.q1:.2f}-{self.q3:.2f})"
        else:
            return f"{self.mean:.2f}"


@dataclass  
class HypothesisTestResult:
    """假设检验结果"""
    test_name: str
    statistic: float
    p_value: float
    effect_size: Optional[float] = None
    confidence_interval: Optional[Tuple[float, float]] = None
    interpretation: str = ""
    
    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value < alpha
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test": self.test_name,
            "statistic": round(self.statistic, 4),
            "p_value": round(self.p_value, 6),
            "effect_size": round(self.effect_size, 4) if self.effect_size else None,
            "significant_at_0.05": self.is_significant(0.05),
            "interpretation": self.interpretation
        }


def calculate_descriptive_stats(data: List[float]) -> DescriptiveStats:
    """
    计算描述性统计
    Calculate descriptive statistics
    """
    if not data:
        return DescriptiveStats(0, 0, 0, 0, 0, 0, 0, 0)
    
    arr = np.array(data)
    return DescriptiveStats(
        n=len(arr),
        mean=float(np.mean(arr)),
        std=float(np.std(arr, ddof=1)) if len(arr) > 1 else 0,
        median=float(np.median(arr)),
        q1=float(np.percentile(arr, 25)),
        q3=float(np.percentile(arr, 75)),
        min_val=float(np.min(arr)),
        max_val=float(np.max(arr))
    )


def paired_t_test(
    group1: List[float],
    group2: List[float],
    alpha: float = 0.05
) -> HypothesisTestResult:
    """
    配对t检验
    Paired t-test
    
    用于比较同一组受试者在两种条件下的差异
    Used for comparing the same subjects under two conditions
    """
    if len(group1) != len(group2):
        raise ValueError("Groups must have equal length for paired t-test")
    
    statistic, p_value = stats.ttest_rel(group1, group2)
    
    # Cohen's d for paired samples
    diff = np.array(group1) - np.array(group2)
    effect_size = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff) > 0 else 0
    
    # Confidence interval for the difference
    mean_diff = np.mean(diff)
    se_diff = stats.sem(diff)
    ci = stats.t.interval(1-alpha, len(diff)-1, loc=mean_diff, scale=se_diff)
    
    interpretation = _interpret_effect_size(effect_size)
    
    return HypothesisTestResult(
        test_name="Paired t-test",
        statistic=float(statistic),
        p_value=float(p_value),
        effect_size=float(effect_size),
        confidence_interval=ci,
        interpretation=interpretation
    )


def independent_t_test(
    group1: List[float],
    group2: List[float],
    alpha: float = 0.05
) -> HypothesisTestResult:
    """
    独立样本t检验
    Independent samples t-test
    """
    statistic, p_value = stats.ttest_ind(group1, group2)
    
    # Cohen's d
    pooled_std = np.sqrt(
        ((len(group1)-1)*np.var(group1, ddof=1) + (len(group2)-1)*np.var(group2, ddof=1)) /
        (len(group1) + len(group2) - 2)
    )
    effect_size = (np.mean(group1) - np.mean(group2)) / pooled_std if pooled_std > 0 else 0
    
    interpretation = _interpret_effect_size(effect_size)
    
    return HypothesisTestResult(
        test_name="Independent t-test",
        statistic=float(statistic),
        p_value=float(p_value),
        effect_size=float(effect_size),
        interpretation=interpretation
    )


def mann_whitney_u_test(
    group1: List[float],
    group2: List[float]
) -> HypothesisTestResult:
    """
    Mann-Whitney U检验
    Mann-Whitney U test (non-parametric)
    
    用于两组独立样本的非参数比较
    """
    statistic, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
    
    # Effect size: rank-biserial correlation
    n1, n2 = len(group1), len(group2)
    effect_size = 1 - (2 * statistic) / (n1 * n2)
    
    return HypothesisTestResult(
        test_name="Mann-Whitney U test",
        statistic=float(statistic),
        p_value=float(p_value),
        effect_size=float(effect_size),
        interpretation=f"Rank-biserial r = {effect_size:.3f}"
    )


def wilcoxon_signed_rank_test(
    group1: List[float],
    group2: List[float]
) -> HypothesisTestResult:
    """
    Wilcoxon符号秩检验
    Wilcoxon signed-rank test (non-parametric paired)
    """
    statistic, p_value = stats.wilcoxon(group1, group2)
    
    return HypothesisTestResult(
        test_name="Wilcoxon signed-rank test",
        statistic=float(statistic),
        p_value=float(p_value),
        interpretation="Non-parametric paired comparison"
    )


def chi_square_test(
    observed: List[List[int]],
    expected: Optional[List[List[int]]] = None
) -> HypothesisTestResult:
    """
    卡方检验
    Chi-square test
    
    用于分类变量的独立性或拟合优度检验
    """
    observed_array = np.array(observed)
    
    if expected is None:
        # Independence test
        statistic, p_value, dof, expected_freq = stats.chi2_contingency(observed_array)
    else:
        # Goodness of fit
        statistic, p_value = stats.chisquare(observed_array.flatten(), expected)
        dof = len(observed_array.flatten()) - 1
    
    # Cramér's V effect size
    n = observed_array.sum()
    min_dim = min(observed_array.shape) - 1
    cramers_v = np.sqrt(statistic / (n * min_dim)) if min_dim > 0 and n > 0 else 0
    
    return HypothesisTestResult(
        test_name="Chi-square test",
        statistic=float(statistic),
        p_value=float(p_value),
        effect_size=float(cramers_v),
        interpretation=f"Cramér's V = {cramers_v:.3f}"
    )


def mcnemar_test(
    table: List[List[int]]
) -> HypothesisTestResult:
    """
    McNemar检验
    McNemar's test
    
    用于配对分类数据的比较
    Commonly used for before-after comparisons or matched-pair designs
    """
    # table is 2x2: [[a, b], [c, d]]
    b = table[0][1]
    c = table[1][0]
    
    # McNemar's test with continuity correction
    statistic = (abs(b - c) - 1) ** 2 / (b + c) if (b + c) > 0 else 0
    p_value = 1 - stats.chi2.cdf(statistic, df=1)
    
    return HypothesisTestResult(
        test_name="McNemar's test",
        statistic=float(statistic),
        p_value=float(p_value),
        interpretation=f"Discordant pairs: b={b}, c={c}"
    )


def calculate_sample_size(
    effect_size: float,
    alpha: float = 0.05,
    power: float = 0.80,
    test_type: str = "two-sample"
) -> int:
    """
    计算样本量
    Calculate required sample size
    
    Args:
        effect_size: Cohen's d effect size
        alpha: significance level (default 0.05)
        power: statistical power (default 0.80)
        test_type: "two-sample" or "one-sample"
        
    Returns:
        Required sample size per group
    """
    # Z values
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    
    if test_type == "two-sample":
        # Two-sample t-test
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
    else:
        # One-sample t-test
        n = ((z_alpha + z_beta) / effect_size) ** 2
    
    return int(np.ceil(n))


def calculate_power(
    n: int,
    effect_size: float,
    alpha: float = 0.05,
    test_type: str = "two-sample"
) -> float:
    """
    计算统计功效
    Calculate statistical power
    """
    z_alpha = stats.norm.ppf(1 - alpha/2)
    
    if test_type == "two-sample":
        z_beta = effect_size * np.sqrt(n/2) - z_alpha
    else:
        z_beta = effect_size * np.sqrt(n) - z_alpha
    
    power = stats.norm.cdf(z_beta)
    return float(power)


def subgroup_analysis(
    data: Dict[str, List[float]],
    test_func: callable = independent_t_test
) -> Dict[str, Any]:
    """
    亚组分析
    Subgroup analysis
    
    Args:
        data: Dictionary of subgroup name -> values
        test_func: Statistical test function to use
        
    Returns:
        Subgroup comparison results
    """
    subgroups = list(data.keys())
    results = {
        "descriptive": {},
        "comparisons": []
    }
    
    # Descriptive statistics for each subgroup
    for name, values in data.items():
        results["descriptive"][name] = calculate_descriptive_stats(values).to_dict()
    
    # Pairwise comparisons
    for i in range(len(subgroups)):
        for j in range(i+1, len(subgroups)):
            group1_name = subgroups[i]
            group2_name = subgroups[j]
            
            test_result = test_func(data[group1_name], data[group2_name])
            
            results["comparisons"].append({
                "groups": f"{group1_name} vs {group2_name}",
                "test_result": test_result.to_dict()
            })
    
    return results


def _interpret_effect_size(d: float) -> str:
    """解释效应量大小"""
    d = abs(d)
    if d < 0.2:
        return "negligible effect"
    elif d < 0.5:
        return "small effect"
    elif d < 0.8:
        return "medium effect"
    else:
        return "large effect"


class StatisticalAnalyzer:
    """
    统计分析器
    Statistical Analyzer for clinical studies
    """
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    def analyze_accuracy_comparison(
        self,
        ai_accuracy: List[float],
        baseline_accuracy: List[float],
        method: str = "paired"
    ) -> Dict[str, Any]:
        """
        比较AI系统与基线的准确率
        Compare AI system accuracy with baseline
        """
        if method == "paired":
            test_result = paired_t_test(ai_accuracy, baseline_accuracy)
        else:
            test_result = independent_t_test(ai_accuracy, baseline_accuracy)
        
        ai_stats = calculate_descriptive_stats(ai_accuracy)
        baseline_stats = calculate_descriptive_stats(baseline_accuracy)
        
        result = {
            "ai_performance": ai_stats.to_dict(),
            "baseline_performance": baseline_stats.to_dict(),
            "comparison": test_result.to_dict(),
            "improvement": (ai_stats.mean - baseline_stats.mean) / baseline_stats.mean * 100
            if baseline_stats.mean > 0 else 0
        }
        
        self.results.append(result)
        return result
    
    def analyze_syndrome_distribution(
        self,
        predicted_syndromes: List[str],
        actual_syndromes: List[str]
    ) -> Dict[str, Any]:
        """
        分析证型分布
        Analyze syndrome distribution
        """
        from collections import Counter
        
        pred_counts = Counter(predicted_syndromes)
        actual_counts = Counter(actual_syndromes)
        
        all_syndromes = set(pred_counts.keys()) | set(actual_counts.keys())
        
        # Create contingency table for chi-square
        observed = []
        for syndrome in all_syndromes:
            observed.append([pred_counts.get(syndrome, 0), actual_counts.get(syndrome, 0)])
        
        chi2_result = chi_square_test(observed) if len(observed) > 1 else None
        
        return {
            "predicted_distribution": dict(pred_counts),
            "actual_distribution": dict(actual_counts),
            "chi_square_test": chi2_result.to_dict() if chi2_result else None
        }
    
    def generate_publication_table(
        self,
        data: Dict[str, List[float]],
        title: str = "Table 1"
    ) -> str:
        """
        生成论文发表用表格
        Generate publication-ready table
        """
        lines = []
        lines.append(f"\n{title}")
        lines.append("-" * 80)
        lines.append(f"{'Variable':<20} {'N':>8} {'Mean ± SD':>20} {'Median (IQR)':>25}")
        lines.append("-" * 80)
        
        for name, values in data.items():
            stats_result = calculate_descriptive_stats(values)
            lines.append(
                f"{name:<20} {stats_result.n:>8} "
                f"{stats_result.to_publication_string('mean_std'):>20} "
                f"{stats_result.to_publication_string('median_iqr'):>25}"
            )
        
        lines.append("-" * 80)
        return "\n".join(lines)
    
    def export_for_spss(self, filename: str = "data_export.csv") -> str:
        """
        导出SPSS兼容格式
        Export in SPSS-compatible format
        """
        # Returns CSV format string
        return "id,variable,value\n"  # Simplified


# 创建单例分析器
statistical_analyzer = StatisticalAnalyzer()
