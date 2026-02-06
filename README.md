# Agentic Chat Application

A synergistic conversational agent built with **LangGraph** and **FastAPI**, designed to answer queries about SynergisticIT training programs and general topics with robust guardrails, intelligent routing, and caching.

## Key Features

-   **Agentic Workflow**: Uses LangGraph to orchestrate a sophisticated decision-making pipeline (Router -> Retriever -> Grader -> Generator).
-   **Smart Routing**: Classifies user intent (Financing, Placement, Curriculum, etc.) and targets specific knowledge bases.
-   **Query Rewriting**: Transforms vague user inputs (e.g., "cost?") into optimized search queries ("What is the tuition cost...?").
-   **Redis Caching**: Caches answers for identical questions to reduce latency and API costs.
    -   *Graceful Fallback*: Automatically disables caching if Redis is not available.
-   **Robust Guardrails**: Filters out toxic, irrelevant, or unsafe queries before they reach the LLM.
-   **Multi-Layered Knowledge Base**:
    -   Decision FAQ (Atomic Q&A)
    -   Policy Documents (Refunds, ISA)
    -   Program Details & Trust (Web Scraped Content)

## Project Structure

```
src/
├── api.py              # FastAPI server entry point
├── config.py           # Configuration & Environment Variables
├── ingest.py           # Knowledge Base Ingestion Script
├── graph/
│   ├── workflow.py     # LangGraph State Machine Definition
│   ├── state.py        # AgentState Type Definition
│   └── nodes/          # Concept-Specific Logic modules
│       ├── router.py
│       ├── retriever.py
│       ├── grader.py
│       ├── generator.py
│       ├── query_rewriter.py
│       └── input_guardrails.py
└── utils/
    └── cache.py        # Redis Cache Manager
```

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the project root:
    ```
    OPENAI_API_KEY=your_api_key_here
    REDIS_URL=redis://localhost:6379/0  # Optional (Defaults to localhost)
    ```

3.  **Infrastructure (Optional)**:
    -   To enable caching, start a Redis server (e.g., via Docker):
        ```bash
        docker run -p 6379:6379 -d redis
        ```

4.  **Ingest Knowledge Base**:
    (First run only)
    ```bash
    python src/ingest.py
    ```

## Usage

Start the API server:
```bash
python src/api.py
```
Or using uvicorn directly:
```bash
uvicorn src.api:app --reload
```

## API Endpoints

### `POST /chat`

Interact with the agent.

**Request Body**:
```json
{
  "question": "What courses do you offer?"
}
```

**Response**:
```json
{
  "answer": "SynergisticIT offers courses in Java, Python, Data Science, AWS, and more...",
  "relevance_score": "3/3"
}
```
