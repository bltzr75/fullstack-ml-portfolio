"""Training script for Model A (GRPO)"""

import torch
import gc
from datetime import datetime
from datasets import Dataset
from trl import GRPOConfig, GRPOTrainer

from configs.hybrid_config import HybridSystemConfig
from configs.model_configs import ModelAConfig
from models.model_a_prose.prose_evaluator import ProseEvaluator
from models.model_a_prose.reward_functions import MODEL_A_REWARD_FUNCTIONS
from utils.metrics import MetricsGRPOTrainer


def train_model_a(config: HybridSystemConfig, 
                 train_dataset: Dataset, 
                 val_dataset: Dataset) -> bool:
    """Train Model A with GRPO for prose evaluation"""
    
    try:
        print("🚀 Initializing Model A training...")
        
        # Clear memory
        torch.cuda.empty_cache()
        gc.collect()
        
        # Initialize model
        model_a_config = ModelAConfig()
        prose_evaluator = ProseEvaluator(model_a_config)
        
        # Load base model
        prose_evaluator.load_base_model(cache_dir=config.cache_dir)
        
        # Setup LoRA
        prose_evaluator.setup_lora()
        
        # Wrap reward functions for GRPO
        def create_grpo_wrapper(reward_func):
            def wrapped(*args, **kwargs):
                try:
                    completions = args[0] if args else kwargs.get('completions', [])
                    clean_kwargs = {k: v for k, v in kwargs.items() if k != 'completions'}
                    clean_kwargs['config'] = config  # Pass config to reward functions
                    return reward_func(completions, **clean_kwargs)
                except Exception as e:
                    print(f"❌ Reward error in {reward_func.__name__}: {e}")
                    return [1.0] * len(args[0] if args else [])
            wrapped.__name__ = f"grpo_{reward_func.__name__}"
            return wrapped
        
        grpo_reward_functions = [create_grpo_wrapper(f) for f in MODEL_A_REWARD_FUNCTIONS]
        
        # GRPO training configuration
        training_args = GRPOConfig(
            learning_rate=model_a_config.learning_rate,
            per_device_train_batch_size=model_a_config.per_device_train_batch_size,
            gradient_accumulation_steps=model_a_config.gradient_accumulation_steps,
            num_generations=model_a_config.num_generations,
            max_steps=config.model_a_training_steps,
            max_prompt_length=model_a_config.max_prompt_length,
            max_completion_length=model_a_config.max_completion_length,
            output_dir="outputs/model_a",
            logging_steps=1,
            save_steps=config.checkpoint_every,
            optim="paged_adamw_8bit",
            warmup_ratio=0.1,
            report_to="none",
            bf16=model_a_config.bf16,
            tf32=model_a_config.tf32,
            gradient_checkpointing=model_a_config.gradient_checkpointing,
            temperature=0.8,
            top_p=0.9,
        )
        
        # Test reward functions
        print("🧪 Testing reward functions...")
        test_prose = ["Technical Skills: 8/10. Total Score: 75. Recommendation: hire"]
        for func in grpo_reward_functions[:3]:
            rewards = func(test_prose)
            print(f"  ✅ {func.__name__}: {rewards}")
        
        # Create trainer
        trainer = MetricsGRPOTrainer(
            model=prose_evaluator.model,
            processing_class=prose_evaluator.tokenizer,
            reward_funcs=grpo_reward_functions,
            args=training_args,
            train_dataset=train_dataset,
        )
        
        print("🏁 Starting Model A GRPO training...")
        start_time = datetime.now()
        
        # Train
        trainer.train()
        
        end_time = datetime.now()
        print(f"✅ Model A training complete! Duration: {end_time - start_time}")
        
        # Save model
        prose_evaluator.save_model("outputs/model_a_prose_evaluator")
        
        return True
        
    except Exception as e:
        print(f"❌ Model A training failed: {e}")
        import traceback
        traceback.print_exc()
        return False
