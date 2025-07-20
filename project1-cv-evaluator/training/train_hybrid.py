"""Main training script for the hybrid CV evaluation system"""

import os
import sys
import json
import torch
import argparse
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.hybrid_config import HybridSystemConfig
from data.dataset_processor import HybridDatasetProcessor
from training.train_model_a import train_model_a
from training.train_model_b import train_model_b
from models.hybrid_system import HybridCVEvaluationSystem
from utils.metrics import evaluate_hybrid_system


def main():
    parser = argparse.ArgumentParser(description='Train Hybrid CV Evaluation System')
    
    # Dataset arguments
    parser.add_argument('--cv_dataset_path', type=str, default='cv_dataset',
                       help='Path to CV dataset')
    parser.add_argument('--skip_dataset_creation', action='store_true',
                       help='Skip dataset creation if already exists')
    
    # Model arguments
    parser.add_argument('--model_a_steps', type=int, default=50,
                       help='Training steps for Model A (GRPO)')
    parser.add_argument('--model_b_steps', type=int, default=500,
                       help='Training steps for Model B (SFT)')
    
    # Training arguments
    parser.add_argument('--train_model_a_only', action='store_true',
                       help='Train only Model A')
    parser.add_argument('--train_model_b_only', action='store_true',
                       help='Train only Model B')
    parser.add_argument('--skip_training', action='store_true',
                       help='Skip training and only evaluate')
    
    # Hardware arguments
    parser.add_argument('--use_a100', action='store_true', default=True,
                       help='Use A100 optimizations')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 HYBRID CV EVALUATION SYSTEM TRAINING")
    print("=" * 70)
    
    # Initialize configuration
    config = HybridSystemConfig(
        model_a_training_steps=args.model_a_steps,
        model_b_training_steps=args.model_b_steps,
        use_a100_optimizations=args.use_a100
    )
    
    # Setup directories
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("checkpoints", exist_ok=True)
    
    # Process dataset
    if not args.skip_dataset_creation:
        print("\n📊 Processing dataset for hybrid training...")
        processor = HybridDatasetProcessor(config)
        model_a_train, model_a_val, model_b_train, model_b_val = processor.process_dataset(
            args.cv_dataset_path
        )
        print(f"✅ Dataset ready: {len(model_a_train)} train samples")
    else:
        print("⏭️ Skipping dataset creation")
    
    # Training
    if not args.skip_training:
        # Train Model A (GRPO for prose evaluation)
        if not args.train_model_b_only:
            print("\n🎯 Training Model A (Prose Evaluator) with GRPO...")
            model_a_success = train_model_a(config, model_a_train, model_a_val)
            if not model_a_success:
                print("❌ Model A training failed!")
                return 1
        
        # Train Model B (SFT for JSON conversion)
        if not args.train_model_a_only:
            print("\n🎯 Training Model B (JSON Converter) with SFT...")
            model_b_success = train_model_b(config, model_b_train, model_b_val)
            if not model_b_success:
                print("❌ Model B training failed!")
                return 1
    
    # Evaluation
    print("\n📊 Evaluating hybrid system...")
    
    # Load trained models
    hybrid_system = HybridCVEvaluationSystem(config)
    
    model_a_path = "outputs/model_a_prose_evaluator" if os.path.exists("outputs/model_a_prose_evaluator") else None
    model_b_path = "outputs/model_b_json_converter" if os.path.exists("outputs/model_b_json_converter") else None
    
    hybrid_system.load_models(model_a_path, model_b_path)
    
    # Evaluate system
    if 'model_a_val' in locals():
        metrics = evaluate_hybrid_system(hybrid_system, model_a_val)
        
        print("\n📈 EVALUATION RESULTS:")
        print(f"  ✅ Success Rate: {metrics['success_rate']:.1%}")
        print(f"  📊 Average Criteria Coverage: {metrics['avg_criteria_coverage']:.1%}")
        print(f"  ⏱️ Average Processing Time: {metrics['avg_processing_time']:.0f}ms")
        print(f"  🔧 Primary Method: {metrics['primary_method']}")
        
        # Save metrics
        with open("outputs/evaluation_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
    
    # Save system configuration
    system_config = {
        "model_a": {
            "name": config.model_a_name,
            "training_steps": config.model_a_training_steps,
            "lora_rank": config.model_a_lora_rank
        },
        "model_b": {
            "name": config.model_b_name,
            "training_steps": config.model_b_training_steps,
            "lora_rank": config.model_b_lora_rank
        },
        "training_completed": datetime.now().isoformat(),
        "use_a100_optimizations": config.use_a100_optimizations
    }
    
    with open("outputs/system_config.json", "w") as f:
        json.dump(system_config, f, indent=2)
    
    print("\n✅ Training pipeline completed successfully!")
    print("📁 Models saved in: outputs/")
    print("📊 Metrics saved in: outputs/evaluation_metrics.json")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
