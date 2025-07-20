# deploy.py (UPDATED VERSION)
import os
from dotenv import load_dotenv
from google.cloud import aiplatform

# Load environment variables
load_dotenv()

# Get configuration from .env
PROJECT_ID = os.getenv('PROJECT_ID')
BUCKET_NAME = os.getenv('BUCKET_NAME')
REGION = os.getenv('REGION')
MODEL_DISPLAY_NAME = os.getenv('MODEL_DISPLAY_NAME')
ENDPOINT_DISPLAY_NAME = os.getenv('ENDPOINT_DISPLAY_NAME')
DEPLOYED_MODEL_DISPLAY_NAME = os.getenv('DEPLOYED_MODEL_DISPLAY_NAME')
MACHINE_TYPE = os.getenv('MACHINE_TYPE')
ACCELERATOR_TYPE = os.getenv('ACCELERATOR_TYPE')
ACCELERATOR_COUNT = int(os.getenv('ACCELERATOR_COUNT', '1'))
MIN_REPLICA_COUNT = int(os.getenv('MIN_REPLICA_COUNT', '0'))
MAX_REPLICA_COUNT = int(os.getenv('MAX_REPLICA_COUNT', '1'))

# Initialize
print(f"🔧 Initializing Vertex AI...")
print(f"   Project: {PROJECT_ID}")
print(f"   Region: {REGION}")
print(f"   Bucket: {BUCKET_NAME}")

aiplatform.init(project=PROJECT_ID, location=REGION)

# First, clean up the bucket and re-upload with correct structure
print("\n🧹 Cleaning up bucket...")
os.system(f"gsutil -m rm -r gs://{BUCKET_NAME}/cv-evaluator/* || true")

print("\n📤 Uploading model files with correct structure...")
# Create a temporary directory with the right structure
os.system("mkdir -p temp_upload")
os.system("cp predictor.py temp_upload/")
os.system("cp requirements.txt temp_upload/")
os.system("cp -r model_files temp_upload/")

# Upload only what's needed
upload_cmd = f"gsutil -m cp -r temp_upload/* gs://{BUCKET_NAME}/cv-evaluator/"
print(f"   Running: {upload_cmd}")
os.system(upload_cmd)

# Clean up temp directory
os.system("rm -rf temp_upload")

print("\n📦 Creating model in Vertex AI...")

# Use custom container for serving
CUSTOM_CONTAINER = "us-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-12:latest"

# For custom prediction code, we need to use LocalModel first
from google.cloud.aiplatform.prediction import LocalModel

# Create a local model with custom predictor
local_model = LocalModel(
    serving_container_image_uri=CUSTOM_CONTAINER,
    serving_container_predict_route="/predict",
    serving_container_health_route="/health",
    serving_container_environment_variables={
        "MODEL_NAME": "cv-evaluator",
    }
)

# Upload with custom prediction code
model = aiplatform.Model.upload(
    display_name=MODEL_DISPLAY_NAME,
    serving_container_image_uri=CUSTOM_CONTAINER,
    artifact_uri=f"gs://{BUCKET_NAME}/cv-evaluator/",
    serving_container_predict_route="/predict",
    serving_container_health_route="/health",
    serving_container_environment_variables={
        "PYTHONPATH": "/opt/python/lib/python3.10/site-packages:/mnt/models",
        "MODEL_NAME": "cv-evaluator",
    },
)

print(f"✅ Model created: {model.display_name}")

print("\n🔧 Creating endpoint...")
endpoint = aiplatform.Endpoint.create(display_name=ENDPOINT_DISPLAY_NAME)
print(f"✅ Endpoint created: {endpoint.display_name}")

print("\n🚀 Deploying model...")
print(f"   Machine type: {MACHINE_TYPE}")
print(f"   Accelerator: {ACCELERATOR_TYPE} x{ACCELERATOR_COUNT}")
print(f"   Replicas: {MIN_REPLICA_COUNT}-{MAX_REPLICA_COUNT}")

model.deploy(
    endpoint=endpoint,
    deployed_model_display_name=DEPLOYED_MODEL_DISPLAY_NAME,
    machine_type=MACHINE_TYPE,
    accelerator_type=ACCELERATOR_TYPE,
    accelerator_count=ACCELERATOR_COUNT,
    min_replica_count=MIN_REPLICA_COUNT,
    max_replica_count=MAX_REPLICA_COUNT,
)

print(f"\n✅ Deployment complete!")
print(f"📌 Endpoint ID: {endpoint.name}")
print(f"\n⚠️  Add this to your .env file:")
print(f"ENDPOINT_ID={endpoint.name}")
