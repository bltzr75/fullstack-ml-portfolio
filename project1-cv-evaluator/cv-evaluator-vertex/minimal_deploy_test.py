# minimal_deploy_test.py
import os
import pickle
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv()

# 1. Create minimal predictor
predictor_code = '''
def predict(instances, **kwargs):
    """Minimal predictor that works with sklearn container"""
    return [{"score": 75, "status": "working"} for _ in instances]
'''

with open("predictor.py", "w") as f:
    f.write(predictor_code)

# 2. Create simple model.pkl (just config, no classes)
model_config = {"type": "test", "version": "1.0"}
with open("model.pkl", "wb") as f:
    pickle.dump(model_config, f)

# 3. Upload files
BUCKET = os.getenv('BUCKET_NAME')
os.system(f"gsutil cp model.pkl gs://{BUCKET}/test-deploy/")
os.system(f"gsutil cp predictor.py gs://{BUCKET}/test-deploy/")

# 4. Deploy
aiplatform.init(
    project=os.getenv('PROJECT_ID'),
    location=os.getenv('REGION')
)

model = aiplatform.Model.upload(
    display_name="test-minimal",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest",
    artifact_uri=f"gs://{BUCKET}/test-deploy/",
)

endpoint = aiplatform.Endpoint.create(display_name="test-endpoint")

model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=1,
)

print(f"✅ Test endpoint: {endpoint.resource_name}")
