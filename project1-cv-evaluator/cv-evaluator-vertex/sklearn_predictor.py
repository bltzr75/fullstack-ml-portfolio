# sklearn_predictor.py - This works with sklearn container!
import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any

class SklearnPredictor:
    """Custom predictor that sklearn container can handle"""
    
    def __init__(self):
        self.loaded = False
        
    def load(self, model_path: str):
        """Load model configuration"""
        # Load the config
        with open(os.path.join(model_path, "model.pkl"), "rb") as f:
            self.config = pickle.load(f)
        
        # For now, just mark as loaded
        self.loaded = True
        print(f"✅ Model loaded: {self.config}")
    
    def predict(self, X: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Make predictions"""
        predictions = []
        
        for instance in X:
            cv_text = instance.get("cv_text", "")
            
            # Mock prediction for testing
            prediction = {
                "cv_preview": cv_text[:100] + "...",
                "total_score": 75,
                "recommendation": "hire",
                "technical_skills": 8,
                "experience_relevance": 7,
                "education_quality": 8,
                "processing_time_ms": 100,
                "model_config": self.config,
                "message": "Sklearn predictor working!"
            }
            predictions.append(prediction)
        
        return predictions

# Create global instance for sklearn container
_predictor = SklearnPredictor()

# Sklearn container entry points
def load(model_path):
    """Called by sklearn container"""
    _predictor.load(model_path)
    return _predictor

def predict(instances, **kwargs):
    """Called by sklearn container"""
    return _predictor.predict(instances, **kwargs)
