"""JSON converter model (Model B)"""

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from peft import LoraConfig, get_peft_model, TaskType
from typing import Optional, Dict, Any

from configs.model_configs import ModelBConfig


class JSONConverter:
    """Model B: Converts prose evaluations to JSON format"""
    
    def __init__(self, config: ModelBConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        
    def load_base_model(self, cache_dir: Optional[str] = None):
        """Load base GPT2 model and tokenizer"""
        
        self.tokenizer = GPT2Tokenizer.from_pretrained(
            self.config.model_name,
            cache_dir=cache_dir
        )
        
        self.model = GPT2LMHeadModel.from_pretrained(
            self.config.model_name,
            device_map="auto",
            torch_dtype=torch.float16,
            cache_dir=cache_dir
        )
        
        # Add padding token for GPT2
        self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def setup_lora(self):
        """Setup LoRA adapters for GPT2"""
        
        lora_config = LoraConfig(
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
        
        self.model = get_peft_model(self.model, lora_config)
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        
        print(f"Trainable params: {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")
        print(f"Total params: {total_params:,}")
    
    def convert_to_json(self, prose_evaluation: str, system_prompt: str) -> str:
        """Convert prose evaluation to JSON format"""
        
        # Use few-shot prompt for better results
        few_shot_prompt = f"""{system_prompt}

Example:
Evaluation: Technical Skills: 8/10. Experience Relevance: 7/10. Total Score: 75. Recommendation: hire
JSON: {{"technical_skills": 8, "experience_relevance": 7, "total_score": 75, "recommendation": "hire"}}

Now convert:
Evaluation: {prose_evaluation[:500]}
JSON:"""
        
        inputs = self.tokenizer(
            few_shot_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_seq_length
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=300,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        json_output = full_output.split("JSON:")[-1].strip()
        
        return json_output
    
    def save_model(self, path: str):
        """Save model and tokenizer"""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
