"""Training script for Model B (SFT)"""

import torch
import gc
from datetime import datetime
from datasets import Dataset, concatenate_datasets
from transformers import Trainer, TrainingArguments

from configs.hybrid_config import HybridSystemConfig
from configs.model_configs import ModelBConfig
from models.model_b_json.json_converter import JSONConverter
from models.model_b_json.training_utils import (
    prepare_model_b_dataset, 
    get_data_collator,
    create_synthetic_json_examples
)


def train_model_b(config: HybridSystemConfig, 
                 train_dataset: Dataset, 
                 val_dataset: Dataset) -> bool:
    """Train Model B with SFT for JSON conversion"""
    
    try:
        print("🚀 Initializing Model B training...")
        
        # Clear memory
        torch.cuda.empty_cache()
        gc.collect()
        
        # Initialize model
        model_b_config = ModelBConfig()
        json_converter = JSONConverter(model_b_config)
        
        # Load base model
        json_converter.load_base_model(cache_dir=config.cache_dir)
        
        # Setup LoRA
        json_converter.setup_lora()
        
        # Prepare datasets
        print("📊 Preparing datasets for Model B...")
        
        # Add synthetic examples for better JSON learning
        synthetic_examples = create_synthetic_json_examples(200)
        synthetic_dataset = Dataset.from_list(synthetic_examples)
        
        # Combine with training data
        combined_train = concatenate_datasets([train_dataset, synthetic_dataset])
        
        # Tokenize datasets
        tokenized_train = prepare_model_b_dataset(
            combined_train, 
            json_converter.tokenizer,
            model_b_config.max_seq_length
        )
        
        tokenized_val = prepare_model_b_dataset(
            val_dataset,
            json_converter.tokenizer,
            model_b_config.max_seq_length
        )
        
        # Set format for PyTorch
        tokenized_train.set_format("torch")
        tokenized_val.set_format("torch")
        
        # Data collator
        data_collator = get_data_collator(json_converter.tokenizer)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir="outputs/model_b",
            num_train_epochs=model_b_config.num_train_epochs,
            per_device_train_batch_size=model_b_config.per_device_train_batch_size,
            gradient_accumulation_steps=model_b_config.gradient_accumulation_steps,
            warmup_steps=model_b_config.warmup_steps,
            max_steps=config.model_b_training_steps,
            logging_steps=20,
            save_steps=100,
            save_total_limit=2,
            learning_rate=model_b_config.learning_rate,
            fp16=False,
            bf16=model_b_config.bf16,
            tf32=model_b_config.tf32,
            report_to="none",
            remove_unused_columns=False,
            dataloader_num_workers=model_b_config.dataloader_num_workers,
            dataloader_pin_memory=True,
            evaluation_strategy="steps",
            eval_steps=100,
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="loss",
        )
        
        # Create trainer
        trainer = Trainer(
            model=json_converter.model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=tokenized_val,
            processing_class=json_converter.tokenizer,
            data_collator=data_collator,
        )
        
        print("🏁 Starting Model B training...")
        print(f"📊 Training samples: {len(tokenized_train)}")
        print(f"📊 Validation samples: {len(tokenized_val)}")
        
        start_time = datetime.now()
        
        # Train
        trainer.train()
        
        end_time = datetime.now()
        print(f"✅ Model B training complete! Duration: {end_time - start_time}")
        
        # Save model
        json_converter.save_model("outputs/model_b_json_converter")
        
        # Quick test
        print("\n🧪 Testing Model B...")
        test_result = json_converter.convert_to_json(
            "Technical Skills: 8/10. Total Score: 75. Recommendation: hire",
            config.MODEL_B_SYSTEM_PROMPT
        )
        print(f"Test output: {test_result[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Model B training failed: {e}")
        import traceback
        traceback.print_exc()
        return False
