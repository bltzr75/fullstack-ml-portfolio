"""Reward functions for GRPO training of Model A"""

import re
import numpy as np
from typing import List, Dict, Any
from sklearn.metrics import mean_squared_error

from configs.hybrid_config import HybridSystemConfig


def prose_structure_reward_func(completions: List[Any], **kwargs) -> List[float]:
    """Reward well-structured prose evaluations with all criteria"""
    rewards = []
    config = kwargs.get('config', HybridSystemConfig())
    required_criteria = list(config.evaluation_criteria.keys())
    
    for completion in completions:
        try:
            text = completion.lower() if isinstance(completion, str) else str(completion).lower()
            reward = 0.0
            
            # Check for each criterion with score format
            criteria_found = 0
            for criterion in required_criteria:
                criterion_text = criterion.replace('_', ' ')
                pattern = f"{criterion_text}.*?\\d+/10"
                if re.search(pattern, text):
                    criteria_found += 1
                    reward += 0.3
            
            # Check for total score
            if re.search(r"total score:?\s*\d+", text):
                reward += 0.5
            
            # Check for recommendation
            if any(rec in text for rec in config.valid_recommendations):
                reward += 0.5
            
            # Check for key strengths
            if "key strengths:" in text or "strengths:" in text:
                reward += 0.3
            
            # Check for areas for improvement
            if "areas for improvement:" in text:
                reward += 0.3
            
            # Bonus for completeness
            if criteria_found >= 8:
                reward += 1.0
            
            rewards.append(min(reward, 5.0))
        except:
            rewards.append(0.0)
    
    return rewards


def prose_score_extraction_reward_func(completions: List[Any], **kwargs) -> List[float]:
    """Reward valid score extraction from prose"""
    rewards = []
    
    for completion in completions:
        try:
            text = str(completion)
            reward = 0.0
            
            # Find all score patterns
            score_pattern = r"(\d+)/10"
            scores = re.findall(score_pattern, text)
            
            if scores:
                valid_scores = [int(s) for s in scores if 1 <= int(s) <= 10]
                
                # Reward valid scores
                reward += len(valid_scores) * 0.2
                
                # Reward realistic distribution
                if valid_scores and 3 <= np.mean(valid_scores) <= 8:
                    reward += 1.0
                
                # Reward variety
                if len(set(valid_scores)) >= 5:
                    reward += 0.5
            
            rewards.append(min(reward, 3.0))
        except:
            rewards.append(0.0)
    
    return rewards


def prose_total_consistency_reward_func(completions: List[Any], **kwargs) -> List[float]:
    """Reward consistency between individual scores and total"""
    rewards = []
    
    for completion in completions:
        try:
            text = str(completion)
            
            # Extract individual scores
            score_pattern = r"(\d+)/10"
            scores = [int(s) for s in re.findall(score_pattern, text) if 1 <= int(s) <= 10]
            
            # Extract total score
            total_match = re.search(r"total score:?\s*(\d+)", text.lower())
            
            if scores and total_match:
                actual_total = int(total_match.group(1))
                expected_total = sum(scores[:10])  # Use first 10 scores
                
                diff = abs(actual_total - expected_total)
                if diff == 0:
                    reward = 2.0
                elif diff <= 2:
                    reward = 1.5
                elif diff <= 5:
                    reward = 1.0
                else:
                    reward = 0.0
            else:
                reward = 0.0
            
            rewards.append(reward)
        except:
            rewards.append(0.0)
    
    return rewards


def prose_recommendation_logic_reward_func(completions: List[Any], **kwargs) -> List[float]:
    """Reward logical recommendations based on total score"""
    rewards = []
    config = kwargs.get('config', HybridSystemConfig())
    
    for completion in completions:
        try:
            text = str(completion).lower()
            
            # Extract total score
            total_match = re.search(r"total score:?\s*(\d+)", text)
            
            # Find recommendation
            recommendation = None
            for rec in config.valid_recommendations:
                if rec in text:
                    recommendation = rec
                    break
            
            if total_match and recommendation:
                total_score = int(total_match.group(1))
                
                # Check logic
                logical = False
                if total_score >= 80 and recommendation in ['strong_hire', 'hire']:
                    logical = True
                elif 60 <= total_score < 80 and recommendation in ['hire', 'lean_hire']:
                    logical = True
                elif 40 <= total_score < 60 and recommendation in ['lean_hire', 'no_hire']:
                    logical = True
                elif total_score < 40 and recommendation in ['no_hire', 'strong_no_hire']:
                    logical = True
                
                reward = 2.0 if logical else 0.5
            else:
                reward = 0.0
            
            rewards.append(reward)
        except:
            rewards.append(0.0)
    
    return rewards


def prose_content_quality_reward_func(completions: List[Any], **kwargs) -> List[float]:
    """Reward detailed, specific evaluations"""
    rewards = []
    
    for completion in completions:
        try:
            text = str(completion)
            reward = 0.0
            
            # Length indicates detail
            if len(text) > 500:
                reward += 0.5
            if len(text) > 800:
                reward += 0.5
            
            # Quality keywords
            quality_keywords = [
                'experience', 'skills', 'demonstrates', 'shows',
                'excellent', 'strong', 'limited', 'could improve',
                'background', 'expertise', 'proficient'
            ]
            
            keywords_found = sum(1 for kw in quality_keywords if kw in text.lower())
            reward += min(keywords_found * 0.1, 1.0)
            
            # Check for specific examples
            if re.search(r"\d+ years", text):
                reward += 0.3
            
            # Strengths and improvements should be specific
            if "strengths:" in text.lower():
                strengths_text = text.lower().split("strengths:")[1].split("\n")[0]
                if len(strengths_text) > 50:
                    reward += 0.5
            
            rewards.append(min(reward, 3.0))
        except:
            rewards.append(0.0)
    
    return rewards


def prose_accuracy_reward_func(prompts: List[Any], completions: List[Any], 
                              ground_truth: List[Dict[str, Any]], **kwargs) -> List[float]:
    """Reward accuracy against ground truth prose evaluations"""
    rewards = []
    config = kwargs.get('config', HybridSystemConfig())
    
    for i, completion in enumerate(completions):
        try:
            text = str(completion)
            truth = ground_truth[i % len(ground_truth)]
            
            # Extract scores from completion
            score_pattern = r"(\w+)\s*(?:skills?|quality|potential|mindset|fit|progression|impression)?:?\s*(\d+)/10"
            found_scores = {}
            
            for match in re.finditer(score_pattern, text.lower()):
                criterion_part = match.group(1)
                score = int(match.group(2))
                
                # Match partial criterion names
                for full_criterion in config.evaluation_criteria.keys():
                    if criterion_part in full_criterion:
                        found_scores[full_criterion] = score
                        break
            
            # Compare with ground truth
            if found_scores and isinstance(truth, dict):
                matched_criteria = 0
                total_diff = 0
                
                for criterion, true_score in truth.items():
                    if criterion in found_scores and criterion in config.evaluation_criteria:
                        diff = abs(found_scores[criterion] - true_score)
                        total_diff += diff
                        matched_criteria += 1
                
                if matched_criteria > 0:
                    avg_diff = total_diff / matched_criteria
                    reward = max(0.0, 3.0 - (avg_diff * 0.5))
                else:
                    reward = 0.5
            else:
                reward = 0.5
            
            rewards.append(reward)
        except:
            rewards.append(0.0)
    
    return rewards


# List of all Model A reward functions
MODEL_A_REWARD_FUNCTIONS = [
    prose_structure_reward_func,
    prose_score_extraction_reward_func,
    prose_total_consistency_reward_func,
    prose_recommendation_logic_reward_func,
    prose_content_quality_reward_func,
    prose_accuracy_reward_func
]
