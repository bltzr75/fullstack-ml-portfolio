"""Prose evaluator model (Model A)"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from typing import Optional, Dict, Any

from configs.model_configs import ModelAConfig


class ProseEvaluator:
    """Model A: Generates prose evaluations of CVs"""
    
    def __init__(self, config: ModelAConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        
    def load_base_model(self, cache_dir: Optional[str] = None):
        """Load base model and tokenizer"""
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            cache_dir=cache_dir
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            cache_dir=cache_dir,
            load_in_4bit=True,
            trust_remote_code=True
        )
        
        # Setup padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.eos_token_id
    
    def setup_lora(self):
        """Setup LoRA adapters"""
        
        lora_config = LoraConfig(
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        
        print(f"Trainable params: {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")
        print(f"Total params: {total_params:,}")
    
    def generate_evaluation(self, cv_text: str, system_prompt: str) -> str:
        """Generate prose evaluation for a CV"""
        
        prompt = f"{system_prompt}\n\nEvaluate this CV:\n\n{cv_text}"
        
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_seq_length
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_completion_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        evaluation = self.tokenizer.decode(
            outputs[0][len(inputs["input_ids"][0]):],
            skip_special_tokens=True
        )
        
        return evaluation
    
    def save_model(self, path: str):
        """Save model and tokenizer"""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
    
    def load_trained_model(self, path: str):
        """Load trained model"""
        # This would load the trained LoRA weights
        pass

