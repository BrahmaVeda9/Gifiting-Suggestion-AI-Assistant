# Phase 1: Project Setup

This folder contains the foundation of the Dearly Backend using FastAPI.

## How to run
1. Ensure you have Python installed.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Run server: `uvicorn main:app --reload`
6. Check health: Open browser to `http://localhost:8000/health`

## How to test
1. Run `pytest` command in the `phase_1_setup` directory.
