"""
Unit Tests for TCM Clinical Evaluation Module
中医临床评估模块单元测试
"""

import pytest
import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evaluation.metrics import (
    calculate_accuracy, calculate_cohens_kappa, calculate_fleiss_kappa,
    calculate_clinical_acceptability, calculate_confidence_interval,
    calculate_sensitivity_specificity, MetricsCalculator, EvaluationResult,
    MetricsReport
)
from src.evaluation.statistical_analysis import (
    calculate_descriptive_stats, paired_t_test, independent_t_test,
    chi_square_test, calculate_sample_size, calculate_power,
    StatisticalAnalyzer
)


class TestMetrics:
    """Test Evaluation Metrics"""
    
    def test_calculate_accuracy(self):
        """Test accuracy calculation"""
        predictions = ["A", "B", "A", "A", "B"]
        ground_truth = ["A", "B", "B", "A", "B"]
        
        acc = calculate_accuracy(predictions, ground_truth)
        assert acc == 0.8  # 4/5 correct
    
    def test_calculate_accuracy_perfect(self):
        """Test perfect accuracy"""
        predictions = ["A", "B", "C"]
        ground_truth = ["A", "B", "C"]
        
        acc = calculate_accuracy(predictions, ground_truth)
        assert acc == 1.0
    
    def test_calculate_cohens_kappa_perfect(self):
        """Test Cohen's Kappa with perfect agreement"""
        rater1 = ["A", "B", "C", "A", "B"]
        rater2 = ["A", "B", "C", "A", "B"]
        
        kappa = calculate_cohens_kappa(rater1, rater2)
        assert kappa == 1.0
    
    def test_calculate_cohens_kappa_moderate(self):
        """Test Cohen's Kappa with moderate agreement"""
        rater1 = ["A", "A", "B", "B", "C", "C"]
        rater2 = ["A", "B", "B", "B", "C", "A"]
        
        kappa = calculate_cohens_kappa(rater1, rater2)
        # Kappa should be between 0 and 1 for partial agreement
        assert 0 < kappa < 1
    
    def test_clinical_acceptability(self):
        """Test clinical acceptability calculation"""
        scores = [5, 4, 4, 3, 2, 5, 4, 3]
        
        result = calculate_clinical_acceptability(scores)
        
        assert result["n"] == 8
        assert 3 <= result["mean"] <= 5
        assert result["acceptable_rate"] > 0.5  # Most scores >= 3
    
    def test_confidence_interval(self):
        """Test confidence interval calculation"""
        data = [0.8, 0.85, 0.9, 0.82, 0.88]
        
        lower, upper = calculate_confidence_interval(data)
        
        assert lower < np.mean(data) < upper
        assert upper - lower < 0.5  # CI should be reasonable
    
    def test_sensitivity_specificity(self):
        """Test sensitivity/specificity calculation"""
        predictions = [True, True, False, True, False, True]
        ground_truth = [True, False, False, True, False, True]
        
        result = calculate_sensitivity_specificity(predictions, ground_truth)
        
        assert "sensitivity" in result
        assert "specificity" in result
        assert "f1_score" in result
        assert 0 <= result["sensitivity"] <= 1
        assert 0 <= result["specificity"] <= 1


class TestMetricsCalculator:
    """Test MetricsCalculator class"""
    
    def test_add_and_calculate(self):
        """Test adding results and calculating report"""
        calc = MetricsCalculator()
        
        # Add some test results
        results = [
            EvaluationResult("1", "太阳病", "太阳病", "麻黄汤", "麻黄汤", 5),
            EvaluationResult("2", "太阳病", "太阳病", "桂枝汤", "麻黄汤", 4),
            EvaluationResult("3", "少阴病", "少阴病", "四逆汤", "四逆汤", 5),
            EvaluationResult("4", "阳明病", "太阳病", "白虎汤", "麻黄汤", 2),
        ]
        
        calc.add_results(results)
        report = calc.calculate_report()
        
        assert report.total_cases == 4
        assert report.syndrome_accuracy == 0.75  # 3/4 correct
        assert report.mean_acceptability == 4.0  # (5+4+5+2)/4
    
    def test_metrics_report_to_dict(self):
        """Test MetricsReport serialization"""
        report = MetricsReport()
        report.total_cases = 100
        report.syndrome_accuracy = 0.85
        report.syndrome_kappa = 0.78
        
        report_dict = report.to_dict()
        
        assert "sample_info" in report_dict
        assert "diagnostic_accuracy" in report_dict
        assert report_dict["diagnostic_accuracy"]["syndrome_accuracy"] == 0.85
    
    def test_export_for_publication(self):
        """Test publication format export"""
        calc = MetricsCalculator()
        
        results = [
            EvaluationResult("1", "太阳病", "太阳病", "麻黄汤", "麻黄汤", 5),
            EvaluationResult("2", "太阳病", "太阳病", "桂枝汤", "桂枝汤", 4),
        ]
        calc.add_results(results)
        
        report = calc.calculate_report()
        pub_text = calc.export_for_publication(report)
        
        assert "Clinical Validation Results" in pub_text
        assert "Sample Size" in pub_text


class TestStatisticalAnalysis:
    """Test Statistical Analysis Functions"""
    
    def test_descriptive_stats(self):
        """Test descriptive statistics"""
        data = [10, 20, 30, 40, 50]
        
        stats = calculate_descriptive_stats(data)
        
        assert stats.n == 5
        assert stats.mean == 30.0
        assert stats.median == 30.0
        assert stats.min_val == 10
        assert stats.max_val == 50
    
    def test_paired_t_test(self):
        """Test paired t-test"""
        group1 = [85, 90, 78, 92, 88]
        group2 = [80, 85, 75, 88, 82]
        
        result = paired_t_test(group1, group2)
        
        assert result.test_name == "Paired t-test"
        assert result.p_value >= 0
        assert result.effect_size is not None
    
    def test_independent_t_test(self):
        """Test independent t-test"""
        group1 = [10, 12, 14, 16, 18]
        group2 = [20, 22, 24, 26, 28]
        
        result = independent_t_test(group1, group2)
        
        assert result.test_name == "Independent t-test"
        # Should be significant since groups are clearly different
        assert result.p_value < 0.05
    
    def test_chi_square(self):
        """Test chi-square test"""
        # 2x2 contingency table
        observed = [[30, 10], [15, 45]]
        
        result = chi_square_test(observed)
        
        assert result.test_name == "Chi-square test"
        assert result.statistic > 0
    
    def test_sample_size_calculation(self):
        """Test sample size calculation"""
        n = calculate_sample_size(
            effect_size=0.5,
            alpha=0.05,
            power=0.80,
            test_type="two-sample"
        )
        
        # Should require reasonable sample size for medium effect
        assert 50 < n < 200
    
    def test_power_calculation(self):
        """Test power calculation"""
        power = calculate_power(
            n=100,
            effect_size=0.5,
            alpha=0.05,
            test_type="two-sample"
        )
        
        assert 0 < power < 1


class TestStatisticalAnalyzer:
    """Test StatisticalAnalyzer class"""
    
    def test_accuracy_comparison(self):
        """Test accuracy comparison analysis"""
        analyzer = StatisticalAnalyzer()
        
        ai_accuracy = [0.85, 0.88, 0.82, 0.90, 0.87]
        baseline = [0.75, 0.78, 0.72, 0.80, 0.77]
        
        result = analyzer.analyze_accuracy_comparison(ai_accuracy, baseline)
        
        assert "ai_performance" in result
        assert "baseline_performance" in result
        assert "comparison" in result
        assert result["improvement"] > 0
    
    def test_publication_table(self):
        """Test publication table generation"""
        analyzer = StatisticalAnalyzer()
        
        data = {
            "Syndrome Accuracy": [0.85, 0.88, 0.82, 0.90, 0.87],
            "Formula Accuracy": [0.75, 0.78, 0.72, 0.80, 0.77]
        }
        
        table = analyzer.generate_publication_table(data, "Table 1: Accuracy Metrics")
        
        assert "Table 1" in table
        assert "Mean ± SD" in table


class TestValidationMetrics:
    """Test metrics relevant for JAMIA/BMC publication"""
    
    def test_kappa_interpretation(self):
        """Test Kappa interpretation for publication"""
        # Perfect agreement
        perfect = calculate_cohens_kappa(["A"]*10, ["A"]*10)
        assert perfect == 1.0
        
        # Almost perfect (>0.81)
        almost = calculate_cohens_kappa(
            ["A", "A", "A", "B", "B", "B", "C", "C", "C", "D"],
            ["A", "A", "A", "B", "B", "B", "C", "C", "D", "D"]
        )
        assert almost > 0.7  # Should be high agreement
    
    def test_clinical_threshold(self):
        """Test clinical acceptability threshold"""
        # High acceptability
        high_scores = [4, 5, 4, 5, 4, 5, 4]
        result = calculate_clinical_acceptability(high_scores, threshold=4)
        assert result["acceptable_rate"] == 1.0
        
        # Mixed acceptability
        mixed_scores = [5, 4, 3, 2, 1, 4, 3]
        result = calculate_clinical_acceptability(mixed_scores, threshold=3)
        assert 0.5 < result["acceptable_rate"] < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
