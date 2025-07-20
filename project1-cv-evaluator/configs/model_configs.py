"""Individual model configurations"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ModelAConfig:
    """Configuration for Model A (Prose Evaluator)"""
    model_name: str = "NousResearch/Hermes-2-Pro-Mistral-7B"
    lora_rank: int = 64
    lora_alpha: int = 64
    lora_dropout: float = 0.1
    target_modules: List[str] = None
    max_seq_length: int = 2048
    
    # GRPO specific
    learning_rate: float = 1e-5
    per_device_train_batch_size: int = 8
    gradient_accumulation_steps: int = 2
    num_generations: int = 4
    max_prompt_length: int = 512
    max_completion_length: int = 512
    
    # A100 optimizations
    bf16: bool = True
    tf32: bool = True
    gradient_checkpointing: bool = True
    
    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]

@dataclass
class ModelBConfig:
    """Configuration for Model B (JSON Converter)"""
    model_name: str = "gpt2"
    lora_rank: int = 32
    lora_alpha: int = 64
    lora_dropout: float = 0.05
    target_modules: List[str] = None
    max_seq_length: int = 1024
    
    # Training specific
    learning_rate: float = 2e-4
    per_device_train_batch_size: int = 16
    gradient_accumulation_steps: int = 1
    num_train_epochs: int = 3
    warmup_steps: int = 100
    
    # Optimizations
    bf16: bool = True
    tf32: bool = True
    dataloader_num_workers: int = 4
    
    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["c_attn", "c_proj"]
