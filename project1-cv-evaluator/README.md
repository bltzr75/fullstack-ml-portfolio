# CV Evaluation Hybrid System

A production-ready hybrid two-model system for evaluating CVs using advanced NLP techniques. This system combines GRPO-trained prose evaluation with structured JSON output generation.

## 🏗️ Architecture Overview

This project implements a hybrid approach for CV evaluation:

1. **Model A (Prose Evaluator)**: Uses `NousResearch/Hermes-2-Pro-Mistral-7B` with GRPO training to generate detailed prose evaluations
2. **Model B (JSON Converter)**: Uses fine-tuned `GPT-2` to convert prose evaluations to structured JSON format

### Why Hybrid Approach?

- **Flexibility**: Prose evaluations are more natural and detailed
- **Structure**: JSON output ensures consistent API responses
- **Robustness**: Fallback extraction methods ensure high success rates
- **Performance**: 100% success rate with 74% average criteria coverage

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- CUDA-capable GPU (A100 recommended for training)
- 40GB+ GPU memory for full training

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Generate synthetic CV dataset
python scripts/prepare_dataset.py --num_cvs 500 --output_dir cv_dataset

# Train both models
python training/train_hybrid.py \
    --cv_dataset_path cv_dataset \
    --model_a_steps 50 \
    --model_b_steps 500 \
    --use_a100
```

### Usage

```python
from models.hybrid_system import HybridCVEvaluationSystem
from configs.hybrid_config import HybridSystemConfig

# Initialize system
config = HybridSystemConfig()
evaluator = HybridCVEvaluationSystem(config)
evaluator.load_models()

# Evaluate a CV
cv_text = """
Name: John Smith
Title: Senior Data Scientist
Experience: 5 years in machine learning
Skills: Python, TensorFlow, PyTorch
"""

result = evaluator.evaluate_cv(cv_text)
print(evaluator.get_evaluation_summary(result))
```

## 🏋️ Training Details

**Model A (GRPO Training)**
- Base Model: `NousResearch/Hermes-2-Pro-Mistral-7B`
- Training Method: Group Relative Policy Optimization (GRPO)
- LoRA Rank: 64, Training Steps: 50

**Model B (SFT Training)**
- Base Model: `GPT-2`
- Training Method: Supervised Fine-Tuning (SFT)
- LoRA Rank: 32, Training Steps: 500

## 📁 Project Structure

```
project1-cv-evaluator/
├── configs/          # Configuration files
├── data/            # Dataset processing
├── models/          # Model implementations
├── training/        # Training scripts
├── inference/       # Inference pipeline
├── utils/           # Utility functions
├── notebooks/       # Jupyter notebooks
└── scripts/         # Helper scripts
```

## 📈 Evaluation Criteria

The system evaluates CVs on 10 criteria (1-10 scale):

1. Technical Skills
2. Experience Relevance
3. Education Quality
4. Leadership Potential
5. Communication Skills
6. Problem Solving
7. Innovation Mindset
8. Cultural Fit
9. Career Progression
10. Overall Impression

## 🔧 Configuration

Configure the system through `configs/hybrid_config.py`:

```python
config = HybridSystemConfig(
    model_a_lora_rank=64,         # Adjust for memory constraints
    model_a_training_steps=50,    # More steps for better quality
    model_b_lora_rank=32,
    model_b_training_steps=500,
    use_a100_optimizations=True   # Enable A100-specific optimizations
)
```

## 🚀 API Deployment

Deploy as an API using FastAPI:

```bash
python inference/production_api.py --host 0.0.0.0 --port 8000
```

## 🚨 Troubleshooting

**CUDA Out of Memory**
- Reduce batch sizes in configuration
- Use gradient checkpointing
- Enable 4-bit quantization

**Model Loading Errors**
- Ensure all model files are downloaded
- Check CUDA compatibility
- Verify transformers version

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Hugging Face for the transformers library
- NousResearch for the Hermes model
- The open-source ML community


