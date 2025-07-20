"""Hybrid inference pipeline implementation"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from models.hybrid_system import HybridCVEvaluationSystem
from configs.hybrid_config import HybridSystemConfig
from utils.extraction import extract_json_from_prose_improved
from utils.validation import validate_evaluation_output


class HybridInference:
    """Production inference pipeline for hybrid CV evaluation"""
    
    def __init__(self, config: Optional[HybridSystemConfig] = None):
        self.config = config or HybridSystemConfig()
        self.system = HybridCVEvaluationSystem(self.config)
        self.system_loaded = False
        
    def load_models(self, 
                   model_a_path: str = "outputs/model_a_prose_evaluator",
                   model_b_path: str = "outputs/model_b_json_converter"):
        """Load trained models"""
        self.system.load_models(model_a_path, model_b_path)
        self.system_loaded = True
        
    def evaluate_cv(self, cv_text: str) -> Dict[str, Any]:
        """Evaluate a single CV"""
        if not self.system_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        return self.system.evaluate_cv(cv_text)
    
    def batch_evaluate(self, cv_texts: List[str], max_workers: int = 1) -> List[Dict[str, Any]]:
        """Evaluate multiple CVs"""
        if not self.system_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        return self.system.batch_evaluate(cv_texts)
    
    def evaluate_with_validation(self, cv_text: str) -> Dict[str, Any]:
        """Evaluate CV with output validation"""
        result = self.evaluate_cv(cv_text)
        
        # Validate output
        validation = validate_evaluation_output(result, self.config)
        result['validation'] = validation
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and configuration"""
        return {
            'system_loaded': self.system_loaded,
            'config': {
                'model_a': self.config.model_a_name,
                'model_b': self.config.model_b_name,
                'a100_optimizations': self.config.use_a100_optimizations
            },
            'evaluation_criteria': list(self.config.evaluation_criteria.keys()),
            'valid_recommendations': self.config.valid_recommendations
        }


def main():
    """CLI interface for hybrid inference"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CV Evaluation Inference')
    parser.add_argument('--cv_file', type=str, help='Path to CV text file')
    parser.add_argument('--cv_text', type=str, help='CV text directly')
    parser.add_argument('--batch_dir', type=str, help='Directory with multiple CVs')
    parser.add_argument('--output', type=str, help='Output JSON file')
    parser.add_argument('--model_a_path', type=str, 
                       default='outputs/model_a_prose_evaluator')
    parser.add_argument('--model_b_path', type=str, 
                       default='outputs/model_b_json_converter')
    
    args = parser.parse_args()
    
    # Initialize inference
    inference = HybridInference()
    inference.load_models(args.model_a_path, args.model_b_path)
    
    # Process input
    if args.cv_file:
        with open(args.cv_file, 'r', encoding='utf-8') as f:
            cv_text = f.read()
        result = inference.evaluate_with_validation(cv_text)
        results = [result]
        
    elif args.cv_text:
        result = inference.evaluate_with_validation(args.cv_text)
        results = [result]
        
    elif args.batch_dir:
        import os
        cv_files = [f for f in os.listdir(args.batch_dir) if f.endswith('.txt')]
        cv_texts = []
        for cv_file in cv_files:
            with open(os.path.join(args.batch_dir, cv_file), 'r') as f:
                cv_texts.append(f.read())
        results = inference.batch_evaluate(cv_texts)
        
    else:
        print("Please provide --cv_file, --cv_text, or --batch_dir")
        return
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results if len(results) > 1 else results[0], f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        for result in results:
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
