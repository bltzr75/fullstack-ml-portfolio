# proper_sklearn_deploy.py
import os
import pickle
import joblib
from sklearn.base import BaseEstimator
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

# 1. Create a proper sklearn estimator
class SimplePredictor(BaseEstimator):
    def fit(self, X, y=None):
        return self
    
    def predict(self, X):
        # X will be the instances from the request
        return [{"score": 75, "recommendation": "hire"} for _ in X]

# 2. Save with joblib (sklearn preferred)
model = SimplePredictor()
joblib.dump(model, "model.joblib")

# 3. Create the exact predictor format sklearn expects
predictor_py = '''
import joblib
import json

def predict(instances, **kwargs):
    model = joblib.load("model.joblib")
    predictions = model.predict(instances)
    return predictions
'''

with open("predictor.py", "w") as f:
    f.write(predictor_py)

# 4. Upload both files
BUCKET = os.getenv('BUCKET_NAME')
os.system(f"gsutil cp model.joblib gs://{BUCKET}/sklearn-proper/")
os.system(f"gsutil cp predictor.py gs://{BUCKET}/sklearn-proper/")

print("✅ Files uploaded. Now deploying...")

# 5. Deploy
aiplatform.init(
    project=os.getenv('PROJECT_ID'),
    location=os.getenv('REGION')
)

# First, clean up the hanging deployment
print("🧹 Cleaning up hanging deployments...")
os.system("gcloud ai endpoints delete 5519509888528547840 --region=us-central1 --quiet || true")

# Deploy fresh
model = aiplatform.Model.upload(
    display_name="sklearn-proper-test",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest",
    artifact_uri=f"gs://{BUCKET}/sklearn-proper/",
)

endpoint = aiplatform.Endpoint.create(display_name="sklearn-proper-endpoint")

model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=1,
    sync=False  # Don't wait
)

print(f"✅ Deploying to: {endpoint.resource_name}")
print("Check status in 2-3 minutes")
