# Agentic Chat Application

A synergistic conversational agent built with LangGraph and FastAPI, designed to answer queries about SynergisticIT training programs and general topics with robust guardrails.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Ensure you have a `.env` file in the project root with your API keys:
    ```
    OPENAI_API_KEY=your_api_key_here
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
  "answer": "SynergisticIT offers courses in Java, Python, Data Science, AWS, and more..."
}
```
