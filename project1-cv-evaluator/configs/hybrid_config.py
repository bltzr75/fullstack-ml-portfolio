"""Hybrid system configuration for CV evaluation"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class HybridSystemConfig:
    """Configuration for the hybrid CV evaluation system"""
    
    # Model A (Prose Evaluator) Configuration
    model_a_name: str = "NousResearch/Hermes-2-Pro-Mistral-7B"
    model_a_lora_rank: int = 64
    model_a_max_seq_length: int = 2048
    model_a_training_steps: int = 50
    
    # Model B (JSON Converter) Configuration
    model_b_name: str = "gpt2"
    model_b_lora_rank: int = 32
    model_b_max_seq_length: int = 1024
    model_b_training_steps: int = 500
    
    # Shared Configuration
    checkpoint_every: int = 10
    cache_dir: str = "/workspace/hf_cache"
    use_a100_optimizations: bool = True
    
    # Training Configuration
    train_split: float = 0.8
    random_seed: int = 42
    
    # Evaluation Criteria
    evaluation_criteria: Dict[str, str] = None
    valid_recommendations: List[str] = None
    
    def __post_init__(self):
        if self.evaluation_criteria is None:
            self.evaluation_criteria = {
                "technical_skills": "Technical expertise and proficiency relevant to role",
                "experience_relevance": "Relevance and quality of work experience",
                "education_quality": "Quality and prestige of educational background",
                "leadership_potential": "Leadership experience and management potential",
                "communication_skills": "Written communication and presentation skills",
                "problem_solving": "Problem-solving abilities and analytical thinking",
                "innovation_mindset": "Innovation, creativity, and forward-thinking",
                "cultural_fit": "Cultural alignment and team collaboration indicators",
                "career_progression": "Career growth trajectory and advancement",
                "overall_impression": "Overall assessment and candidate potential"
            }
        
        if self.valid_recommendations is None:
            self.valid_recommendations = [
                'strong_hire', 'hire', 'lean_hire', 'no_hire', 'strong_no_hire'
            ]

# System prompts
MODEL_A_SYSTEM_PROMPT = """You are a professional CV evaluator with years of hiring experience.
Analyze the CV and provide a structured evaluation in clear prose covering ALL of these criteria:

1. Technical Skills (score 1-10): Assess technical expertise
2. Experience Relevance (score 1-10): Evaluate work experience quality
3. Education Quality (score 1-10): Review educational background
4. Leadership Potential (score 1-10): Assess leadership capabilities
5. Communication Skills (score 1-10): Evaluate communication abilities
6. Problem Solving (score 1-10): Assess analytical thinking
7. Innovation Mindset (score 1-10): Review creativity and innovation
8. Cultural Fit (score 1-10): Evaluate team collaboration potential
9. Career Progression (score 1-10): Assess career growth trajectory
10. Overall Impression (score 1-10): Provide overall assessment

Format your response as:
- Start each criterion with its name followed by ": X/10" where X is the score
- After all scores, state "Total Score: Y" where Y is the sum
- Then state "Recommendation: [recommendation]" using one of: strong_hire, hire, lean_hire, no_hire, strong_no_hire
- List "Key Strengths:" followed by 2-3 specific strengths
- List "Areas for Improvement:" followed by 1-2 areas
- Be specific and detailed in your evaluation"""

MODEL_B_SYSTEM_PROMPT = """Convert the CV evaluation prose into a JSON object.
Extract all scores (1-10), total score, recommendation, strengths, and improvements.
Output ONLY valid JSON, no explanations."""
