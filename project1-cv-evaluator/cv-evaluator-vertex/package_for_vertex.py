# package_for_vertex.py
import pickle
import os

# Create a dummy model object that Vertex AI will accept
dummy_model = {
    "model_type": "cv_evaluator",
    "version": "1.0",
    "description": "This is a placeholder. Actual model loading happens in predictor.py"
}

# Save as model.pkl
with open("model.pkl", "wb") as f:
    pickle.dump(dummy_model, f)

print("✅ Created model.pkl")

# Upload to GCS
os.system("gsutil cp model.pkl gs://cv-evaluator-bucket/cv-evaluator/")
print("✅ Uploaded model.pkl to GCS")

# Also ensure predictor.py and requirements.txt are there
os.system("gsutil cp predictor.py gs://cv-evaluator-bucket/cv-evaluator/")
os.system("gsutil cp requirements.txt gs://cv-evaluator-bucket/cv-evaluator/")
os.system("gsutil -m cp -r model_files gs://cv-evaluator-bucket/cv-evaluator/")

print("✅ All files uploaded")
