# custom_predictor.py
import os
import pickle
import numpy as np

class CvEvaluatorPredictor:
    def __init__(self):
        pass
    
    def predict(self, instances):
        """Simple predictor that returns mock results for testing"""
        predictions = []
        
        for instance in instances:
            cv_text = instance.get("cv_text", "")
            
            # Mock response for testing deployment
            prediction = {
                "cv_preview": cv_text[:100] + "...",
                "model_a_prose_output": "Technical Skills (score 8/10): Strong technical background...",
                "extraction_summary": {
                    "criteria_found": 10,
                    "total_criteria": 10,
                    "extraction_method": "direct_from_prose"
                },
                "final_evaluation": {
                    "technical_skills": 8,
                    "experience_relevance": 9,
                    "education_quality": 8,
                    "total_score": 75,
                    "recommendation": "hire",
                    "key_strengths": ["Strong technical skills", "Good experience"],
                    "areas_for_improvement": ["Leadership development"]
                }
            }
            predictions.append(prediction)
        
        return predictions

# Create and save the predictor
predictor = CvEvaluatorPredictor()
with open("model.pkl", "wb") as f:
    pickle.dump(predictor, f)

print("✅ Created custom predictor model.pkl")
