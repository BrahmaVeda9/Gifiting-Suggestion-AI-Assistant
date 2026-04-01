# Phase 3: Gemini API Integration (Sense Layer)

This folder contains the logic to run the MVP's "Sense Mode". It uses Google Gemini to read user inputs and extract structured attributes like budget, relationship context, frustrations, and the preference between "wow vs. utility".

## Overview
- `ai_client.py`: Calls Gemini to extract the required JSON structure.
- `schemas.py`: Pydantic schemas for expected models.
- `logic.py`: Confidence score calculation and clarification prompting based on missing data.
- `tests/`: Logic testing with pytest.

## Testing
1. Install requirements: `pip install -r requirements.txt`
2. Run tests: `pytest`
