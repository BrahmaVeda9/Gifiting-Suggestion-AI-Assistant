# Phase 6: Testing and Refinement

This folder contains the End-to-End integration test script to simulate the full user journey:
1. Sending the story to the API (Sense)
2. Getting the strategies from the API (Think)
3. Generating the "Why" note (Verify/Act)

## How to use
1. Make sure the Phase 5 FastAPI server is running (`uvicorn main:app --reload` from `phase_5_api` folder).
2. Install requirements: `pip install -r requirements.txt`
3. Execute `python e2e_test.py` to see the flow. You can uncomment the `httpx` logic inside to test against the real local server.
