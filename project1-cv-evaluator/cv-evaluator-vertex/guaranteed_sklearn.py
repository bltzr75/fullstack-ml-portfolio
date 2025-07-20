# guaranteed_sklearn.py
import pickle
from sklearn import datasets
from sklearn.ensemble import RandomForestClassifier
from google.cloud import aiplatform
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Create a REAL sklearn model
iris = datasets.load_iris()
model = RandomForestClassifier()
model.fit(iris.data, iris.target)

# 2. Save it (no custom predictor needed!)
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

# 3. Upload ONLY the model
BUCKET = os.getenv('BUCKET_NAME')
os.system(f"gsutil cp model.pkl gs://{BUCKET}/sklearn-iris/")

# 4. Deploy (no predictor.py needed)
aiplatform.init(
    project=os.getenv('PROJECT_ID'),
    location=os.getenv('REGION')
)

model = aiplatform.Model.upload(
    display_name="sklearn-iris-test",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest",
    artifact_uri=f"gs://{BUCKET}/sklearn-iris/",
)

endpoint = aiplatform.Endpoint.create(display_name="sklearn-iris-endpoint")

deployment = model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-2",
    min_replica_count=1,
    max_replica_count=1,
)

print(f"✅ Deployed: {endpoint.resource_name}")

# 5. Test it
test_instance = [[5.1, 3.5, 1.4, 0.2]]  # Iris data format
prediction = endpoint.predict(instances=test_instance)
print(f"✅ Prediction: {prediction.predictions}")
