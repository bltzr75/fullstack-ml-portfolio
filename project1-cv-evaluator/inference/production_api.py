"""Production API for CV evaluation service"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import logging

from inference.hybrid_inference import HybridInference
from configs.hybrid_config import HybridSystemConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CV Evaluation API",
    description="Hybrid two-model system for CV evaluation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global inference instance
inference_system = None


class CVRequest(BaseModel):
    """Request model for CV evaluation"""
    cv_text: str = Field(..., description="CV text to evaluate")
    include_validation: bool = Field(default=False, description="Include validation results")


class BatchCVRequest(BaseModel):
    """Request model for batch CV evaluation"""
    cv_texts: List[str] = Field(..., description="List of CV texts to evaluate")
    include_validation: bool = Field(default=False, description="Include validation results")


class EvaluationResponse(BaseModel):
    """Response model for CV evaluation"""
    technical_skills: Optional[int] = None
    experience_relevance: Optional[int] = None
    education_quality: Optional[int] = None
    leadership_potential: Optional[int] = None
    communication_skills: Optional[int] = None
    problem_solving: Optional[int] = None
    innovation_mindset: Optional[int] = None
    cultural_fit: Optional[int] = None
    career_progression: Optional[int] = None
    overall_impression: Optional[int] = None
    total_score: Optional[int] = None
    recommendation: Optional[str] = None
    key_strengths: Optional[List[str]] = None
    areas_for_improvement: Optional[List[str]] = None
    processing_time_ms: Optional[int] = None
    pipeline_method: Optional[str] = None
    error: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the inference system on startup"""
    global inference_system
    
    logger.info("Initializing CV evaluation system...")
    
    try:
        config = HybridSystemConfig()
        inference_system = HybridInference(config)
        inference_system.load_models()
        logger.info("CV evaluation system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CV Evaluation API",
        "version": "1.0.0",
        "status": "ready" if inference_system and inference_system.system_loaded else "not_ready"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if inference_system and inference_system.system_loaded:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system_status": inference_system.get_system_status()
        }
    else:
        raise HTTPException(status_code=503, detail="System not ready")


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_cv(request: CVRequest):
    """Evaluate a single CV"""
    try:
        if request.include_validation:
            result = inference_system.evaluate_with_validation(request.cv_text)
        else:
            result = inference_system.evaluate_cv(request.cv_text)
        
        return EvaluationResponse(**result)
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate/batch", response_model=List[EvaluationResponse])
async def evaluate_batch(request: BatchCVRequest):
    """Evaluate multiple CVs"""
    try:
        results = inference_system.batch_evaluate(request.cv_texts)
        
        if request.include_validation:
            for result in results:
                validation = validate_evaluation_output(result, inference_system.config)
                result['validation'] = validation
        
        return [EvaluationResponse(**result) for result in results]
        
    except Exception as e:
        logger.error(f"Batch evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/criteria")
async def get_evaluation_criteria():
    """Get evaluation criteria information"""
    if inference_system:
        return {
            "criteria": inference_system.config.evaluation_criteria,
            "valid_recommendations": inference_system.config.valid_recommendations
        }
    else:
        raise HTTPException(status_code=503, detail="System not ready")


@app.post("/evaluate/async")
async def evaluate_cv_async(request: CVRequest, background_tasks: BackgroundTasks):
    """Evaluate CV asynchronously (returns job ID)"""
    # This would typically use a job queue like Celery
    # For now, just return a placeholder
    job_id = f"job_{datetime.now().timestamp()}"
    
    # In production, you would:
    # 1. Submit job to queue
    # 2. Return job ID
    # 3. Provide endpoint to check job status
    
    return {
        "job_id": job_id,
        "status": "submitted",
        "message": "CV evaluation job submitted"
    }


def main():
    """Run the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CV Evaluation API Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    uvicorn.run(
        "inference.production_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


if __name__ == "__main__":
    main()
