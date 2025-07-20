"""Metrics and evaluation utilities"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import Counter
import torch
from trl import GRPOTrainer


class MetricsGRPOTrainer(GRPOTrainer):
    """Enhanced GRPO Trainer with detailed metrics"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step_metrics = []
        self.detailed_logging = True
        self.actual_step_count = 0
    
    def log(self, logs, start_time=None):
        super().log(logs, start_time)
        
        if not self.detailed_logging:
            return
        
        # Get actual step number
        step = logs.get('step', self.actual_step_count)
        self.actual_step_count = max(self.actual_step_count, step)
        
        print(f"\n" + "="*70)
        print(f"📊 STEP {step} METRICS")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        print("="*70)
        
        # Progress bar
        progress = (step / self.args.max_steps) * 100 if self.args.max_steps > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * progress // 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"📈 Progress: [{bar}] {progress:.1f}% ({step}/{self.args.max_steps})")
        
        # Categorize metrics
        loss_metrics = {}
        reward_metrics = {}
        lr_metrics = {}
        
        for key, value in logs.items():
            if isinstance(value, (int, float)):
                if 'loss' in key.lower():
                    loss_metrics[key] = value
                elif 'reward' in key.lower():
                    reward_metrics[key] = value
                elif 'lr' in key.lower() or 'learning' in key.lower():
                    lr_metrics[key] = value
        
        # Display metrics
        if loss_metrics:
            print(f"\n📉 LOSS METRICS:")
            for key, value in loss_metrics.items():
                print(f"  {key}: {value:.6f}")
        
        if reward_metrics:
            print(f"\n🏆 REWARD METRICS:")
            for key, value in reward_metrics.items():
                print(f"  {key}: {value:.6f}")
            
            # Show reward summary
            total_rewards = sum(reward_metrics.values())
            avg_reward = total_rewards / len(reward_metrics) if reward_metrics else 0
            print(f"  📊 Average reward: {avg_reward:.3f}")
        
        if lr_metrics:
            print(f"\n📈 LEARNING RATE:")
            for key, value in lr_metrics.items():
                print(f"  {key}: {value:.2e}")
        
        # Memory monitoring
        if torch.cuda.is_available():
            memory_used = torch.cuda.memory_allocated(0) / 1024**3
            memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
            memory_pct = (memory_used / torch.cuda.get_device_properties(0).total_memory * 1024**3) * 100
            
            print(f"\n🔋 GPU MEMORY:")
            print(f"  Used: {memory_used:.1f}GB ({memory_pct:.1f}%)")
            print(f"  Reserved: {memory_reserved:.1f}GB")
        
        # Store metrics
        self.step_metrics.append({
            'step': step,
            'metrics': {k: v for k, v in logs.items() if isinstance(v, (int, float))},
            'timestamp': datetime.now().isoformat()
        })
        
        print("="*70)


def evaluate_hybrid_system(system, test_dataset, num_samples: int = 20) -> Dict[str, Any]:
    """Evaluate the hybrid CV evaluation system"""
    
    print(f"📊 Evaluating hybrid system on {num_samples} samples...")
    
    results = []
    processing_times = []
    criteria_coverage = []
    methods_used = []
    
    for i in range(min(num_samples, len(test_dataset))):
        sample = test_dataset[i]
        
        # Extract CV text
        cv_text = sample['prompt'].split("Evaluate this CV:")[-1].strip()
        
        # Evaluate
        result = system.evaluate_cv(cv_text)
        results.append(result)
        
        # Collect metrics
        if 'error' not in result:
            processing_times.append(result.get('processing_time_ms', 0))
            
            # Count criteria extracted
            criteria_found = len([k for k in result.keys() 
                                if k in system.config.evaluation_criteria])
            criteria_total = len(system.config.evaluation_criteria)
            criteria_coverage.append(criteria_found / criteria_total)
            
            methods_used.append(result.get('pipeline_method', 'unknown'))
    
    # Calculate summary metrics
    successful = sum(1 for r in results if 'error' not in r)
    success_rate = successful / len(results) if results else 0
    
    # Method distribution
    method_counter = Counter(methods_used)
    primary_method = method_counter.most_common(1)[0][0] if method_counter else 'unknown'
    
    metrics = {
        'total_samples': len(results),
        'successful': successful,
        'success_rate': success_rate,
        'avg_processing_time': sum(processing_times) / len(processing_times) if processing_times else 0,
        'avg_criteria_coverage': sum(criteria_coverage) / len(criteria_coverage) if criteria_coverage else 0,
        'primary_method': primary_method,
        'method_distribution': dict(method_counter),
        'detailed_results': results
    }
    
    return metrics


def calculate_criteria_coverage(result: Dict[str, Any], 
                              evaluation_criteria: Dict[str, str]) -> float:
    """Calculate the percentage of evaluation criteria covered"""
    
    if 'error' in result:
        return 0.0
    
    criteria_found = [k for k in result.keys() if k in evaluation_criteria]
    return len(criteria_found) / len(evaluation_criteria)
