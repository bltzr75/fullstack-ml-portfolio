#!/usr/bin/env python3
"""Evaluate the complete hybrid pipeline"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from inference.hybrid_inference import HybridInference
from utils.metrics import evaluate_hybrid_system


def main():
    parser = argparse.ArgumentParser(description='Evaluate hybrid CV evaluation pipeline')
    parser.add_argument('--test_dataset', type=str, default='cv_dataset',
                       help='Path to test dataset')
    parser.add_argument('--num_samples', type=int, default=20,
                       help='Number of samples to evaluate')
    parser.add_argument('--model_a_path', type=str, 
                       default='outputs/model_a_prose_evaluator')
    parser.add_argument('--model_b_path', type=str,
                       default='outputs/model_b_json_converter')
    parser.add_argument('--output', type=str, default='evaluation_results.json',
                       help='Output file for results')
    
    args = parser.parse_args()
    
    print("🔍 Evaluating Hybrid CV Evaluation Pipeline")
    print("=" * 60)
    
    # Initialize system
    print("Loading models...")
    inference = HybridInference()
    inference.load_models(args.model_a_path, args.model_b_path)
    
    # Load test samples
    print(f"Loading test samples from {args.test_dataset}...")
    test_samples = []
    
    cv_files = sorted(Path(args.test_dataset).glob("cv_*.txt"))[:args.num_samples]
    
    for cv_file in cv_files:
        with open(cv_file, 'r', encoding='utf-8') as f:
            cv_text = f.read()
        
        # Load corresponding persona if available
        persona_file = cv_file.parent / f"persona_{cv_file.stem.split('_')[1]}.json"
        if persona_file.exists():
            with open(persona_file, 'r') as f:
                persona = json.load(f)
        else:
            persona = {}
        
        test_samples.append({
            'cv_text': cv_text,
            'metadata': persona
        })
    
    print(f"Loaded {len(test_samples)} test samples")
    
    # Evaluate samples
    print("\nEvaluating samples...")
    results = []
    
    for i, sample in enumerate(test_samples):
        print(f"  Sample {i+1}/{len(test_samples)}...", end='', flush=True)
        
        result = inference.evaluate_with_validation(sample['cv_text'])
        result['sample_metadata'] = sample['metadata']
        results.append(result)
        
        if 'error' not in result:
            print(" ✅")
        else:
            print(f" ❌ ({result['error']})")
    
    # Calculate metrics
    print("\nCalculating metrics...")
    
    successful = sum(1 for r in results if 'error' not in r)
    success_rate = successful / len(results) if results else 0
    
    # Method distribution
    methods = [r.get('pipeline_method', 'error') for r in results if 'error' not in r]
    method_counts = {}
    for method in methods:
        method_counts[method] = method_counts.get(method, 0) + 1
    
    # Criteria coverage
    criteria_coverage = []
    for result in results:
        if 'error' not in result:
            coverage = len([k for k in result.keys() 
                          if k in inference.config.evaluation_criteria])
            criteria_coverage.append(coverage / len(inference.config.evaluation_criteria))
    
    avg_coverage = sum(criteria_coverage) / len(criteria_coverage) if criteria_coverage else 0
    
    # Processing times
    processing_times = [r.get('processing_time_ms', 0) for r in results if 'error' not in r]
    avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    # Validation results
    validation_passed = sum(1 for r in results 
                          if 'validation' in r and r['validation']['valid'])
    
    # Summary
    summary = {
        'total_samples': len(results),
        'successful': successful,
        'success_rate': success_rate,
        'validation_passed': validation_passed,
        'average_criteria_coverage': avg_coverage,
        'average_processing_time_ms': avg_time,
        'method_distribution': method_counts,
        'detailed_results': results
    }
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Success Rate: {success_rate:.1%} ({successful}/{len(results)})")
    print(f"Validation Passed: {validation_passed}/{successful}")
    print(f"Average Criteria Coverage: {avg_coverage:.1%}")
    print(f"Average Processing Time: {avg_time:.0f}ms")
    print(f"\nMethod Distribution:")
    for method, count in method_counts.items():
        print(f"  {method}: {count} ({count/successful*100:.1f}%)")
    
    print(f"\nDetailed results saved to: {args.output}")


if __name__ == "__main__":
    main()
