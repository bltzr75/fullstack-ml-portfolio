"""Validation utilities for CV evaluation outputs"""

from typing import Dict, Any, List
from configs.hybrid_config import HybridSystemConfig


def validate_evaluation_output(result: Dict[str, Any], 
                              config: HybridSystemConfig) -> Dict[str, Any]:
    """Validate CV evaluation output format and content"""
    
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'criteria_coverage': 0,
        'format_valid': True,
        'scores_valid': True,
        'recommendation_valid': True
    }
    
    # Check for error
    if 'error' in result:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Error in result: {result['error']}")
        return validation_result
    
    # Check required fields
    required_fields = list(config.evaluation_criteria.keys()) + [
        'total_score', 'recommendation', 'key_strengths', 
        'areas_for_improvement', 'processing_time_ms'
    ]
    
    missing_fields = [field for field in required_fields if field not in result]
    if missing_fields:
        validation_result['format_valid'] = False
        validation_result['errors'].append(f"Missing required fields: {missing_fields}")
    
    # Check criteria coverage
    criteria_found = [k for k in result.keys() if k in config.evaluation_criteria]
    validation_result['criteria_coverage'] = len(criteria_found) / len(config.evaluation_criteria)
    
    if len(criteria_found) < 5:
        validation_result['warnings'].append(
            f"Low criteria coverage: {len(criteria_found)}/{len(config.evaluation_criteria)}"
        )
    
    # Validate scores
    for criterion in config.evaluation_criteria.keys():
        if criterion in result:
            score = result[criterion]
            if not isinstance(score, (int, float)) or not (1 <= score <= 10):
                validation_result['scores_valid'] = False
                validation_result['errors'].append(
                    f"Invalid score for {criterion}: {score} (must be 1-10)"
                )
    
    # Validate total score
    if 'total_score' in result:
        total = result['total_score']
        if not isinstance(total, (int, float)) or not (10 <= total <= 100):
            validation_result['errors'].append(
                f"Invalid total score: {total} (must be 10-100)"
            )
        
        # Check consistency
        individual_sum = sum(result.get(k, 0) for k in config.evaluation_criteria.keys())
        if abs(individual_sum - total) > 5:
            validation_result['warnings'].append(
                f"Total score inconsistency: sum={individual_sum}, total={total}"
            )
    
    # Validate recommendation
    if 'recommendation' in result:
        if result['recommendation'] not in config.valid_recommendations:
            validation_result['recommendation_valid'] = False
            validation_result['errors'].append(
                f"Invalid recommendation: {result['recommendation']}"
            )
    
    # Validate list fields
    list_fields = ['key_strengths', 'areas_for_improvement']
    for field in list_fields:
        if field in result and not isinstance(result[field], list):
            validation_result['errors'].append(f"{field} must be a list")
    
    # Set overall validity
    validation_result['valid'] = (
        len(validation_result['errors']) == 0 and
        validation_result['format_valid'] and
        validation_result['scores_valid'] and
        validation_result['recommendation_valid']
    )
    
    return validation_result


def validate_cv_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Simple validation function for backwards compatibility"""
    config = HybridSystemConfig()
    validation = validate_evaluation_output(result, config)
    
    return {
        'valid': validation['valid'],
        'reason': validation['errors'][0] if validation['errors'] else 'All validations passed'
    }
