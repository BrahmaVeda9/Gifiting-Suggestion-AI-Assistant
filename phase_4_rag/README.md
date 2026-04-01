# Phase 4: RAG Implementation

This folder handles generating embeddings for the "Think" layer of the MVP and using Supabase pgvector to search for the best strategy cards.

## Setup
1. Run `setup_pgvector.sql` in your Supabase SQL Editor.
2. Insert sample strategies manually with embeddings to test it out (this could be seeded later).

## Testing
1. Install requirements: `pip install -r requirements.txt`
2. Run mock tests: `pytest`
