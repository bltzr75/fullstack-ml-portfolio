# Project 3 - LangGraph Map-Reduce

A Flask application that implements a Map-Reduce pattern using LangGraph's Send API for parallel computation of sum of squares.

## Overview

This project demonstrates:
- **LangGraph Map-Reduce Pattern**: Using Send API for parallel execution
- **Generator → Parallel Mappers → Reducer**: Classic fan-out/fan-in architecture
- **Flask REST API**: Clean HTTP interface
- **Docker Deployment**: Containerized for easy deployment
- **LangGraph Studio**: Visual development and debugging environment

## Architecture

```
Input: {"length": N}
     ↓
Generator Node (creates N random numbers)
     ↓
Fan-out via Send API
     ↓
Mapper Nodes (N parallel executions: number → number²)
     ↓
Fan-in via state aggregation
     ↓
Reducer Node (sum all squares)
     ↓
Output: {"sum_of_squares": result}
```

## Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone and navigate to project
cd project3-langgraph-mapreduce

# Build and start container
docker compose up --build

# Test the API
curl -X POST localhost:5000/sum_of_squares \
  -H "Content-Type: application/json" \
  -d '{"length": 10}'
```

### Option 2: Local Development
```bash
# Install dependencies (requires Python 3.11+ for LangGraph Studio)
pip install -r requirements.txt

# Start Flask app
python app.py

# Test the API (in another terminal)
curl -X POST localhost:5000/sum_of_squares \
  -H "Content-Type: application/json" \
  -d '{"length": 10}'
```

### Option 3: LangGraph Studio (For Development & Recording)
```bash
# Requires Python 3.11+ and langgraph-cli[inmem]
pip install -U "langgraph-cli[inmem]"

# Start LangGraph development server
langgraph dev

# Access LangGraph Studio at provided URL:
# https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

## API Reference

### Endpoints

#### `POST /sum_of_squares`
Calculate sum of squares using LangGraph Map-Reduce pattern.

**Request:**
```json
{
  "length": 100
}
```

**Response:**
```json
{
  "sum_of_squares": 328350,
  "length": 100,
  "execution_time": 0.0234,
  "numbers_processed": 100,
  "api_response_time": 0.0267
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "LangGraph Map-Reduce API",
  "timestamp": 1752087666.127
}
```

#### `GET /sum_of_squares`
Get endpoint documentation.

## LangGraph Implementation Details

### Key Components

1. **Generator Node**: Creates random numbers (0-99)
2. **Send API**: Creates parallel mapper tasks
3. **Mapper Nodes**: Square individual numbers in parallel
4. **Reducer Node**: Aggregates and sums results

### Send API Pattern
```python
def continue_to_mappers(state: OverallState) -> List[Send]:
    """Fan-out using Send API"""
    return [Send("mapper", {"number": num}) for num in state['numbers']]

# Add to graph
graph.add_conditional_edges(
    "generator",
    continue_to_mappers,
    ["mapper"]
)
```

### State Management
```python
class OverallState(TypedDict):
    length: int
    numbers: List[int]
    squared_results: Annotated[List[int], operator.add]  # Auto-aggregation
    sum_of_squares: int
    execution_time: float
```

## LangGraph Studio Recording

### Setup for Visual Demonstration
1. **Start LangGraph Studio:**
   ```bash
   langgraph dev
   ```

2. **Access the web interface** at the provided URL

3. **Load the mapreduce graph** and set input:
   ```json
   {"length": 5}
   ```

4. **Record the execution** showing:
   - Graph structure visualization
   - Send API fan-out pattern
   - Parallel mapper execution
   - State aggregation and reduction

### Recording Checklist
- ✅ Show graph structure (Generator → Send → Mappers → Reducer)
- ✅ Demonstrate parallel execution of mappers
- ✅ Highlight the Send API pattern
- ✅ Show state aggregation in action
- ✅ Display final results

## Docker Commands

```bash
# Build and start
docker compose up --build

# Start in background
docker compose up -d

# View logs
docker compose logs -f

# Stop containers
docker compose down

# Rebuild everything
docker compose up --build --force-recreate
```

## Examples

### Small Dataset
```bash
curl -X POST localhost:5000/sum_of_squares \
  -H "Content-Type: application/json" \
  -d '{"length": 5}'

# Response: {"sum_of_squares": 12345, "length": 5, ...}
```

### Large Dataset
```bash
curl -X POST localhost:5000/sum_of_squares \
  -H "Content-Type: application/json" \
  -d '{"length": 1000}'

# Response: {"sum_of_squares": 3328467, "length": 1000, ...}
```

### Error Handling
```bash
# Invalid input
curl -X POST localhost:5000/sum_of_squares \
  -H "Content-Type: application/json" \
  -d '{"length": -5}'

# Response: {"error": "Field 'length' must be a positive integer"}
```

## Project Structure

```
project3-langgraph-mapreduce/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container definition
├── docker-compose.yml     # Docker orchestration
├── langgraph.json         # LangGraph Studio configuration
├── .env                   # Environment variables
├── app.py                 # Flask REST API
└── langgraph_mapreduce.py # Core LangGraph implementation
```

## Key Features

- ✅ **LangGraph Send API**: Proper parallel execution pattern
- ✅ **Map-Reduce Architecture**: Generator → Parallel Mappers → Reducer
- ✅ **REST API**: Clean HTTP interface with error handling
- ✅ **Docker Ready**: One-command deployment
- ✅ **LangGraph Studio**: Visual development and debugging
- ✅ **Input Validation**: Handles edge cases and invalid inputs
- ✅ **Performance Logging**: Execution time tracking
- ✅ **Health Checks**: Built-in monitoring endpoints

## Technical Notes

- **Parallelism**: Uses LangGraph's Send API for true parallel execution
- **State Aggregation**: Automatic result collection via `operator.add`
- **Error Handling**: Comprehensive validation and error responses
- **Performance**: Optimized for datasets up to 10,000 elements
- **Security**: Non-root user in Docker container
- **Studio Integration**: Graph visualization and interactive debugging

## Requirements

### Core Requirements
- Python ≥ 3.9 (for basic functionality)
- LangGraph (latest)
- Flask ≥ 2.3.0
- Docker & Docker Compose (for containerized deployment)

### LangGraph Studio Requirements
- Python ≥ 3.11 (required for langgraph-cli[inmem])
- langgraph-cli[inmem] package
- LangSmith account (free)

### Setup for Different Python Versions
```bash
# For Python 3.11+ (LangGraph Studio support)
python3.11 -m venv venv_project3_py311
source venv_project3_py311/bin/activate
pip install -r requirements.txt
pip install -U "langgraph-cli[inmem]"

# For Python 3.9-3.10 (basic functionality only)
python3 -m venv venv_project3
source venv_project3/bin/activate
pip install -r requirements.txt
```

## Development Status

- [x] Phase 1: Environment setup
- [x] Phase 2: LangGraph Send API implementation
- [x] Phase 3: Flask integration
- [x] Phase 4: Docker deployment
- [x] Phase 5: Documentation
- [x] LangGraph Studio setup
- [ ] LangGraph Studio recording (60-90 seconds)

## Testing

### Quick Tests
```bash
# Test core functionality
python langgraph_mapreduce.py

# Test Flask API
curl -X POST localhost:5000/sum_of_squares \
  -H "Content-Type: application/json" \
  -d '{"length": 10}'

# Test Docker deployment
docker compose up --build -d
curl -X POST localhost:5000/sum_of_squares \
  -H "Content-Type: application/json" \
  -d '{"length": 10}'
docker compose down
```

### LangGraph Studio Test
```bash
# Start development server
langgraph dev

# Access web interface and test with input: {"length": 5}
```

---

*Built for demonstrating LangGraph Map-Reduce patterns with parallel execution using the Send API.*
