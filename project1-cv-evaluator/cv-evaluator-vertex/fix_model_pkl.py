# fix_model_pkl.py
import pickle
import json

# Instead of pickling the class, pickle just the configuration
model_config = {
    "model_type": "cv_evaluator",
    "version": "1.0",
    "model_a_path": "model_files/model_a_prose_evaluator",
    "model_b_path": "model_files/model_b_json_converter",
    "base_model_a": "NousResearch/Hermes-2-Pro-Mistral-7B",
    "base_model_b": "gpt2"
}

# Save configuration only
with open("model.pkl", "wb") as f:
    pickle.dump(model_config, f)

print("✅ Created model.pkl with config only")

# Upload fixed model.pkl
import os
os.system("gsutil cp model.pkl gs://cv-evaluator-bucket/cv-evaluator/")
