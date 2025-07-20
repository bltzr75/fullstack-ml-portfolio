"""Dataset processor for hybrid two-model training"""

import os
import json
import random
import zipfile
from typing import Dict, List, Any, Tuple
from datasets import Dataset

from configs.hybrid_config import HybridSystemConfig, MODEL_A_SYSTEM_PROMPT, MODEL_B_SYSTEM_PROMPT
from .cv_generator import CVGenerator
from .ground_truth_generator import GroundTruthGenerator


class HybridDatasetProcessor:
    """Process datasets for both Model A and Model B training"""
    
    def __init__(self, config: HybridSystemConfig):
        self.config = config
        self.cv_generator = CVGenerator()
        self.ground_truth_generator = GroundTruthGenerator(config)
    
    def process_dataset(self, cv_dataset_path: str) -> Tuple[Dataset, Dataset, Dataset, Dataset]:
        """Process CV dataset for hybrid training"""
        
        # Extract if zip file
        if cv_dataset_path.endswith('.zip'):
            extract_path = cv_dataset_path.replace('.zip', '')
            with zipfile.ZipFile(cv_dataset_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            cv_dataset_path = extract_path
        
        # Load CV files
        cv_files = [f for f in os.listdir(cv_dataset_path) 
                   if f.startswith('cv_') and f.endswith('.txt')]
        
        print(f"📊 Processing {len(cv_files)} CV files for hybrid training...")
        
        model_a_samples = []  # Prose evaluation samples
        model_b_samples = []  # JSON conversion samples
        
        for i, cv_file in enumerate(cv_files):
            cv_path = os.path.join(cv_dataset_path, cv_file)
            with open(cv_path, 'r', encoding='utf-8') as f:
                cv_text = f.read()
            
            # Load persona data
            cv_number = cv_file.replace('cv_', '').replace('.txt', '')
            persona_path = os.path.join(cv_dataset_path, f'persona_{cv_number}.json')
            
            if os.path.exists(persona_path):
                with open(persona_path, 'r', encoding='utf-8') as f:
                    persona_data = json.load(f)
            else:
                # Generate default persona
                persona_data = self._generate_default_persona()
            
            # Generate ground truth (both JSON and prose)
            json_truth, prose_truth = self.ground_truth_generator.generate_ground_truth(
                persona_data.get('quality_tier', 'good'),
                persona_data.get('experience_level', 'mid'),
                persona_data.get('domain', 'data_science')
            )
            
            # Model A sample (CV → Prose)
            model_a_prompt = f"{MODEL_A_SYSTEM_PROMPT}\n\nEvaluate this CV:\n\n{cv_text}"
            
            model_a_samples.append({
                'prompt': model_a_prompt,
                'chosen': prose_truth,
                'ground_truth': json_truth,  # For accuracy reward
                'metadata': {
                    'quality': persona_data.get('quality_tier', 'good'),
                    'exp_level': persona_data.get('experience_level', 'mid'),
                    'domain': persona_data.get('domain', 'data_science')
                }
            })
            
            # Model B sample (Prose → JSON)
            model_b_prompt = f"{MODEL_B_SYSTEM_PROMPT}\n\nCV Evaluation:\n{prose_truth}\n\nJSON:"
            
            model_b_samples.append({
                'prompt': model_b_prompt,
                'completion': json.dumps(json_truth, indent=2),
                'metadata': persona_data
            })
            
            if (i + 1) % 100 == 0:
                print(f"  ✅ Processed {i + 1}/{len(cv_files)} CVs...")
        
        # Create datasets
        model_a_dataset = Dataset.from_list(model_a_samples)
        model_b_dataset = Dataset.from_list(model_b_samples)
        
        # Split into train/val
        train_size = int(len(model_a_dataset) * self.config.train_split)
        
        model_a_train = model_a_dataset.select(range(train_size))
        model_a_val = model_a_dataset.select(range(train_size, len(model_a_dataset)))
        
        model_b_train = model_b_dataset.select(range(train_size))
        model_b_val = model_b_dataset.select(range(train_size, len(model_b_dataset)))
        
        return model_a_train, model_a_val, model_b_train, model_b_val
    
    def _generate_default_persona(self) -> Dict[str, Any]:
        """Generate default persona if not found"""
        return {
            'quality_tier': random.choice(['excellent', 'good', 'average']),
            'experience_level': random.choice(['entry', 'mid', 'senior']),
            'domain': random.choice(['data_science', 'software_engineering', 'marketing', 'finance'])
        }
    
    def create_synthetic_examples(self, num_examples: int = 200) -> List[Dict[str, Any]]:
        """Create synthetic examples for Model B training"""
        synthetic_examples = []
        
        for _ in range(num_examples):
            # Generate random scores
            scores = {k: random.randint(4, 9) 
                     for k in self.config.evaluation_criteria.keys()}
            total = sum(scores.values())
            
            # Create prose
            prose = self._create_prose_from_scores(scores, total)
            
            # Create JSON
            json_obj = {
                **scores,
                "total_score": total,
                "recommendation": self._get_recommendation(total),
                "key_strengths": ["Strong technical skills", "Good experience"],
                "areas_for_improvement": ["Leadership development needed"],
                "processing_time_ms": random.randint(500, 2000)
            }
            
            json_str = json.dumps(json_obj, indent=2)
            text = f"Convert to JSON:\n{prose}\n\nJSON:\n{json_str}"
            
            synthetic_examples.append({"text": text})
        
        return synthetic_examples
    
    def _create_prose_from_scores(self, scores: Dict[str, int], total: int) -> str:
        """Create prose evaluation from scores"""
        prose_parts = []
        
        for criterion, score in scores.items():
            criterion_text = criterion.replace('_', ' ').title()
            prose_parts.append(f"{criterion_text}: {score}/10.")
        
        prose_parts.append(f"Total Score: {total}.")
        prose_parts.append(f"Recommendation: {self._get_recommendation(total)}")
        
        return " ".join(prose_parts)
    
    def _get_recommendation(self, total_score: int) -> str:
        """Get recommendation based on total score"""
        if total_score >= 85:
            return 'strong_hire'
        elif total_score >= 70:
            return 'hire'
        elif total_score >= 55:
            return 'lean_hire'
        elif total_score >= 40:
            return 'no_hire'
        else:
            return 'strong_no_hire'
