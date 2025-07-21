# Full-Stack ML Engineering Portfolio

## Overview

This portfolio demonstrates expertise in machine learning engineering and full-stack development through three comprehensive projects: fine-tuning LLMs for structured evaluation, building production-ready web applications, and orchestrating parallel processing with LangGraph.

Each project showcases different aspects of modern ML engineering, from model training and deployment to user interface development and distributed computing patterns.

---

## Project 1 — CV Evaluation LLM

### Goal

Build a fine-tuned LLM that evaluates CVs against 10 criteria and returns structured JSON responses, demonstrating advanced ML model development and structured output generation.

### Tech Stack

| Component    | Version / Note          |
| ------------ | ----------------------- |
| PyTorch      | ≥ 2.0                   |
| Transformers | Hugging Face latest     |
| PEFT         | For LoRA implementation |
| TRL          | For GRPO training       |
| Python       | ≥ 3.9                   |

---

### Section 1A: Model Implementation

#### Requirements

1. **Base Model Selection**

   * Choose and justify an open-source LLM (e.g., Llama 2/3, Mistral, CodeLlama)
   * Explain your choice based on: size, performance, licensing, context length
   * Document expected hardware requirements

2. **Fine-tuning Strategy**

   * Implement LoRA (Low-Rank Adaptation) for efficient training
   * Use GRPO (Group Relative Policy Optimization) for alignment
   * Create training loop with proper validation splits

3. **CV Evaluation Criteria**
   Example:

   ```json
   {
     "technical_skills": 8,
     "experience_relevance": 7,
     "education_quality": 9,
     "leadership_potential": 6,
     "communication_skills": 8,
     "problem_solving": 7,
     "innovation_mindset": 8,
     "cultural_fit": 9,
     "career_progression": 7,
     "overall_impression": 8,
     "total_score": 77,
     "recommendation": "strong_hire",
     "key_strengths": ["Strong technical background", "Excellent education"],
     "areas_for_improvement": ["Limited leadership experience"],
     "processing_time_ms": 1247
   }
   ```

---

## Project 2 — Todo List Application (NestJS + React)

### Goal

Build a full-stack todo application that demonstrates your ability to create production-ready user interfaces and APIs.

### Tech Stack

| Component   | Version / Note                                  |
| ----------- | ----------------------------------------------- |
| React       | ≥ 18 with TypeScript                            |
| NestJS      | Latest with TypeScript                          |
| Material-UI | @mui/material                                   |
| Docker      | For containerization                            |
| Database    | Your choice (PostgreSQL, MongoDB, or in-memory) |

---

### Backend (NestJS)

1. **API Endpoints**

   * `GET    /todos`          — List all todos
   * `POST   /todos`          — Create new todo
   * `PUT    /todos/:id`      — Update todo
   * `DELETE /todos/:id`      — Delete todo
   * `GET    /todos/:id`      — Get single todo

2. **Todo Model**

   ```ts
   interface Todo {
     id: string;
     title: string;
     description?: string;
     completed: boolean;
     priority: 'low' | 'medium' | 'high';
     dueDate?: Date;
     createdAt: Date;
     updatedAt: Date;
   }
   ```

3. **Bonus Features (Not necessary)**

   * Input validation with class-validator
   * Proper error handling and HTTP status codes
   * Swagger/OpenAPI documentation

---

### Frontend (React + TypeScript)

1. **Core Features**

   * Add new todos
   * Edit todos inline
   * Mark todos as complete/incomplete
   * Delete todos with confirmation
   * Filter todos (all, active, completed)
   * Sort by priority, due date, or creation date

2. **UI Requirements**

   * Use Material-UI components consistently
   * Loading states and error handling

3. **State Management**

   * Use Redux
   * Use MVP design (Redux for state, MVP for view, redux-thunk as controllers)
   * Implement optimistic updates
   * Handle API loading and error states

---

### Infrastructure

1. **Docker Setup**

   * Multi-stage builds for production optimization
   * Docker Compose for easy local development
   * Environment variable configuration

2. **Data Persistence**

   * Choose between PostgreSQL, MongoDB, or in-memory storage
   * Implement proper database migrations (if applicable)
   * Seed data for testing

---

## Project 3 — LangGraph Map-Reduce

### Goal

Demonstrate orchestration of parallel processing workers with LangGraph, showcasing distributed computing patterns and workflow management.

### Scenario

Expose a Flask endpoint:

`POST /sum_of_squares {"length": 100}` → returns `{"sum_of_squares": 123456}`

---

### Graph Design

1. **Generator Node**

   * Produce a list of length random ints (0–99)

2. **Mapper Branch**

   * Square each number in parallel (must use Send API)

3. **Reducer Node**

   * Sum results and return JSON

> Reference tutorial:
> [Medium Tutorial on LangGraph Send API](https://medium.com/@astropomeai/implementing-map-reduce-with-langgraph-creating-flexible-branches-for-parallel-execution-b6dc44327c0e)



---

### Tech Stack

| Component | Version / Note      |
| --------- | ------------------- |
| Python    | ≥ 3.9               |
| LangGraph | Latest              |
| Flask     | Lightweight wrapper |

---

### Requirements

#### Core Implementation

1. **Generator Node**

   * Accept input parameter `length`
   * Generate list of random integers (0–99)
   * Pass list to mapper branches

2. **Mapper Branch**

   * Use LangGraph Send API for parallel execution
   * Each branch squares one number
   * Must demonstrate true parallelism

3. **Reducer Node**

   * Collect all squared results
   * Sum the values
   * Return formatted JSON response

4. **Flask Integration**

   * Single POST endpoint `/sum_of_squares`
   * Proper error handling for invalid input
   * JSON request/response format

#### Advanced Features

* Graceful handling of bad input/failures
* Logging of execution time and parallelism
* Clean separation of graph logic and Flask app

#### Quick Test

```bash
docker compose up --build

curl -X POST localhost:5000/sum_of_squares \
  -H "Content-Type: application/json" \
  -d '{"length": 10}'
```

---

## Repository Structure

```
project1-cv-evaluator/
project2-todo-app/
project3-langgraph-mapreduce/
README.md
```

