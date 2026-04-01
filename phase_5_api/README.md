# Phase 5: API Endpoints

This folder contains the FastAPI endpoints tying the whole Sense-Think-Verify loop together.

## Endpoints
- `POST /api/chat/intake`: Receives user stories, runs Gemini extraction (Sense), and returns the Confidence Score + context gaps.
- `POST /api/strategies`: Accepts the context and runs Vector DB Query (Think) to return cards.
- `POST /api/generate-note`: Generates a fully personalized "Why" note using Gemini.

## Testing
1. Install requirements: `pip install -r requirements.txt`
2. Run mock tests: `pytest`
3. Run server: `uvicorn main:app --reload`
