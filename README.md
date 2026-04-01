# Dearly AI Backend Development

Dearly is an AI-powered gifting assistant focused on "Relationship Intelligence". It helps users find the perfect gift by understanding the recipient's daily habits, annoyances, and specific giver preferences (like budget and utility vs WOW factor) to suggest deeply thoughtful strategies and products.

## Development Approach

This project is developed in isolated phase-wise development folders so that each phase can be tested independently. You can trace the progress of the backend through these separate modules:

- **`phase_1_setup/`**: Initial Python FastAPI setup, configuration management, and basic testing structure.
- **`phase_2_database/`**: Supabase integration (Users, Recipients, Interactions tables).
- **`phase_3_sense_layer/`**: Gemini API integration to extract user preferences (budget, wow vs utility, frustrations).
- **`phase_4_rag/`**: Vector DB (Supabase pgvector) setup for storing strategies and matching concepts.
- **`phase_5_api/`**: Integration of the FastAPI endpoints (`/chat/intake`, `/strategies`, `/generate-note`).
- **`phase_6_testing/`**: Final end-to-end refinement.

## Tech Stack
- **Backend Framework**: Python (FastAPI)
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI**: Google Gemini API

## Getting Started
Navigate to any phase folder and check its individual `README.md` for run instructions and test cases. Each phase acts as an independent building block.
