"""Ground truth generation for CV evaluations"""

import random
from typing import Dict, Any, Tuple, List

from configs.hybrid_config import HybridSystemConfig


class GroundTruthGenerator:
    """Generate ground truth evaluations for training"""
    
    def __init__(self, config: HybridSystemConfig):
        self.config = config
        self.evaluation_criteria = config.evaluation_criteria
        self.valid_recommendations = config.valid_recommendations
    
    def generate_ground_truth(self, 
                            quality: str, 
                            exp_level: str, 
                            domain: str) -> Tuple[Dict[str, Any], str]:
        """Generate both JSON and prose ground truth"""
        
        # Generate scores
        scores = self._generate_scores(quality, exp_level, domain)
        
        # Calculate total
        total_score = sum(scores.values())
        
        # Get recommendation
        recommendation = self._get_recommendation(total_score)
        
        # Generate strengths and improvements
        strengths = self._generate_strengths(scores, domain, quality)
        improvements = self._generate_improvements(scores, exp_level, quality)
        
        # Create JSON ground truth
        json_truth = {
            **scores,
            'total_score': total_score,
            'recommendation': recommendation,
            'key_strengths': strengths,
            'areas_for_improvement': improvements,
            'processing_time_ms': random.randint(800, 2500)
        }
        
        # Generate prose ground truth
        prose_truth = self._generate_prose_evaluation(
            scores, total_score, recommendation, strengths, improvements
        )
        
        return json_truth, prose_truth
    
    def _generate_scores(self, quality: str, exp_level: str, domain: str) -> Dict[str, int]:
        """Generate evaluation scores based on parameters"""
        
        # Base scores by quality
        base_scores = {
            'excellent': 8.5,
            'good': 7.0,
            'average': 5.5,
            'below_average': 3.5
        }
        
        # Experience modifiers
        exp_modifiers = {
            'entry': -0.5,
            'mid': 0,
            'senior': 0.5,
            'executive': 1.0
        }
        
        base_score = base_scores.get(quality, 6.0)
        exp_modifier = exp_modifiers.get(exp_level.lower(), 0)
        
        scores = {}
        
        for criterion in self.evaluation_criteria.keys():
            # Base calculation
            score = base_score + exp_modifier + random.uniform(-1.0, 1.0)
            
            # Domain-specific adjustments
            if criterion == 'technical_skills' and domain == 'data_science':
                score += 0.5
            elif criterion == 'leadership_potential' and exp_level.lower() == 'executive':
                score += 1.0
            elif criterion == 'experience_relevance' and exp_level.lower() == 'entry':
                score -= 1.0
            
            # Ensure valid range
            scores[criterion] = max(1, min(10, round(score)))
        
        return scores
    
    def _get_recommendation(self, total_score: int) -> str:
        """Get recommendation based on total score"""
        if total_score >= 85:
            return 'strong_hire'
        elif total_score >= 70:
            return 'hire'
        elif total_score >= 55:
            return 'lean_hire'
        elif total_score >= 40:
            return 'no_hire'
        else:
            return 'strong_no_hire'
    
    def _generate_strengths(self, 
                          scores: Dict[str, int], 
                          domain: str, 
                          quality: str) -> List[str]:
        """Generate key strengths based on scores"""
        
        # Find top scoring criteria
        high_scores = [(k, v) for k, v in scores.items() if v >= 8]
        high_scores.sort(key=lambda x: x[1], reverse=True)
        
        strengths = []
        
        if high_scores:
            for criterion, _ in high_scores[:2]:
                strength = f"Strong {criterion.replace('_', ' ')}"
                strengths.append(strength)
        
        # Add domain-specific strength
        if quality in ['excellent', 'good']:
            strengths.append(f"Excellent {domain.replace('_', ' ')} expertise")
        
        # Ensure at least 2 strengths
        while len(strengths) < 2:
            strengths.append("Solid professional background")
        
        return strengths[:3]
    
    def _generate_improvements(self, 
                             scores: Dict[str, int], 
                             exp_level: str, 
                             quality: str) -> List[str]:
        """Generate areas for improvement based on scores"""
        
        # Find lower scoring criteria
        low_scores = [(k, v) for k, v in scores.items() if v <= 5]
        low_scores.sort(key=lambda x: x[1])
        
        improvements = []
        
        if low_scores:
            for criterion, _ in low_scores[:2]:
                improvement = f"Could improve {criterion.replace('_', ' ')}"
                improvements.append(improvement)
        
        # Experience-based improvements
        if exp_level.lower() == 'entry':
            improvements.append("Needs more professional experience")
        elif quality == 'below_average':
            improvements.append("Requires skill development")
        
        # Ensure at least 1 improvement
        if not improvements:
            improvements.append("Continue professional development")
        
        return improvements[:2]
    
    def _generate_prose_evaluation(self,
                                 scores: Dict[str, int],
                                 total_score: int,
                                 recommendation: str,
                                 strengths: List[str],
                                 improvements: List[str]) -> str:
        """Generate natural language evaluation"""
        
        prose_parts = []
        
        # Individual criteria evaluations
        for criterion, score in scores.items():
            criterion_text = criterion.replace('_', ' ').title()
            
            # Add qualitative assessment
            if score >= 8:
                qualifier = "Excellent"
            elif score >= 6:
                qualifier = "Good"
            elif score >= 4:
                qualifier = "Average"
            else:
                qualifier = "Below average"
            
            prose_parts.append(
                f"{criterion_text}: {score}/10. {qualifier} performance in this area."
            )
        
        # Total and recommendation
        prose_parts.append(f"\nTotal Score: {total_score}")
        prose_parts.append(f"Recommendation: {recommendation}")
        
        # Strengths
        prose_parts.append("\nKey Strengths:")
        for strength in strengths:
            prose_parts.append(f"- {strength}")
        
        # Improvements
        prose_parts.append("\nAreas for Improvement:")
        for improvement in improvements:
            prose_parts.append(f"- {improvement}")
        
        return "\n".join(prose_parts)
