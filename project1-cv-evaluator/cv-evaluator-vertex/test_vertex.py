# test_vertex.py
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
    print("❌ Error: ENDPOINT_ID not set in .env file")
    print("Run deploy.py first and add the endpoint ID to .env")
    exit(1)

# Initialize
print(f"🔧 Connecting to Vertex AI endpoint...")
print(f"   Project: {PROJECT_ID}")
print(f"   Region: {REGION}")
print(f"   Endpoint: {ENDPOINT_ID}")

aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint = aiplatform.Endpoint(ENDPOINT_ID)

# Test CV
test_cv = """
Sarah Johnson
Senior Software Engineer

Experience:
- 7 years at Microsoft, Amazon, Google
- Led teams of 12 engineers
- Built cloud services handling 5M requests/day

Education:
- MS Computer Science - Stanford

Skills: Python, AWS, Kubernetes, Docker
"""

# Make prediction
print("\n🔄 Sending request to Vertex AI...")
response = endpoint.predict(instances=[{"cv_text": test_cv}])

# Show results
prediction = response.predictions[0]
print("\n📝 MODEL A PROSE OUTPUT:")
print("-" * 60)
print(prediction["model_a_prose_output"])
print("-" * 60)

print("\n📊 EXTRACTION SUMMARY:")
print(f"Criteria found: {prediction['extraction_summary']['criteria_found']}/{prediction['extraction_summary']['total_criteria']}")

print("\n✅ FINAL EVALUATION:")
final_eval = prediction["final_evaluation"]
print(f"Total Score: {final_eval.get('total_score', 'N/A')}/100")
print(f"Recommendation: {final_eval.get('recommendation', 'N/A')}")

print("\n📊 Individual Scores:")
for criterion, score in final_eval.items():
    if criterion in ["technical_skills", "experience_relevance", "education_quality", 
                     "leadership_potential", "communication_skills", "problem_solving",
                     "innovation_mindset", "cultural_fit", "career_progression", 
                     "overall_impression"]:
        print(f"  • {criterion.replace('_', ' ').title()}: {score}/10")

print("\n⏱️ Processing time: {prediction.get('processing_time_ms', 'N/A')}ms")
