"""Hybrid CV Evaluation System combining Model A and Model B"""

import json
import re
import torch
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM, GPT2LMHeadModel, GPT2Tokenizer

from configs.hybrid_config import HybridSystemConfig, MODEL_A_SYSTEM_PROMPT, MODEL_B_SYSTEM_PROMPT
from utils.extraction import extract_json_from_prose_improved
from utils.validation import validate_evaluation_output


class HybridCVEvaluationSystem:
    """Production-ready hybrid CV evaluation system"""
    
    def __init__(self, config: HybridSystemConfig):
        self.config = config
        self.model_a = None
        self.tokenizer_a = None
        self.model_b = None
        self.tokenizer_b = None
        self.system_ready = False
        
    def load_models(self, model_a_path: Optional[str] = None, model_b_path: Optional[str] = None):
        """Load both models for the hybrid system"""
        try:
            # Load Model A (Prose Evaluator)
            model_a_path = model_a_path or self.config.model_a_name
            self.tokenizer_a = AutoTokenizer.from_pretrained(
                model_a_path, 
                cache_dir=self.config.cache_dir
            )
            self.model_a = AutoModelForCausalLM.from_pretrained(
                model_a_path,
                device_map="auto",
                torch_dtype=torch.float16,
                cache_dir=self.config.cache_dir,
                trust_remote_code=True
            )
            
            if self.tokenizer_a.pad_token is None:
                self.tokenizer_a.pad_token = self.tokenizer_a.eos_token
            
            # Load Model B (JSON Converter)
            model_b_path = model_b_path or self.config.model_b_name
            self.tokenizer_b = GPT2Tokenizer.from_pretrained(
                model_b_path,
                cache_dir=self.config.cache_dir
            )
            self.model_b = GPT2LMHeadModel.from_pretrained(
                model_b_path,
                device_map="auto",
                torch_dtype=torch.float16,
                cache_dir=self.config.cache_dir
            )
            
            self.tokenizer_b.pad_token = self.tokenizer_b.eos_token
            
            self.system_ready = True
            print("✅ Hybrid system loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            raise
    
    def evaluate_cv(self, cv_text: str) -> Dict[str, Any]:
        """Evaluate a CV using the hybrid two-stage approach"""
        if not self.system_ready:
            return {"error": "System not properly initialized"}
        
        start_time = datetime.now()
        
        try:
            # Stage 1: Generate prose evaluation with Model A
            prose_evaluation = self._generate_prose_evaluation(cv_text)
            
            # Try direct extraction first
            extracted_json = extract_json_from_prose_improved(
                prose_evaluation, 
                self.config.evaluation_criteria
            )
            
            # Check if extraction is sufficient
            if self._is_extraction_complete(extracted_json):
                extracted_json['processing_time_ms'] = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                extracted_json['pipeline_method'] = 'direct_extraction'
                return extracted_json
            
            # Stage 2: Use Model B for JSON conversion if needed
            json_output = self._convert_to_json(prose_evaluation)
            
            if json_output and 'error' not in json_output:
                json_output['processing_time_ms'] = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                json_output['pipeline_method'] = 'model_b_generation'
                return json_output
            
            # Fallback: Return partial extraction with defaults
            return self._create_fallback_response(extracted_json, prose_evaluation, start_time)
            
        except Exception as e:
            return {
                'error': f'Pipeline failed: {str(e)}',
                'processing_time_ms': int((datetime.now() - start_time).total_seconds() * 1000)
            }
    
    def _generate_prose_evaluation(self, cv_text: str) -> str:
        """Generate prose evaluation using Model A"""
        prompt = f"{MODEL_A_SYSTEM_PROMPT}\n\nEvaluate this CV:\n\n{cv_text}"
        
        inputs = self.tokenizer_a(
            prompt, 
            return_tensors="pt", 
            truncation=True, 
            max_length=self.config.model_a_max_seq_length
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model_a.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer_a.eos_token_id,
            )
        
        prose_evaluation = self.tokenizer_a.decode(
            outputs[0][len(inputs["input_ids"][0]):],
            skip_special_tokens=True
        )
        
        return prose_evaluation
    
    def _convert_to_json(self, prose_evaluation: str) -> Optional[Dict[str, Any]]:
        """Convert prose to JSON using Model B"""
        few_shot_prompt = """Convert CV evaluations to JSON format.

Example:
Evaluation: Technical Skills: 8/10. Experience Relevance: 7/10. Total Score: 75. Recommendation: hire
JSON: {"technical_skills": 8, "experience_relevance": 7, "total_score": 75, "recommendation": "hire"}

Now convert:
Evaluation: %s
JSON:"""
        
        prose_cleaned = prose_evaluation.replace('{', '').replace('}', '').replace('"', '')[:500]
        model_b_input = few_shot_prompt % prose_cleaned
        
        inputs = self.tokenizer_b(
            model_b_input, 
            return_tensors="pt", 
            truncation=True, 
            max_length=self.config.model_b_max_seq_length
        )
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model_b.generate(
                **inputs,
                max_new_tokens=300,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer_b.eos_token_id,
            )
        
        full_output = self.tokenizer_b.decode(outputs[0], skip_special_tokens=True)
        json_output = full_output.split("JSON:")[-1].strip()
        
        try:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', json_output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except:
            pass
        
        return None
    
    def _is_extraction_complete(self, extracted_json: Dict[str, Any]) -> bool:
        """Check if extraction has sufficient fields"""
        required_fields = len([k for k in extracted_json.keys() 
                             if k in self.config.evaluation_criteria])
        return required_fields >= 5 and 'total_score' in extracted_json
    
    def _create_fallback_response(self, 
                                 extracted_json: Dict[str, Any], 
                                 prose_evaluation: str,
                                 start_time: datetime) -> Dict[str, Any]:
        """Create fallback response with defaults"""
        # Fill missing criteria with default scores
        for criterion in self.config.evaluation_criteria.keys():
            if criterion not in extracted_json:
                extracted_json[criterion] = 5  # Default middle score
        
        # Calculate total if missing
        if 'total_score' not in extracted_json:
            extracted_json['total_score'] = sum(
                extracted_json.get(k, 5) for k in self.config.evaluation_criteria.keys()
            )
        
        # Set recommendation if missing
        if 'recommendation' not in extracted_json:
            total = extracted_json.get('total_score', 50)
            if total >= 85:
                extracted_json['recommendation'] = 'strong_hire'
            elif total >= 70:
                extracted_json['recommendation'] = 'hire'
            elif total >= 50:
                extracted_json['recommendation'] = 'lean_hire'
            else:
                extracted_json['recommendation'] = 'no_hire'
        
        # Add default strengths/improvements if missing
        if 'key_strengths' not in extracted_json:
            extracted_json['key_strengths'] = ["Professional experience", "Educational background"]
        if 'areas_for_improvement' not in extracted_json:
            extracted_json['areas_for_improvement'] = ["Could expand skill set"]
        
        extracted_json['processing_time_ms'] = int(
            (datetime.now() - start_time).total_seconds() * 1000
        )
        extracted_json['pipeline_method'] = 'partial_extraction'
        
        return extracted_json
    
    def batch_evaluate(self, cv_texts: List[str]) -> List[Dict[str, Any]]:
        """Evaluate multiple CVs"""
        results = []
        for i, cv_text in enumerate(cv_texts):
            print(f"Evaluating CV {i+1}/{len(cv_texts)}...")
            results.append(self.evaluate_cv(cv_text))
        return results
    
    def get_evaluation_summary(self, result: Dict[str, Any]) -> str:
        """Generate a human-readable summary"""
        if "error" in result:
            return f"Evaluation failed: {result['error']}"
        
        summary = []
        summary.append(f"Total Score: {result.get('total_score', 'N/A')}/100")
        summary.append(f"Recommendation: {result.get('recommendation', 'N/A')}")
        
        # Show top strengths
        criteria_scores = [(k, v) for k, v in result.items()
                          if k in self.config.evaluation_criteria and isinstance(v, (int, float))]
        if criteria_scores:
            top_criteria = sorted(criteria_scores, key=lambda x: x[1], reverse=True)[:3]
            summary.append("\nTop Strengths:")
            for criterion, score in top_criteria:
                summary.append(f"  - {criterion.replace('_', ' ').title()}: {score}/10")
        
        return "\n".join(summary)
