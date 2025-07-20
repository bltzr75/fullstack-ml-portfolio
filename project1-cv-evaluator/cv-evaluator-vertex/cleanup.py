# cleanup.py
import os
from dotenv import load_dotenv
from google.cloud import aiplatform

# Load environment variables
load_dotenv()

# Get configuration
ENDPOINT_ID = os.getenv('ENDPOINT_ID')
PROJECT_ID = os.getenv('PROJECT_ID')
REGION = os.getenv('REGION')

if not ENDPOINT_ID:
    print("❌ No ENDPOINT_ID in .env - nothing to clean up")
    exit(0)

# Initialize
aiplatform.init(project=PROJECT_ID, location=REGION)

print("🗑️ Cleaning up Vertex AI resources...")

try:
    # Get endpoint
    endpoint = aiplatform.Endpoint(ENDPOINT_ID)
    
    # Undeploy all models
    print("📤 Undeploying models...")
    endpoint.undeploy_all()
    
    # Delete endpoint
    print("🗑️ Deleting endpoint...")
    endpoint.delete()
    
    print("✅ Cleanup complete!")
    print("\n⚠️  Remember to remove ENDPOINT_ID from .env")
    
except Exception as e:
    print(f"❌ Error during cleanup: {e}")
