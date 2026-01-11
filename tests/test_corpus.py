"""
Unit Tests for TCM Chain-of-Thought Corpus Module
中医思维链语料库模块单元测试
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus.tcm_cot_schema import (
    ChainOfThought, DiagnosticEvidence, DiagnosticMethod,
    PulseGridData, PulseQuality, ReasoningStep,
    SyndromeDifferentiation, SyndromeType,
    TreatmentPrinciple, PrescriptionRationale, HerbEntry
)
from src.corpus.knowledge_base import knowledge_base, KnowledgeBase
from src.corpus.cot_generator import generate_chain_of_thought, ChainOfThoughtGenerator


class TestTCMCotSchema:
    """Test TCM Chain-of-Thought Schema"""
    
    def test_diagnostic_evidence_creation(self):
        """Test creating diagnostic evidence"""
        evidence = DiagnosticEvidence(
            method=DiagnosticMethod.PALPATION,
            observation="脉浮紧",
            clinical_significance="表寒证",
            confidence=0.9
        )
        assert evidence.method == DiagnosticMethod.PALPATION
        assert evidence.observation == "脉浮紧"
        assert evidence.confidence == 0.9
    
    def test_pulse_grid_data(self):
        """Test pulse grid data structure"""
        pulse_grid = PulseGridData(
            left_cun={"浮": "有力"},
            overall_assessment="六脉浮紧",
            pulse_features=[PulseQuality.FLOATING, PulseQuality.WIRY]
        )
        assert pulse_grid.left_cun == {"浮": "有力"}
        assert len(pulse_grid.pulse_features) == 2
    
    def test_syndrome_differentiation(self):
        """Test syndrome differentiation structure"""
        syndrome = SyndromeDifferentiation(
            primary_syndrome=SyndromeType.TAIYANG,
            secondary_syndromes=[SyndromeType.EXTERIOR, SyndromeType.COLD],
            evidence_summary="恶寒发热、无汗、脉浮紧",
            key_symptoms=["恶寒", "发热", "无汗"]
        )
        assert syndrome.primary_syndrome == SyndromeType.TAIYANG
        assert len(syndrome.secondary_syndromes) == 2
    
    def test_chain_of_thought_to_dict(self):
        """Test ChainOfThought serialization"""
        cot = ChainOfThought(cot_id="test_001")
        cot.chief_complaint = "发热恶寒2天"
        
        cot_dict = cot.to_dict()
        assert cot_dict["cot_id"] == "test_001"
        assert cot_dict["chief_complaint"] == "发热恶寒2天"
    
    def test_chain_of_thought_to_json(self):
        """Test ChainOfThought JSON serialization"""
        cot = ChainOfThought(cot_id="test_002")
        json_str = cot.to_json()
        assert '"cot_id": "test_002"' in json_str


class TestKnowledgeBase:
    """Test Knowledge Base"""
    
    def test_get_clause(self):
        """Test getting Shanghan Lun clause"""
        clause = knowledge_base.get_clause("TAIYANG_001")
        assert clause is not None
        assert "太阳之为病" in clause["original_text"]
    
    def test_get_formula(self):
        """Test getting formula information"""
        formula = knowledge_base.get_formula("桂枝汤")
        assert formula is not None
        assert formula["pinyin"] == "Guizhi Tang"
        assert len(formula["composition"]) == 5
    
    def test_match_syndrome_to_formula(self):
        """Test syndrome-formula matching"""
        symptoms = ["发热", "汗出", "恶风"]
        pulse = ["浮", "缓"]
        
        matches = knowledge_base.match_syndrome_to_formula(symptoms, pulse)
        assert len(matches) > 0
        # 桂枝汤 should be in top matches for these symptoms
        formula_names = [m["formula_name"] for m in matches]
        assert "桂枝汤" in formula_names
    
    def test_check_herb_compatibility(self):
        """Test herb compatibility checking"""
        # Test prohibited combination
        herbs = ["甘草", "甘遂"]  # 十八反
        result = knowledge_base.check_herb_compatibility(herbs)
        assert len(result["prohibited"]) > 0
        
        # Test enhancement combination
        herbs = ["附子", "干姜"]  # 相须
        result = knowledge_base.check_herb_compatibility(herbs)
        assert len(result["enhancements"]) > 0
    
    def test_identify_six_meridian_pattern(self):
        """Test six meridian pattern identification"""
        symptoms = ["恶寒", "发热", "头痛"]
        pulse = ["浮"]
        
        patterns = knowledge_base.identify_six_meridian_pattern(symptoms, pulse)
        assert len(patterns) > 0
        # Taiyang should be top match
        assert patterns[0]["pattern"] == "太阳病"
    
    def test_get_classical_reference(self):
        """Test getting classical references for syndrome"""
        refs = knowledge_base.get_classical_reference("太阳伤寒证")
        assert len(refs) > 0


class TestChainOfThoughtGenerator:
    """Test Chain-of-Thought Generator"""
    
    def test_generate_cot_basic(self):
        """Test basic CoT generation"""
        pulse_data = {
            "positions": {
                "1": {"levels": {"fu": "紧"}},
                "8": {"value": "浮紧"}
            }
        }
        symptoms = ["恶寒", "发热", "无汗", "头痛"]
        
        cot = generate_chain_of_thought(
            pulse_grid_data=pulse_data,
            symptoms=symptoms,
            chief_complaint="恶寒发热2天"
        )
        
        assert cot is not None
        assert cot.chief_complaint == "恶寒发热2天"
        assert len(cot.reasoning_steps) >= 3
    
    def test_generate_cot_taiyang_shanghan(self):
        """Test CoT generation for Taiyang Shanghan case"""
        pulse_data = {
            "positions": {
                "1": {"levels": {"fu": "浮紧"}},
                "2": {"levels": {"fu": "浮紧"}},
                "3": {"levels": {"fu": "紧"}},
                "8": {"value": "浮紧"}
            }
        }
        symptoms = ["恶寒", "发热", "无汗", "头痛", "身痛", "喘"]
        
        cot = generate_chain_of_thought(
            pulse_grid_data=pulse_data,
            symptoms=symptoms,
            chief_complaint="恶寒发热、头身疼痛2天"
        )
        
        # Should identify as Taiyang
        if cot.syndrome_differentiation:
            assert cot.syndrome_differentiation.primary_syndrome == SyndromeType.TAIYANG
        
        # Should recommend 麻黄汤
        if cot.prescription:
            assert "麻黄" in cot.prescription.formula_name
    
    def test_generate_cot_shaoyin(self):
        """Test CoT generation for Shaoyin case"""
        pulse_data = {
            "positions": {
                "1": {"levels": {"fu": "微弱", "chen": "几无"}},
                "8": {"value": "微细"}
            }
        }
        symptoms = ["四肢厥冷", "腹泻", "精神萎靡"]
        
        cot = generate_chain_of_thought(
            pulse_grid_data=pulse_data,
            symptoms=symptoms,
            chief_complaint="四肢厥冷、腹泻3天"
        )
        
        assert cot is not None
        assert len(cot.diagnostic_evidence) > 0
    
    def test_cot_has_classical_references(self):
        """Test that CoT includes classical references"""
        pulse_data = {"positions": {"8": {"value": "浮紧"}}}
        symptoms = ["恶寒", "发热"]
        
        cot = generate_chain_of_thought(
            pulse_grid_data=pulse_data,
            symptoms=symptoms,
            chief_complaint="感冒"
        )
        
        # At least one reasoning step should have classical reference
        has_reference = any(
            step.classical_reference is not None 
            for step in cot.reasoning_steps
        )
        assert has_reference


class TestIntegration:
    """Integration Tests"""
    
    def test_full_diagnosis_workflow(self):
        """Test complete diagnosis workflow"""
        # 1. Prepare clinical data
        pulse_data = {
            "positions": {
                "1": {"levels": {"fu": "浮紧", "zhong": "有力", "chen": "弱"}},
                "2": {"levels": {"fu": "紧", "zhong": "中等", "chen": "弱"}},
                "3": {"levels": {"fu": "紧", "zhong": "中等", "chen": "弱"}},
                "7": {"value": "太阳伤寒"},
                "8": {"value": "浮紧"},
                "9": {"value": "发汗解表"}
            }
        }
        symptoms = ["恶寒", "发热", "无汗", "头痛", "身痛", "骨节疼痛", "喘"]
        
        # 2. Generate CoT
        cot = generate_chain_of_thought(
            pulse_grid_data=pulse_data,
            symptoms=symptoms,
            chief_complaint="恶寒发热、头身疼痛2天，无汗，微喘"
        )
        
        # 3. Verify complete chain
        assert cot.cot_id is not None
        assert len(cot.diagnostic_evidence) > 0
        assert len(cot.reasoning_steps) >= 3
        assert cot.syndrome_differentiation is not None
        assert cot.treatment_principle is not None
        assert cot.prescription is not None
        
        # 4. Verify JSON serialization
        json_output = cot.to_json()
        assert len(json_output) > 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
