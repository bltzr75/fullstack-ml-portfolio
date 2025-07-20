# deploy_simple.py - Simplified deployment using custom predictor
import os
from dotenv import load_dotenv
from google.cloud import aiplatform

# Load environment variables
load_dotenv()

# Get configuration
PROJECT_ID = os.getenv('PROJECT_ID')
BUCKET_NAME = os.getenv('BUCKET_NAME')
REGION = os.getenv('REGION')
MODEL_DISPLAY_NAME = os.getenv('MODEL_DISPLAY_NAME')
ENDPOINT_DISPLAY_NAME = os.getenv('ENDPOINT_DISPLAY_NAME')
MACHINE_TYPE = os.getenv('MACHINE_TYPE')
MIN_REPLICA_COUNT = int(os.getenv('MIN_REPLICA_COUNT', '1'))
MAX_REPLICA_COUNT = int(os.getenv('MAX_REPLICA_COUNT', '1'))

# Initialize
print(f"🔧 Initializing Vertex AI...")
aiplatform.init(project=PROJECT_ID, location=REGION)

# Use sklearn container which is more flexible
SERVING_CONTAINER = "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"

print("\n📦 Creating model with custom predictor...")

# Create model without uploading artifacts (we'll handle it differently)
model = aiplatform.Model.upload(
    display_name=MODEL_DISPLAY_NAME,
    serving_container_image_uri=SERVING_CONTAINER,
    artifact_uri=f"gs://{BUCKET_NAME}/cv-evaluator/",
)

print(f"✅ Model created: {model.display_name}")

print("\n🔧 Creating endpoint...")
endpoint = aiplatform.Endpoint.create(display_name=ENDPOINT_DISPLAY_NAME)

print("\n🚀 Deploying model...")
model.deploy(
    endpoint=endpoint,
    deployed_model_display_name=os.getenv('DEPLOYED_MODEL_DISPLAY_NAME'),
    machine_type=MACHINE_TYPE,
    min_replica_count=MIN_REPLICA_COUNT,
    max_replica_count=MAX_REPLICA_COUNT,
    # No GPU for initial test
)

print(f"\n✅ Deployment complete!")
print(f"📌 Endpoint ID: {endpoint.name}")
print(f"ENDPOINT_ID={endpoint.name}")
