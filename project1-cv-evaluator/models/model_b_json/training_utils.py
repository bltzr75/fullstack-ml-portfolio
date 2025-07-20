"""Training utilities for Model B"""

from typing import List, Dict, Any
from datasets import Dataset
from transformers import DataCollatorForLanguageModeling


def prepare_model_b_dataset(dataset: Dataset, tokenizer, max_length: int = 512) -> Dataset:
    """Prepare dataset for Model B training"""
    
    def format_for_gpt(example):
        """Format examples for GPT2 training"""
        text = f"{example['prompt']}\n{example['completion']}"
        return {"text": text}
    
    def tokenize_function(examples):
        """Tokenize examples"""
        model_inputs = tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=max_length
        )
        model_inputs["labels"] = model_inputs["input_ids"].copy()
        return model_inputs
    
    # Format dataset
    formatted_dataset = dataset.map(format_for_gpt)
    
    # Tokenize
    tokenized_dataset = formatted_dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=formatted_dataset.column_names
    )
    
    return tokenized_dataset


def get_data_collator(tokenizer):
    """Get data collator for language modeling"""
    return DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # GPT2 is not a masked LM
        pad_to_multiple_of=8
    )


def create_synthetic_json_examples(num_examples: int = 200) -> List[Dict[str, str]]:
    """Create synthetic examples for JSON training"""
    import random
    
    examples = []
    
    for _ in range(num_examples):
        # Generate random scores
        scores = {
            'technical_skills': random.randint(4, 9),
            'experience_relevance': random.randint(4, 9),
            'education_quality': random.randint(4, 9),
            'leadership_potential': random.randint(4, 9),
            'communication_skills': random.randint(4, 9),
            'problem_solving': random.randint(4, 9),
            'innovation_mindset': random.randint(4, 9),
            'cultural_fit': random.randint(4, 9),
            'career_progression': random.randint(4, 9),
            'overall_impression': random.randint(4, 9)
        }
        
        total = sum(scores.values())
        
        # Create prose
        prose_parts = []
        for criterion, score in scores.items():
            criterion_text = criterion.replace('_', ' ').title()
            prose_parts.append(f"{criterion_text}: {score}/10.")
        
        prose_parts.append(f"Total Score: {total}.")
        
        # Determine recommendation
        if total >= 85:
            rec = 'strong_hire'
        elif total >= 70:
            rec = 'hire'
        elif total >= 55:
            rec = 'lean_hire'
        else:
            rec = 'no_hire'
        
        prose_parts.append(f"Recommendation: {rec}")
        prose = " ".join(prose_parts)
        
        # Create JSON
        import json
        json_obj = {
            **scores,
            "total_score": total,
            "recommendation": rec,
            "key_strengths": ["Strong technical skills", "Good experience"],
            "areas_for_improvement": ["Leadership development needed"],
            "processing_time_ms": random.randint(500, 2000)
        }
        
        json_str = json.dumps(json_obj, indent=2)
        
        # Create training example
        text = f"Convert to JSON:\n{prose}\n\nJSON:\n{json_str}"
        examples.append({"text": text})
    
    return examples
